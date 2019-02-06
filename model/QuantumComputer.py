from copy import copy

import functools


class Register:

    def __init__(self, nqbits, value = 0):
        self.value = value
        self.nqubits = nqbits
        self.qbits = self.valueToBits(self.value)

    def valueToBits(self, value):
        bin_truncated = list(map(lambda x: int(x), bin(value)[2:]))
        return [0 for i in range(self.nqubits - bin_truncated.__len__())] + bin_truncated

    def bitListToStringValue(self, bitList):
        return "".join(map(lambda x: str(x), bitList))

    def bitlistToDecimal(self, bitList):
        decimal = 0
        multiplier = 1
        for i in range(len(bitList) - 1, -1, -1):
            decimal += bitList[i] * multiplier
            multiplier *= 2
        return decimal

    def swapBitAt(self, i):
        b = self.qbits[i]
        self.qbits[i] = 1 if b == 0 else 0
        self.value = self.bitlistToDecimal(self.qbits)

    def updateRegisterWith(self, newValue, newBitlist):
        self.value = newValue
        self.qbits = newBitlist

class QuantumComputer:

    def __init__(self, nqbits):
        self.register = Register(nqbits=nqbits)
        self.grid = {} # dict of dicts, {i: {j : gateName}}

    def addGate(self, i, j, name):
        if not self.grid.__contains__(i):
            self.grid[i] = {}
        self.grid[i][j] = name

    def removeGate(self, i, j):
            self.grid[i].__delitem__(j)

    def qbitValueAt(self, i):
        return self.register.qbits[i]

    def swapQbitValueAt(self, i):
        self.register.swapBitAt(i)

    def removeQbit(self, i):
        if self.grid.__contains__(i):
            self.grid.__delitem__(i)
        self.shiftGrid(i)
        self.register = self.registerWithRemovedQbit(i)

    def addQbit(self):
        self.register = self.registerWithAddedQbit()

    def shiftGrid(self, i):
        indecies_bigger_than_i = list(filter(lambda x: x>i, self.grid.keys()))
        indecies_lower_than_i = list(filter(lambda x: x<i, self.grid.keys()))
        values_of_bigger_indicies = { x: self.grid[x] for x in indecies_bigger_than_i }
        values_of_lower_indicies = {x: self.grid[x] for x in indecies_lower_than_i }
        self.grid = {x: values_of_lower_indicies[x] for x in indecies_lower_than_i}
        self.grid.update({x-1: values_of_bigger_indicies[x] for x in indecies_bigger_than_i})

    def registerWithRemovedQbit(self, i):
        v = self.register.value
        bitsList = self.register.valueToBits(v)
        bitlist_with_removed_qbit = bitsList[:i] + bitsList[i + 1:]
        return Register(
            nqbits = self.register.nqubits - 1,
            value = self.register.bitlistToDecimal(bitlist_with_removed_qbit)
        )

    def registerWithAddedQbit(self):
        v = self.register.value
        bitsList = self.register.valueToBits(v)
        bitlist_with_added_qbit = bitsList + [0]
        return Register(
            nqbits = self.register.nqubits + 1,
            value = self.register.bitlistToDecimal(bitlist_with_added_qbit)
        )

    def update_dict(self, a, b):
        dest = dict(a)
        dest.update(b)
        return dest

    def flattenedGrid(self): #returns a one-dimensional copy of the grid instead of the original two dimensional structure
        list_of_dicts = [{(y[0], j): name for (j, name) in y[1].items()} for y in self.grid.items()]
        return dict(functools.reduce(lambda acc, d: self.update_dict(acc, d), list_of_dicts, {}))

    def nextStep(self):
        pass

    def fastForward(self):
        pass

    def breakSimulation(self):
        pass

