# stdlib
import datetime
import sys
import math
import random
import itertools as it
# local
import args
import spambase
from decisionstumps import StumpLibrary, Stump
from boosting import Boosting
import resultset


random.seed(int('f06', 16))


'''
python homework04.py
    [--folds NUM] [--testfold NUM]
    [--rounds NUM]
    [--beststump]

Load the spambase dataset, and fold it into 10 folds or [--folds NUM]. Test on
fold zero and train on the rest or test on [--testfold NUM].

Train by creating decision stumps for datapoints in the training set. Cache the
datapoint indexes for each decision stump which that decision stump incorrectly
classifies.

Boost decision stumps until training error converges, or for [--rounds NUM].
Boost a randomly chosen decision stump or the optimal one if [--beststump] is
given.

A dataset is a list of data points. Each data point has a list of features
values and a label. A feature vector is the list of all values a particular
feature takes on accross the dataset.
'''


def mistakect(dataset, fn):
    '''Map classifier function onto dataset. Count incorrect predictions.'''
    return sum(1 for dp in dataset if fn(dp) != dp.label)


PERSISTENCE = 3
MINDIFF = 0.001
def checkconverged(err):
    '''Return true unless error seems to have converged.

    Convergence occurs when error fails to decrease by at least MINDIFFERENCE for
    PERSISTENCE rounds in a row.

    Use it to check stopping conditions.
    Doesn't reset unless memoization is partially deleted.

    '''
    try:
        preverr = checkconverged.preverr
        checkconverged.preverr = err
        if preverr - err >= MINDIFF:
            checkconverged.ct = 0
        else:
            checkconverged.ct += 1
        return checkconverged.ct < PERSISTENCE
    except AttributeError:
        checkconverged.preverr = err
        checkconverged.ct = 0
        return True


def countdown(n=0):
    '''Return true n times.

    Use it to check stopping conditions.
    Doesn't reset unles memoization is deleted.

    '''
    try:
        countdown.value -= 1
        return countdown.value > 0
    except AttributeError:
        countdown.value = n
        return True


if __name__ == '__main__':
    opt = args.parse([('folds', 10, int),
                      ('testfold', 0, int),
                      ('rounds', None, int),
                      ('beststump', False, None)], sys.argv)
    print
    print 'Boosting {} decision stumps {}.'.format(
        'optimal' if opt['beststump'] else 'random',
        'until convergence' if opt['rounds'] is None else 'for {} rounds'.format(opt['rounds']))
    if opt['rounds'] is None:
        print 'Convergence occurs when test error fails to decrease by {} for {} rounds in a row.'.format(MINDIFF, PERSISTENCE)
    print 'Using spambase data folded {} ways. Testing on fold {}.'.format(
        opt['folds'], opt['testfold'])

    # stopping conditions
    if opt['rounds'] is None:
        def doround(err, rndct):
            return checkconverged(err)
    else:
        def doround(err, rndct):
            return countdown(rndct)

    # load from file
    spambase.load()

    # roll into folds
    folds = [[] for i in xrange(opt['folds'])]
    k = 0 # kurrent fold
    for dp in spambase.data:
        # change the 0,1 labels to -1,1
        dp.label = 1 if dp.label else -1
        # add to the current fold & switch to the next fold
        folds[k].append(dp)
        k = (k + 1) % opt['folds']

    # unroll to testing & training
    testing = folds.pop(opt['testfold'])
    training = reduce(lambda acc, cur: acc + cur, folds)
    del folds

    print 'Testing count:', len(testing)
    print 'Training count:', len(training)
    print 'Feature count:', len(training[0].features)

    # make stumps
    sv = StumpLibrary(training)
    svpick = sv.pick_best if opt['beststump'] else sv.pick_random

    # initialize boosting and weights
    boost = Boosting(training)
    wv = boost.init()
    H = boost.classify

    # do rounds
    roundct = 0
    testerr = 1
    start = datetime.datetime.now()
    print 'Round LocalError Feature TrainingError TestingError TestingAUC'
    while doround(testerr, opt['rounds']):
        roundct += 1
        print roundct,
        #
        # pick a stump
        stump = svpick(wv)
        print stump[0],
        #
        # curry the stump to a classifier function [dp --> -1 or 1]
        curried = (lambda s: lambda dp: Stump.query(s, dp))(stump)
        #
        # boost new datapoint weights
        wv = boost.round(curried)
        #
        # output status
        print mistakect(training, H) / float(len(training)),
        testerr = mistakect( testing, H) / float(len( testing))
        print testerr,
        #
        # calculate auc
        rv = [resultset.DataResult(int(dp.label > 0), boost.model(dp)) for dp in testing]
        print resultset.auc(resultset.rocdata(rv)),
        #
        # done
        print
    print 'Boosting time:', str(datetime.datetime.now() - start)
    rocfn = 'boostROC-{}.log'.format(datetime.datetime.now()).replace(':', '-')
    print 'Writing ROC data to "{}"'.format(rocfn)
    with open(rocfn, mode='wb') as fd:
        for fpr, tpr in resultset.rocdata(rv):
            fd.write('{} {}\n'.format(fpr, tpr))
    
    #raw_input('[Press Enter to Quit]')

###############################################################################
