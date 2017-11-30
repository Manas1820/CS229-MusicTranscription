import numpy as np
from util import read_melody
from pitch_contour import trainTransition

# load training annotations
annotations_train = '/root/MedleyDB_selected/Annotations/Melody_Annotations/MELODY1/train/'

melodies = []
print ("Loading training data ...")
for filename in os.listdir(annotations_dir):
    if filename.endswith(".csv"):
        audioName = filename[:filename.find('MELODY')-1] # remove the trailing '_MELODY1.csv'
        new_bin_melody, _ = read_melody(audioName, annotations_dir)
        melodies.append(new_bin_melody)
        print ("Loaded annotations for %s") % audioName

bins = range(109)

print ("Finished loading data")

# Maximum Likelihood estimates
# store in outputFile
outputFile = 'transitions_mle'
print ("Training transitions ...")
trainTransition(data, bins, outputFile, alpha=1)

print("Done.")
print("Verifying transitions ...")
# Verify soundness of transition estimates
transitions = np.load(outputFile).item()
    for i in range(109):
        count = 0
        for j in range(109):
            count += probabilities[(i,j)]
        self.assertEqual(int(round(count)), 1)

print ("Done. Transitions were saved in %s") % outputFile
