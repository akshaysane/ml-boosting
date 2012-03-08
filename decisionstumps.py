# stdlib
import math
import random
import itertools as it
# local
import progress as pg


'''
A Decision stump is a tuple of:
-- feature index: integer index of the feature this stump looks at
-- threshold: float value above which this stump classifies positively
-- mistakes: list of integer indexes of datapoints this stump misclassifies
'''


###############################################################################


class StumpLibrary(object):

    # instance

    def __init__(self, dataset):
        self.sv = self.__class__.from_dataset(dataset)

    def pick_best(self, weights, foo=None):
        '''Return, without replacement, the least random stump in the library.
        Least random refers to the one with error farthest from one-half.
        Calculate error weighting datapoints according to the given list.
        '''
        def optimality(s):
            '''Return the randomness and weighted error of the given stump.'''
            err = Stump.error(s, weights)
            return [abs(0.5 - err), err]
        dist, err, i = max(optimality(s) + [i] \
                           for i, s in it.imap(None, it.count(), self.sv))      # O(n* n * m)
        print err,
        return (self.sv.pop(i), dist) if foo else self.sv.pop(i)

    def pick_random(self, weights):
        '''Return, without replacement, some random stump.'''
        i = random.choice(xrange(len(self.sv)))
        print Stump.error(self.sv[i], weights),
        return self.sv.pop(i)

    # class

    @classmethod
    def from_dataset(cls, dataset):
        stumps = []
        print 'Making distinct stumps and caching mistakes.'
        maxstumps = len(dataset[0].features) * (len(dataset) - 1 + 2)
        with pg.Progress(maxstumps, 2, pg.bar('Stumps', 32)) as p:
            # generate pairs of (index, feature vector)
            for i, fv in enumerate(it.izip(*(dp.features for dp in dataset))):
                for t in cls.thresholds(fv):
                    s = i, t, Stump.mistakes((i, t, []), dataset)
                    stumps.append(s)
                    p.next()
        return stumps

    # static

    @staticmethod
    def thresholds(fv):
        '''Calculate threshold values from a list of feature values.'''
        fv = list(set(fv)) # remove duplicates
        fv.sort()
        # create thresholds between adjacent pairs
        tv = [(a + b) / 2.0 for a, b in it.imap(None, fv, fv[1:])]
        return [fv[0] - 1] + tv + [fv[-1] + 1]


###############################################################################


class Stump(object):

    # instance

    def __init__(self):
        raise NotImplementedError

    # class

    @classmethod
    def mistakes(cls, stump, dataset):
        '''Return datapoint indexes on which the given stump makes mistakes.'''
        return [i for i, dp in it.imap(None, it.count(), dataset) \
                if cls.query(stump, dp) != dp.label]

    # static

    @staticmethod
    def query(stump, dp):
        '''How does the given stump to classify a datapoint?'''
        i, t, _ = stump
        return 1 if dp.features[i] > t else -1

    @staticmethod
    def error(stump, weights):
        '''Calculate the weighted error of the given stump.'''
        _, _, mistakes = stump
        return math.fsum(weights[m] for m in mistakes)


###############################################################################
