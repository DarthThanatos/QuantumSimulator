from model.constants import X
from util.Utils import flatten_dicts

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
        self.grid = {}  # dict of dicts of single gates, {i: {j : gateName}}
        self.multiGates = {}
        # ^ dict of dicts { j: { (ctrl1, ctrl2 ...) -> (name, target) } }, where name is a simple target gate name,
        # whereas j is a column in the grid, and ctrl_i are indices of rows, and target is a row of simple gate

    def can_add_gate_at(self, i, j):
        if self.__overlaps_single_gate(i, j):
            return False
        if self.__overlaps_multi_gate(i, j):
            return False
        return True

    def __overlaps_single_gate(self,i, j):
        return self.grid.__contains__(i) and self.grid[i].__contains__(j)

    def __overlaps_multi_gate(self, i, j):
        if not self.multiGates.__contains__(j):
            return False
        for ctrl_i_tuple, (_, target_i) in self.multiGates[j].items():
            for ctrl_i in ctrl_i_tuple:
                if ctrl_i >= i >= target_i or target_i >= i >= ctrl_i:
                    return True
        return False

    def addGate(self, i, j, name):
        if not self.grid.__contains__(i):
            self.grid[i] = {}
        self.grid[i][j] = name

    def removeGate(self, i, j):
        self.grid[i].__delitem__(j)
        self.__remove_control_bits(i, j)

    def qbitValueAt(self, i):
        return self.register.qbits[i]

    def swapQbitValueAt(self, i):
        self.register.swapBitAt(i)

    def removeQbit(self, i):
        if self.grid.__contains__(i):
            self.grid.__delitem__(i)
        self.shiftGrid(i)
        self.register = self.registerWithRemovedQbit(i)
        self.multiGates = self.__multi_qbit_gates_after_qbit_removed(i)

    def __multi_qbit_gates_after_qbit_removed(self, i):
        new_multi_gates_dict = {}
        for j in self.multiGates:
            new_multi_gates_dict[j] = {}
            for ctrl_i_tuple, (name, target_i) in self.multiGates[j].items():
                if target_i != i:
                    new_ctrl_indexes_tuple = ()
                    for ctrl_i in ctrl_i_tuple:
                        if ctrl_i != i:
                            new_ctrl_indexes_tuple += (ctrl_i - 1 if ctrl_i > i else ctrl_i,)
                    if len(new_ctrl_indexes_tuple) > 0:
                        new_multi_gates_dict[j][new_ctrl_indexes_tuple] = (name, target_i - 1 if target_i > i else target_i)
        return new_multi_gates_dict

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

    def flattenedGrid(self):
        # returns a one-dimensional copy of the grid instead of the original two dimensional structure
        list_of_dicts = [{(y[0], j): name for (j, name) in y[1].items()} for y in self.grid.items()]
        return flatten_dicts(list_of_dicts)

    def flattenedMultiGates(self):
        # transforms { j: { (ctrl1, ctrl2 ...) -> (name, target) } }
        # to {(ctrl1, j1) -> (name_1, target_i_1), (ctrl2, j2) -> (name_2, target_i_2)...} and returns it

        def map_fun(x):
            j, cs_n_t = x
            res = {}
            for i_coll, (name, target) in cs_n_t:
                for i in i_coll:
                    res.update({(i, j): (name, target)})
            return res

        items = [(j, multigateItems.items()) for (j, multigateItems) in self.multiGates.items()]
        list_of_dicts = map(map_fun, items)
        return flatten_dicts(list_of_dicts)

    def can_put_target(self, i_ctrl, j_ctrl, i_target, j_target):
        if j_target != j_ctrl:
            return False
        if not self.__target_exists_at(i_target, j_target):
            return False
        if not self.__can_target_have_more_ctrls(i_target, j_target):
            return False
        if self.__gate_between_exists(i_ctrl, i_target, j_target):
            return False
        return True

    def __gate_between_exists(self, i_ctrl, i_target, j):
        i_list = self.__get_i_in_column(j)
        for i in i_list:
            if i_ctrl > i > i_target or i_target > i > i_ctrl:
                return True
        return False

    def __get_i_in_column(self, j):
        # returns a list of i indices at j column from a grid
        flattened_grid = self.flattenedGrid()
        return list(map(lambda ijv: ijv[0][0], filter(lambda ijv: ijv[0][1] == j, flattened_grid.items())))

    def __can_target_have_more_ctrls(self, i, j):
        if not self.multiGates.__contains__(j):
            return True
        entry = self.__get_multigate_entry(i, j)
        if len(entry) == 0:
            return True
        _, (name, _) = entry[0]
        return name == X

    def __target_exists_at(self, i, j):
        if not self.grid.__contains__(i):
            return False
        if not self.grid[i].__contains__(j):
            return False
        return True

    def put_ctrl(self, i_ctrl, i_target, j):
        target_name = self.grid[i_target][j]
        if not self.multiGates.__contains__(j):
            self.multiGates[j] = {}
        entry = self.__get_multigate_entry(i_target, j)
        if not len(entry) == 0:
            self.__add_ctrl_to_existing_gate(entry, i_ctrl, i_target, j)
        else:
            self.multiGates[j][(i_ctrl,)] = (target_name, i_target)

    def __add_ctrl_to_existing_gate(self, entry, i_ctrl, i_target, j):
        ctrls, (name, _) = entry[0]
        self.multiGates[j].__delitem__(ctrls)
        self.multiGates[j][ctrls + (i_ctrl,)] = (name, i_target)

    def __get_multigate_entry(self, i, j):
        multi_gates_at_j = self.multiGates[j]
        ctrls_with_i_target = list(filter(lambda c_nt: c_nt[1][1] == i, multi_gates_at_j.items()))
        return ctrls_with_i_target

    def __remove_control_bits(self, i, j):
        # having a target at (i,j), removes associated controlled bits
        if not self.multiGates.__contains__(j):
            return
        entry = self.__get_multigate_entry(i, j)
        if len(entry) == 0:
            return
        self.multiGates[j].__delitem__(entry[0][0])

    def nextStep(self):
        pass

    def fastForward(self):
        pass

    def breakSimulation(self):
        pass
