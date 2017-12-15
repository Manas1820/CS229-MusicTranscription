
import numpy as np
from pitch_contour import PitchContour
from PitchEstimationDataSet import PitchEstimationDataSet
from fragmenter_hmm_solver import fragmented_solver
from config import *
import sys
from time import time

debug = False
K=5
b_prob = np.zeros((1,K))
w_prob = np.zeros((1,K))

confirm_prob = np.zeros((1, K)) # Cases where HMM confirms positive result from CNN
fix_prob = np.zeros((1, K)) # Cases where HMM finds positive result when CNN didn't
break_prob = np.zeros((1, K)) # Cases where HMM ignores CNN result and is mistaken

def getNumberOfHits(ground_truth, prediction, N, probs, cnn_prediction = None):
    global b_prob
    global w_prob
    global confirm_prob, fix_prob, break_prob
    numCorrect = 0
    numCNNCorrect = 0
    numConfirm = 0 
    numFix = 0
    numBreak = 0
    for i in range(N):
          if ground_truth[i] == prediction[i]:
            b_prob = np.append(b_prob, probs[i,:].reshape((1,K)), axis = 0)
            numCorrect +=1
          else:
            w_prob = np.append(w_prob, probs[i,:].reshape((1,K)), axis = 0)
          if cnn_prediction is not None:
            if cnn_prediction[i] == ground_truth[i]:
              numCNNCorrect += 1
            if ground_truth[i] == prediction[i] and prediction[i] == cnn_prediction[i]:
              numConfirm +=1
              confirm_prob = np.append(confirm_prob, probs[i, :].reshape((1,K)), axis=0)
            elif ground_truth[i] == prediction[i] and prediction[i] != cnn_prediction[i]:
              numFix +=1
              fix_prob = np.append(fix_prob, probs[i, :].reshape((1,K)), axis=0)
            elif ground_truth[i] != prediction[i] and cnn_prediction[i] == ground_truth[i]:
              numBreak +=1
              break_prob = np.append(break_prob, probs[i, :].reshape((1,K)), axis=0)
    print (numCorrect, numCNNCorrect, numConfirm, numFix, numBreak)
    return numCorrect, numCNNCorrect, numConfirm, numFix, numBreak

configuration = config_cqt()
# val_set = PitchEstimationDataSet(configuration['annot_folder']+'val/', configuration['image_folder']+'val/', sr_ratio=configuration['sr_ratio'])
annotations_val = '/root/MedleyDB_selected/Annotations/Melody_Annotations/MELODY1/val/'
val_set = PitchEstimationDataSet(annotations_val, '/root/data/val', sr_ratio=1, audio_type="MIX")

# Load CNN results from validation set
filepath = "dataset/val_result_mtrx.npy"
validation_inference = np.load(filepath)

# Load trained Maximum Likelihood Estimates
trained_mle = "dataset/transitions_mle.npy" # Path to saves parameters for HMM
transitions = np.load(trained_mle).item()

# Run inference on each song
hmmTotalAccuracy = {}
# rangeM = [20, 50, 100, 200, 300, 500, 1000]
# for M in [50, 100, 200, 300, 400, 500]:
#rangeM = [0.5, 0.2, 0.1, 0.01, 0.001]
rangeM = [300]
# rangeT=[0.60, 0.65, 0.66, 0.67, 0.68, 0.69, 0.7]
# rangeT = [0.65, 0.8, 0.9, 1.0]
rangeT = [1]
ranges = [(m, t) for m in rangeM for t in rangeT]
for (M, threshold) in ranges:
  start = time()
  totalAccuracy = 0
  cnnOnlyAccuracy = 0
  totalFix = 0
  totalBreak = 0
  totalConfirm = 0
  offset = 0

  for songID in range(len(val_set.songNames)):
      songName = val_set.songNames[songID]
      print ("Evaluating for " + songName)
      N = val_set.songLengths[songID]
      probabilities = np.zeros((N, K))
      bins = np.zeros((N,K))
      print ("Loading for %d notes" % N)
      for i in range(N):
          probabilities[i] = validation_inference[i + offset][:K][:,0]
          probabilities[i] /= np.sum(probabilities[i])
          bins[i] = validation_inference[i + offset][:K][:,1]
      offset += N
      chunksizes = max(0, int(M * N))
      solution = fragmented_solver(N, K, chunksizes, probabilities, bins, transitions, threshold)
      currentAccuracy, currentCnnOnlyAccuracy, confirmAcc, fixAcc, breakAcc \
          = getNumberOfHits(val_set.pitches[songID], solution, N, probabilities, bins[:, 0])
      # currentCnnOnlyAccuracy, _ = getNumberOfHits(val_set.pitches[songID], bins[:, 0], N)
      cnnOnlyAccuracy += currentCnnOnlyAccuracy
      totalAccuracy += currentAccuracy
      totalFix += fixAcc
      totalConfirm += confirmAcc
      totalBreak += breakAcc
      print(M, threshold)
      print ("With HMM: Accuracy rate on this song %f " % (totalAccuracy/N))
      print ("Without HMM accuracy %f" % (cnnOnlyAccuracy/N))
      print ("HMM v. CNN stats confirm %f, fix %f, break %f" % (totalConfirm/N, totalFix/N, totalBreak/N))
#      np.save("good_prob_hmm_refined"+str(threshold), b_prob)
      # np.save("good_bin_hmm", b_bin)
      np.save("confirm_prob_hmm"+str(threshold), confirm_prob)
      np.save("break_prob_hmm"+str(threshold), break_prob)
      np.save("fix_prob_hmm"+str(threshold), fix_prob)
      b_prob = np.zeros((1,K))
      w_prob = np.zeros((1,K))
      confirm_prob = np.zeros((1,K))
      break_prob = np.zeros((1,K))
      fix_prob = np.zeros((1,K))
      sys.stdout.flush()
  print ('M %f' % M)
  print ('Using {:f} seconds'.format(time()-start))
  hmmTotalAccuracy[(M, threshold)] = (totalAccuracy/val_set.lengths[-1])



print (hmmTotalAccuracy)
# print ("With HMM: Total accuracy rate")
# print (totalAccuracy/val_set.lengths[-1])
print ("Without HMM: Total accuracy rate")
print (cnnOnlyAccuracy/val_set.lengths[-1])

# np.save("bad_bin_hmm", w_bin)
