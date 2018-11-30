import numpy as np
from typing import List

class Gate(object):
    """docstring for Gate"""
    def __init__(self):
        super(Gate, self).__init__()
        self.matrix = np.array([])

    def getMatrix(self):
        return self.matrix
        