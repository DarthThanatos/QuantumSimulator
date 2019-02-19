import collections

from qutip import ket

from model.CircuitStepSimulator import CircuitStepSimulator
from model.constants import MEASURE
from model.gates.GateCreator import GateCreator
from util.Utils import flatten_dicts


class Register:
    def __init__(self, nqbits, value=0):
        self.value = value
        self.nqubits = nqbits
        self.qbits = self.value_to_bits(self.value)

    def value_to_bits(self, value):
        bin_truncated = list(map(lambda x: int(x), bin(value)[2:]))
        return [0 for i in range(self.nqubits - bin_truncated.__len__())] + bin_truncated

    def bit_list_to_string_value(self, bitList):
        return "".join(map(lambda x: str(x), bitList))

    def bitlist_to_decimal(self, bitList):
        decimal = 0
        multiplier = 1
        for i in range(len(bitList) - 1, -1, -1):
            decimal += bitList[i] * multiplier
            multiplier *= 2
        return decimal

    def swap_bit_at(self, i):
        b = self.qbits[i]
        self.qbits[i] = 1 if b == 0 else 0
        self.value = self.bitlist_to_decimal(self.qbits)

    def update_register_with(self, newValue, newBitlist):
        self.value = newValue
        self.qbits = newBitlist

    def initial_qutip_ket(self):
        return ket(self.bit_list_to_string_value(self.qbits))


class Circuit:

    def __init__(self, nqbits):
        self.__register = Register(nqbits=nqbits)
        self.__gate_creator = GateCreator()
        self.__step_simulator = CircuitStepSimulator(self)
        self.__grid = {}  # dict of dicts of single gates, {i: {j : gate}}
        self.__multi_gates = {}
        # ^ dict of dicts { j -> { (ctrl1, ctrl2 ...) -> gate } }, where name is a simple target gate name,
        # whereas j is a column in the grid, and ctrl_i are indices of rows, and target is a row of simple gate

    def current_simulation_psi(self):
        psi = self.__step_simulator.current_simulation_psi()
        return psi if self.__step_simulator.is_simulation_on() else self.initial_register_ket()

    def initial_register_ket(self):
        return self.__register.initial_qutip_ket()

    def recreate_gate_at(self, i, j, gate):
        return self.add_gate(i, j, gate.get_name(), gate.parameters())

    def circuit_qubits_number(self):
        return self.__register.nqubits

    def can_add_gate_at(self, i, j):
        if self.__overlaps_single_gate(i, j):
            return False
        if self.__overlaps_multi_gate(i, j):
            return False
        return True

    def __overlaps_single_gate(self, i, j):
        return self.__grid.__contains__(i) and self.__grid[i].__contains__(j)

    def __overlaps_multi_gate(self, i, j):
        if not self.__multi_gates.__contains__(j):
            return False
        for ctrl_i_tuple, gate in self.__multi_gates[j].items():
            target_i = gate.target()
            for ctrl_i in ctrl_i_tuple:
                if ctrl_i >= i >= target_i or target_i >= i >= ctrl_i:
                    return True
        return False

    def add_gate(self, i, j, name, parameters=None):
        if not self.__grid.__contains__(i):
            self.__grid[i] = {}
        gate = self.__gate_creator.createGate(name, i, parameters)
        self.__grid[i][j] = gate
        return gate

    def remove_gate(self, i, j):
        gate = self.__grid[i][j]
        self.__grid[i].__delitem__(j)
        self.__remove_control_bits(i, j)
        return gate

    def qbit_value_at(self, i):
        return self.__register.qbits[i]

    def swap_qbit_value_at(self, i):
        self.__register.swap_bit_at(i)

    def remove_qbit(self, i):
        if self.__grid.__contains__(i):
            self.__grid.__delitem__(i)
        self.__shift_grid(i)
        self.__register = self.__register_with_removed_qbit(i)
        self.__multi_gates = self.__multi_qbit_gates_after_qbit_removed(i)

    def __multi_qbit_gates_after_qbit_removed(self, i):
        new_multi_gates_dict = {}
        for j in self.__multi_gates:
            new_multi_gates_dict[j] = {}
            for ctrl_i_tuple, gate in self.__multi_gates[j].items():
                name, target_i = gate.get_name(), gate.target()
                if target_i != i:
                    new_ctrl_indexes_tuple = ()
                    for ctrl_i in ctrl_i_tuple:
                        if ctrl_i != i:
                            new_ctrl_indexes_tuple += (ctrl_i - 1 if ctrl_i > i else ctrl_i,)
                    if len(new_ctrl_indexes_tuple) > 0:
                        gate.set_target(target_i - 1 if target_i > i else target_i)
                        new_multi_gates_dict[j][new_ctrl_indexes_tuple] = gate
            if new_multi_gates_dict[j].items().__len__() == 0:
                new_multi_gates_dict.__delitem__(j)
        return new_multi_gates_dict

    def add_qbit(self):
        self.__register = self.__register_with_added_qbit()

    def __shift_grid(self, i):
        indecies_bigger_than_i = list(filter(lambda x: x > i, self.__grid.keys()))
        indecies_lower_than_i = list(filter(lambda x: x < i, self.__grid.keys()))
        values_of_bigger_indicies = {x: self.__grid[x] for x in indecies_bigger_than_i}
        values_of_lower_indicies = {x: self.__grid[x] for x in indecies_lower_than_i}
        self.__grid = {x: values_of_lower_indicies[x] for x in indecies_lower_than_i}
        self.__grid.update({x - 1: values_of_bigger_indicies[x] for x in indecies_bigger_than_i})

    def __register_with_removed_qbit(self, i):
        v = self.__register.value
        bitsList = self.__register.value_to_bits(v)
        bitlist_with_removed_qbit = bitsList[:i] + bitsList[i + 1:]
        return Register(
            nqbits=self.__register.nqubits - 1,
            value=self.__register.bitlist_to_decimal(bitlist_with_removed_qbit)
        )

    def __register_with_added_qbit(self):
        v = self.__register.value
        bitsList = self.__register.value_to_bits(v)
        bitlist_with_added_qbit = bitsList + [0]
        return Register(
            nqbits=self.__register.nqubits + 1,
            value=self.__register.bitlist_to_decimal(bitlist_with_added_qbit)
        )

    def flattened_grid(self):
        # returns a one-dimensional copy of the grid instead of the original two dimensional structure
        list_of_dicts = [{(y[0], j): gate.get_name() for (j, gate) in y[1].items()} for y in self.__grid.items()]
        return flatten_dicts(list_of_dicts)

    def flattened_multi_gates(self):
        # transforms { j: { (ctrl1, ctrl2 ...) -> (name, target) } }
        # to {(ctrl1, j1) -> (name_1, target_i_1), (ctrl2, j2) -> (name_2, target_i_2)...} and returns it

        def map_fun(x):
            j, cs_n_t = x
            res = {}
            for i_coll, gate in cs_n_t:
                name, target = gate.get_name(), gate.target()
                for i in i_coll:
                    res.update({(i, j): (name, target)})
            return res

        items = [(j, multigateItems.items()) for (j, multigateItems) in self.__multi_gates.items()]
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
        flattened_grid = self.flattened_grid()
        return list(map(lambda ijv: ijv[0][0], filter(lambda ijv: ijv[0][1] == j, flattened_grid.items())))

    def __can_target_have_more_ctrls(self, i, j):
        if not self.__multi_gates.__contains__(j):
            gate = self.__grid[i][j]
            return gate.get_name() != MEASURE
        return True

    def __target_exists_at(self, i, j):
        if not self.__grid.__contains__(i):
            return False
        if not self.__grid[i].__contains__(j):
            return False
        return True

    def put_ctrl(self, i_ctrl, i_target, j):
        gate = self.__grid[i_target][j]
        if not self.__multi_gates.__contains__(j):
            self.__multi_gates[j] = {}
        entry = self.__get_multigate_entry(i_target, j)
        if not len(entry) == 0:
            self.__add_ctrl_to_existing_gate(entry, i_ctrl, j)
        else:
            self.__multi_gates[j][(i_ctrl,)] = gate

    def __add_ctrl_to_existing_gate(self, entry, i_ctrl, j):
        ctrls, gate = entry[0]
        self.__multi_gates[j].__delitem__(ctrls)
        self.__multi_gates[j][ctrls + (i_ctrl,)] = gate

    def __get_multigate_entry(self, i, j):
        multi_gates_at_j = self.__multi_gates[j]
        ctrls_with_i_target = list(filter(lambda c_nt: c_nt[1].target() == i, multi_gates_at_j.items()))
        return ctrls_with_i_target

    def __remove_control_bits(self, i, j):
        # having a target at (i,j), removes associated controlled bits
        if not self.__multi_gates.__contains__(j):
            return
        entry = self.__get_multigate_entry(i, j)
        if len(entry) == 0:
            return
        self.__multi_gates[j].__delitem__(entry[0][0])
        if self.__multi_gates[j].items().__len__() == 0:
            self.__multi_gates.__delitem__(j)

    def __simulation_gates_dict(self, reject):
        simulation_gates = {}
        for i in self.__grid:
            for j in self.__grid[i]:
                gate = self.__grid[i][j]
                if reject(i, j, gate):
                    continue
                if not simulation_gates.__contains__(j):
                    simulation_gates[j] = {}
                simulation_gates[j][i] = gate
        return collections.OrderedDict(sorted(simulation_gates.items()))

    def __simulation_single_gates_dict(self):
        def reject(i, j, gate):
            return self.__gate_entry_in_multi_gates(i, j) or gate.get_name() == MEASURE
        return self.__simulation_gates_dict(reject)

    def __gate_entry_in_multi_gates(self, i, j):
        if j not in self.__multi_gates:
            return False
        for ctrl_i_tuple, gate in self.__multi_gates[j].items():
            if gate.target() == i:
                return True
        return False

    def __simulation_measure_gates_dict(self):
        def reject(_i, _j, gate):
            return gate.get_name() != MEASURE
        return self.__simulation_gates_dict(reject)

    def __simulation_multi_gates_dict(self):
        return collections.OrderedDict(sorted(self.__multi_gates.items()))

    def next_step(self):
        self.__with_initialization(self.__step_simulator.next_step)

    def fast_forward(self):
        self.__with_initialization(self.__step_simulator.fast_forward)

    def back_step(self):
        self.__with_initialization(self.__step_simulator.back_step)

    def fast_back(self):
        self.__step_simulator.fast_back()

    def __with_initialization(self, simulator_fun):
        single_gates = self.__simulation_single_gates_dict()
        measure_gates = self.__simulation_measure_gates_dict()
        multi_gates = self.__simulation_multi_gates_dict()
        simulator_fun(single_gates, measure_gates, multi_gates)

    def simulation_step(self):
        return self.__step_simulator.simulation_step()

