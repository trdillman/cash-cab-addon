from random import normalvariate, randrange
from builtins import property


class RandomNormal:
    
    def __init__(self, mean, sigmaRatio=0.05, numValues=100):
        self.numValues = numValues
        sigma = abs(sigmaRatio*mean)
        self.values = tuple(normalvariate(mean, sigma) for _ in range(numValues))
        # the current index
        self.index = -1
    
    @property
    def value(self):
        self.index += 1
        if self.index == self.numValues:
            self.index = 0

        return self.values[self.index]


class RandomWeighted:
    
    # the number of random indices for <self.distrList>
    numIndices = 1000

    def __init__(self, distribution):
        """
        Args:
            distribution (tuple): A tuple of tuples (value, its relative weight between integer 1 and 100)
        """
        self.singleValue = None
        distrList = []
        
        if len(distribution) == 1:
            self.singleValue = distribution[0][0]
        else: 
            for n,w in distribution:
                distrList.extend(n for _ in range(w))
            self.distrList = distrList
            lenDistrList = len(distrList)
            self.indices = tuple(randrange(lenDistrList) for _ in range(self.numIndices))
            # the current index in <self.indices> which in turn points to <self.distrList>
            self.index = -1
    
    @property
    def value(self):
        if self.singleValue is None:
            self.index += 1
            if self.index == self.numIndices:
                self.index = 0
            return self.distrList[ self.indices[self.index] ]
        else:
            return self.singleValue