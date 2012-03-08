# stdlib
import math
import itertools as it
import decisionstumps

class Boosting(object):

    def __init__(self, dataset):
        self.data = dataset
        self.weights = len(dataset) * [1.0 / len(dataset)]
        self._fn = []
        self._loop = self.__loop()

    @property
    def weighted_data(self):
        '''Yield weights paired with datapoints.'''
        return it.imap(None, self.weights, self.data)

    def init(self):
        '''Return the initial weight vector.'''
        return self._loop.next()

    def round(self, c):
        '''Take a classifier and return an updated weight vector.'''
        return self._loop.send(c)

    def __loop(self):
        while True:
            #
            # yield current weights, get a local classifier
            classify = yield self.weights[:]                                    # O(n)
            #
            # calculate local classifier error and confidence
            error = math.fsum(w for w, dp in self.weighted_data \
                              if classify(dp) != dp.label)                      # O(n)
            assert 0 <= error <= 1
            conf = 0.5 * math.log((1 - error) / error)
            #
            # calculate new datapoint weights and normalize them
            self.weights = [w * math.e ** (-conf * classify(dp) * dp.label) \
                            for w, dp in self.weighted_data]                    # O(n)
            z = math.fsum(self.weights)                                         # O(n)
            self.weights = [w / z for w in self.weights]                        # O(n)
            #
            # curry the local classifier up with its confidence
            curried = (lambda cls, c: lambda dp: cls(dp) * c)(classify, conf)
            self._fn.append(curried)

    def model(self, dp):
        return math.fsum(fn(dp) for fn in self._fn)                             # O(n)

    def classify(self, dp):
        return 1 if self.model(dp) > 0 else -1                                  # O(n)
