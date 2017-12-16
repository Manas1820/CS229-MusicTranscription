'''
Future work: Multiple pitches at a time
( Currently the training results are not satisfactory. )
'''

# utils
from __future__ import print_function
import argparse
from time import time
import os # for mkdir
import sys # for flushing stdout
# torch related
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.autograd import Variable
from torch.utils.data import DataLoader
from collections import Counter
# our code
from PitchEstimationDataSet import *
from model.model_multi import *
from util_cnn import *
from config import *

# Training settings
parser = argparse.ArgumentParser(description='PyTorch MNIST Example')
parser.add_argument('--mode', type=str,
                    help='Running mode: train / test')
# NOTE: please specify pretrained model in config.py
parser.add_argument('--batch-size', type=int, default=32, metavar='N',
                    help='input batch size for training (default: 32)')
parser.add_argument('--test-batch-size', type=int, default=1, metavar='N',
                    help='input batch size for testing (default: 32)')
parser.add_argument('--epochs', type=int, default=60, metavar='N',
                    help='number of epochs to train (default: 10)')
parser.add_argument('--lr', type=float, default=0.001, metavar='LR',
                    help='learning rate (default: 0.001)')
parser.add_argument('--lr-interval', type=int, default=5000, metavar='LR',
                    help='decrease lr if avg err of a lr-interval plateaus (default: 5000)')
parser.add_argument('--update_momentum', type=bool, default=True, metavar='M',
                    help='whether to update SGD momentum')
parser.add_argument('--momentum', type=float, default=0.9, metavar='M',
                    help='SGD momentum (default: 0.9)')
parser.add_argument('--no-cuda', action='store_true', default=False,
                    help='disables CUDA training')
parser.add_argument('--seed', type=int, default=1, metavar='S',
                    help='random seed (default: 1)')
parser.add_argument('--log-interval', type=int, default=10, metavar='N',
                    help='how many batches to wait before logging training status')
parser.add_argument('--save-interval', type=int, default=5000, metavar='N',
                    help='how many batches to wait before saving the trained model')
# NOTE: save_dir and save_prefix are moved to config.py

args = parser.parse_args()
args.cuda = not args.no_cuda and torch.cuda.is_available()

torch.manual_seed(args.seed)
if args.cuda:
    torch.cuda.manual_seed(args.seed)


kwargs = {'num_workers': 1, 'pin_memory': True} if args.cuda else {}
# Configuration
cfg = config_mixed() # NOTE: change this if you want to use different configuration
# Fields in cfg:
#   annot_folder: where the annotations are
#   image_folder: where the spectrograms are
#   audio_type: 'RAW' or 'MIX'
#   multiple: whether to use multiple pitches at a time; if True, then the input/target will be vectors.
#   save_dir: where the trained models are saved
#   save_prefix: prefix of the file name of the saved model ('.pt' files)
#   use_pretrained: whether or not to use a pretrained model
#   pretrained_path: path to the pretrained model

if True:
    # train
    training_set = PitchEstimationDataSet(cfg['annot_folder']+'train/', cfg['image_folder']+'train/', sr_ratio=6, audio_type=cfg['audio_type'], multiple=cfg['multiple'])
    train_loader = DataLoader(training_set, batch_size=args.batch_size, shuffle=True, **kwargs)

if False:
    # val
    val_set = PitchEstimationDataSet(cfg['annot_folder']+'val/', cfg['image_folder']+'val/', sr_ratio=6, audio_type=cfg['audio_type'], multiple=cfg['multiple'])
    val_loader = DataLoader(val_set, batch_size=1, shuffle=False, **kwargs)

if False:
    # test
    test_set = PitchEstimationDataSet(cfg['annot_folder']+'test/', cfg['image_folder']+'test/', sr_ratio=6, audio_type=cfg['audio_type'], multiple=cfg['multiple'])
    test_loader = DataLoader(val_set, batch_size=1, shuffle=False, **kwargs)


def train(model, train_loader, criterion, epoch):
    model.train()
    batch_start = time()
    avg_loss, prev_avg_loss = 0, 1000
    for batch_idx, dictionary in enumerate(train_loader):
        data = dictionary['image']
        target = dictionary['frequency']
        data, target = Variable(data).type(torch.FloatTensor), Variable(target).type(torch.FloatTensor)
        if args.cuda:
            data, target = data.cuda(), target.cuda()

        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()

        # training log
        if batch_idx % args.log_interval == 0:
            print('Train Epoch: epoch {} iter {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}\tTime per batch: {:.6f}s'.format(
                epoch, batch_idx, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.data[0],
                (time()-batch_start)/args.log_interval))
            batch_start = time()
            sys.stdout.flush()
        # save trained model
        if batch_idx % args.save_interval == 0:
            save_name = cfg['save_prefix'] + str(batch_idx) + '.pt'
            print('Saving model: ' + save_name)
            torch.save(model, cfg['save_dir']+save_name)


def validate(data_loader, model, criterion, outfile=None):
    out_mtrx = np.empty((len(data_loader), 108, 2))

    batch_time = AverageMeter()
    losses = AverageMeter()
    top1, top5 = AverageMeter(), AverageMeter()

    model.eval()

    for batch_idx, dictionary in enumerate(data_loader):
        batch_start = time()

        data, target = Variable(dictionary['image'], volatile=True).type(torch.FloatTensor), Variable(dictionary['frequency']).type(torch.FloatTensor)
        if args.cuda:
            data, target = data.cuda(), target.cuda()

        # compute output
        output = model(data)
        pos_prob = output.data * target.data
        neg_prob = output.data * (1-target.data)
        out_mtrx[batch_idx, :, 0] = pos_prob.view(-1).cpu().numpy()
        out_mtrx[batch_idx, :, 1] = neg_prob.view(-1).cpu().numpy()
        # performance measure: loss & top 1/5 accuracy
        """
        loss = criterion(output, target) # TODO: uncomment when training
        losses.update(loss.data[0], data.size(0)) # TODO: uncomment when training
        # Save probabilities & corresponding pitch bins
        probs, pitch_bins = torch.sort(output.data, 1, True) # params: data, axis, descending
        out_mtrx[batch_idx, :, 0] = probs.view(-1).cpu().numpy()
        out_mtrx[batch_idx, :, 1] = pitch_bins.view(-1).cpu().numpy()
        """

        batch_time.update(time() - batch_start)
        
        if batch_idx % (10*args.log_interval) == 0 and False:
            print('Val({:d}): '
                  'Loss: {:f} (avg: {:f})\t'
                  'Time: {:f}'.format(
                  batch_idx, losses.val, losses.avg, top1.val, top1.avg, top5.val, top5.avg, batch_time.avg))
            sys.stdout.flush()

    # overall average
    print('\n================\n'
          'Loss: {:f}\nPrec@1: {:f}\nPrec@5: {:f}'
          '\n================\n\n'.format(
          losses.avg, top1.avg, top5.avg))

    if outfile:
        np.save(outfile, out_mtrx)

    return top1.avg


if __name__ == '__main__':
    model = Net_Multi()
    if args.cuda:
        model.cuda()
    print_config(args, cfg)
    model.print_archi()

    optimizer = optim.SGD(model.parameters(), lr=args.lr, momentum=args.momentum)
    lr_update_interval = [5, 10, 40, 50]

    # input / target are vectors
    # use weight to help make up for unbalanced classes
    criterion = torch.nn.MultiLabelSoftMarginLoss()
    best_prec = 0
    if args.mode == 'train':
        if cfg['use_pretrained']:
            pretrained_dict = torch.load(cfg['pretrained_path'])['state_dict']
            model.load_state_dict(pretrained_dict)
            model.cuda()
        if not os.path.exists(cfg['save_dir']):
          os.mkdir(cfg['save_dir'])
        for epoch in range(args.epochs + 1):
            if epoch > 0:
                # use epoch=0 to check saving checkpoint
                print('\n\n###############\n'
                  '    Epoch {:d}'
                  '\n###############'.format(epoch))
        
                train(model, train_loader, criterion, epoch)
    
            # validation
            prec = validate(val_loader, model, criterion)
            is_best = prec > best_prec
            best_prec = max(prec, best_prec)
            save_checkpoint({
                'epoch': epoch,
                'state_dict': model.state_dict(),
                'best_prec': best_prec,
                'optimizer': optimizer.state_dict(),
            }, is_best, filename=cfg['save_dir']+cfg['save_prefix']+'_epoch{:d}.pt'.format(epoch))
    
            # update lr
            if epoch in lr_update_interval:
                args.lr /= 10
                for param_group in optimizer.param_groups:
                    print(param_group['lr'])
                    param_group['lr'] = args.lr
                print('Update lr to ' + str(args.lr))
            # update momentum
            if args.update_momentum and args.momentum < 0.9:
                args.momentum += 0.1
                for param_group in optimizer.param_groups:
                    print(param_group['momentum'])
                    param_group['momentum'] = args.momentum
                print('Update momentum to ' + str(args.momentum))
    else:
        # testing
        pretrained_dict = torch.load(cfg['pretrained_path'])['state_dict']
        model.load_state_dict(pretrained_dict)
        model.cuda()
        validate(val_loader, model, criterion)
