import numpy as np 


class FIFOBuffer(object):
    """
    A circular FIFO buffer implemented on top of numpy.
    """

    def __init__(self, size, dimensions=1, dtype=np.float32, filled=False):
        self._cache = np.zeros(size * dimensions, dtype)
        self._values = np.zeros(size * dimensions, dtype)
        self._size = size
        self._dimensions = dimensions
        self._array_size = size * dimensions
        if filled:
            self._ind = self._array_size
        else:
            self._ind = 0
        self._cached = False

    def add(self, *args):
        """
        Add a vector to the queue.
        """
        ind = self._ind % self._array_size
        self._values[ind:ind + self._dimensions] = args
        self._ind += self._dimensions
        self._cached = False

    def array(self):
        """
        Returns a numpy array containing the last stored values.
        """
        if self._ind < self._array_size:
            return self._values[:self._ind]
        if not self._cached:
            ind = self._ind % self._array_size
            self._cache[:self._array_size - ind] = self._values[ind:]
            self._cache[self._array_size - ind:] = self._values[:ind]
            self._cached = True
        return self._cache

    def __len__(self):
        if self._ind < self._array_size:
            return self._ind / self._dimensions
        return self._size
