import numpy as np 


class FIFOBuffer(object):
    """
    A circular FIFO buffer implemented on top of numpy.
    """

    def __init__(self, shape, dtype=np.float32, filled=False):
        self._cache = np.zeros(shape, dtype)
        self._values = np.zeros(shape, dtype)
        self.shape = shape
        if filled:
            self._ind = self.shape[0]
        else:
            self._ind = 0
        self._cached = False

    def add(self, value):
        """
        Add a value to the buffer.
        """
        ind = self._ind % self.shape[0]
        self._values[ind] = value
        self._ind += 1
        self._cached = False

    def array(self):
        """
        Returns a numpy array containing the last stored values.
        """
        if self._ind < self.shape[0]:
            return self._values[:self._ind]
        if not self._cached:
            ind = self._ind % self.shape[0]
            self._cache[:self.shape[0] - ind] = self._values[ind:]
            self._cache[self.shape[0] - ind:] = self._values[:ind]
            self._cached = True
        return self._cache

    def __len__(self):
        return min(self._ind, self.shape[0])
