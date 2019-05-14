import collections
import traceback

import sys
from qutip import ket

from model.CircuitStepSimulator import CircuitStepSimulator
from model.constants import MEASURE
from model.gates.GateCreator import GateCreator
from util.Utils import flatten_dicts, to_bin_str
import numpy as np
from model.gates.Measurement import MeasurementGate


class Register:

    def __init__(self, nqbits, value=0):
        self.__value = value
        self.__nqubits = nqbits
        self.__qbits = self.value_to_bits(self.__value)
        self.__qubits_hidden = [False for _ in range(nqbits)]

    def qubits_hidden(self):
        return self.__qubits_hidden

    def set_hidden_qubits(self, hidden_qubits):
        # a list of bools, qubit is hidden if hidden_qubits[i] == True
        assert all(type(x) == bool for x in hidden_qubits), "hidden_qubits should be a list of bools"
        assert len(hidden_qubits) == self.__nqubits, "hidden_qubits should have length of the original register"
        assert not all(x for x in hidden_qubits), "At least one qubit should not be hidden"
        self.__qubits_hidden = list(hidden_qubits)

    def __value_without_hidden(self, value):
        bin_s = to_bin_str(value, self.__nqubits)
        filtered_enum = list(filter(lambda iv: not self.__qubits_hidden[iv[0]], enumerate(bin_s)))
        filtered_bin_s = "".join(map(lambda iv: iv[1], filtered_enum))
        return int(filtered_bin_s, 2)

    def value(self, with_hidden=True):
        return self.__value if with_hidden else self.__value_without_hidden(self.__value)

    def nqubits(self, with_hidden=True):
        return self.__nqubits if with_hidden else sum(not h for h in self.__qubits_hidden)

    def __visible_qubits_list(self, bit_list):
        filtered_enum = list(filter(lambda iv: not self.__qubits_hidden[iv[0]], enumerate(bit_list)))
        only_visible = list(map(lambda iv: iv[1], filtered_enum))
        return only_visible

    def qbits(self, with_hidden=True):
        return self.__qbits if with_hidden else self.__visible_qubits_list(self.__qbits)

    def value_to_bits(self, value, with_hidden=True):
        if not with_hidden:
            value = self.__value_without_hidden(value)
        bin_truncated = list(map(lambda x: int(x), bin(value)[2:]))
        return [0 for i in range(self.__nqubits - bin_truncated.__len__())] + bin_truncated

    def value_to_ket(self, value, with_hidden=True):
        if not with_hidden:
            value = self.__value_without_hidden(value)
        bin_truncated = list(map(lambda x: int(x), bin(value)[2:]))
        return ket(bin_truncated)

    def bit_list_to_string_value(self, bitList, with_hidden=True):
        if not with_hidden:
            bitList = self.__visible_qubits_list(bitList)
        return "".join(map(lambda x: str(x), bitList))

    def bitlist_to_decimal(self, bitList, with_hidden=True):
        decimal = 0
        multiplier = 1
        if not with_hidden:
            bitList = self.__visible_qubits_list(bitList)
        for i in range(len(bitList) - 1, -1, -1):
            decimal += bitList[i] * multiplier
            multiplier *= 2
        return decimal

    def initial_qutip_ket(self, with_hidden=True):
        bit_list = self.__qbits
        if not with_hidden:
            bit_list = self.__visible_qubits_list(bit_list)
        return ket(self.bit_list_to_string_value(bit_list))

    def swap_bit_at(self, i):
        b = self.__qbits[i]
        self.__qbits[i] = 1 if b == 0 else 0
        self.__value = self.bitlist_to_decimal(self.__qbits)

    def __prepared_state(self, psi, with_hidden=True):
        if not with_hidden:
            for target in self.__qubits_hidden:
                measure_gate = MeasurementGate(target)
                psi = measure_gate.transform(psi, self.__nqubits)
        existing_states_with_amplitudes = dict(
            map(
                lambda x: (self.__value_without_hidden(x), psi.data[x, 0]) if not with_hidden else (x, psi.data[x, 0]), 
                psi.data.tocoo().row
            )
        )
        return psi, existing_states_with_amplitudes

    def print_register_state(self, psi, with_hidden=True):
        psi, existing_states_with_amplitudes = self.__prepared_state(psi, with_hidden)
        for existing_state, amplitude in existing_states_with_amplitudes.items():
            binS = to_bin_str(existing_state, self.nqubits(with_hidden))
            probability = np.abs(amplitude) ** 2
            print("|{}> |{}>: prob: {} ampl: {}".format(existing_state, binS, probability, amplitude))
        print("="*20)

    def current_psi_representation(self, psi, with_hidden=True):
        nqubits = self.nqubits(with_hidden)
        representation = []
        psi, existing_states_with_amplitudes = self.__prepared_state(psi, with_hidden)
        for existing_state, amplitude in existing_states_with_amplitudes.items():
            binS = to_bin_str(existing_state, nqubits)
            probability = np.abs(amplitude) ** 2
            valueS = "|{}>".format(existing_state)
            qubitsS = "|{}>".format(binS)
            probabilityS = "{:.2f}".format(probability)
            amplitudeS = "{:.2f}".format(amplitude)
            representation.append((valueS, qubitsS, probabilityS, amplitudeS))
        return representation


class Circuit:

    def __init__(self, quantum_computer, nqbits):
        assert nqbits > 0, "Number of qubits must be bigger than 0"
        self.__quantum_computer = quantum_computer
        self.__register = Register(nqbits=nqbits)
        self.__gate_creator = GateCreator()
        self.__step_simulator = CircuitStepSimulator(self)
        self.__grid = {}  # dict of dicts of single gates, {i: {j : gate}}
        self.__multi_gates = {}
        # ^ dict of dicts { j -> { (ctrl1, ctrl2 ...) -> gate } }, where name is a simple target gate name,
        # whereas j is a column in the grid, and ctrl_i are indices of rows, and target is a row of simple gate

    def init_register(self, nqubits, value):
        assert nqubits > 0, "Number of qubits must be bigger than 0"
        self.__register = Register(nqbits=nqubits, value=value)
        self.__step_simulator = CircuitStepSimulator(self)
        self.__grid = {}  # dict of dicts of single gates, {i: {j : gate}}
        self.__multi_gates = {}

    def current_psi_representation(self, with_hidden=True):
        psi = self.current_simulation_psi()
        return self.__register.current_psi_representation(psi, with_hidden)

    def print_register_state(self, with_hidden=True):
        psi = self.current_simulation_psi()
        self.__register.print_register_state(psi, with_hidden)

    def get_hidden_qubits(self):
        return self.__register.qubits_hidden()

    def set_hidden_qubits(self, hidden_qubits):
        self.__register.set_hidden_qubits(hidden_qubits)

    def set_to(self, value):
        ket_value = self.__register.value_to_ket(value)
        self.__step_simulator.set_current_psi(ket_value)

    def step_already_simulated(self, step):
        return self.__step_simulator.step_already_simulated(step)

    def initial_int_value(self):
        return self.__register.value()

    def current_simulation_psi(self):
        psi = self.__step_simulator.current_simulation_psi()
        return psi if self.__step_simulator.is_simulation_on() else self.initial_register_ket()

    def initial_register_ket(self):
        return self.__register.initial_qutip_ket()

    def recreate_gate_at(self, i, j, gate):
        return self.add_gate(i, j, gate.get_name(), gate.parameters())

    def copy_gate_at(self, i, j, gate_copy):
        return self.add_gate(i, j, gate_copy.get_name(), gate_copy.parameters())

    def circuit_qubits_number(self):
        return self.__register.nqubits()

    def can_add_gate_at(self, i, j):
        if j < 0:
            return False
        if self.__register.nqubits() <= i or i < 0:
            return False
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
        return self.__register.qbits()[i]

    def swap_qbit_value_at(self, i):
        self.__register.swap_bit_at(i)

    def add_qbit(self):
        self.__register = self.__register_with_added_qbit()
        self.update_schodringer_experiments()

    def update_schodringer_experiments(self):
        # check if can add schodringer experiment working only with one qubit
        if self.__register.nqubits() == 1:
            self.__quantum_computer.add_schodringer_experiment_if_not_exists()
        else:
            self.__quantum_computer.remove_schodringer_experiment_if_exists()

    def remove_qbit(self, i):
        assert self.__register.nqubits() > 1, "Number of qubits must be bigger than 0"
        if self.__grid.__contains__(i):
            self.__grid.__delitem__(i)
        self.__shift_grid(i)
        self.__register = self.__register_with_removed_qbit(i)
        self.__multi_gates = self.__multi_qbit_gates_after_qbit_removed(i)
        self.update_schodringer_experiments()

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

    def __update_target_bits(self, shifted_gates):
        for target, j_gate in shifted_gates.items():
            for j, gate in j_gate.items():
                gate.set_target(target - 1)

    def __shift_grid(self, i):
        indecies_bigger_than_i = list(filter(lambda x: x > i, self.__grid.keys()))
        indecies_lower_than_i = list(filter(lambda x: x < i, self.__grid.keys()))
        values_of_bigger_indicies = {x: self.__grid[x] for x in indecies_bigger_than_i}
        values_of_lower_indicies = {x: self.__grid[x] for x in indecies_lower_than_i}
        self.__grid = {x: values_of_lower_indicies[x] for x in indecies_lower_than_i}
        self.__grid.update({x - 1: values_of_bigger_indicies[x] for x in indecies_bigger_than_i})
        self.__update_target_bits(values_of_bigger_indicies)

    def __register_with_removed_qbit(self, i):
        v = self.__register.value()
        bitsList = self.__register.value_to_bits(v)
        bitlist_with_removed_qbit = bitsList[:i] + bitsList[i + 1:]
        return Register(
            nqbits=self.__register.nqubits() - 1,
            value=self.__register.bitlist_to_decimal(bitlist_with_removed_qbit)
        )

    def __register_with_added_qbit(self):
        v = self.__register.value()
        bitsList = self.__register.value_to_bits(v)
        bitlist_with_added_qbit = bitsList + [0]
        return Register(
            nqbits=self.__register.nqubits() + 1,
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
        if j_target != j_ctrl or i_ctrl == i_target or j_ctrl < 0:
            return False
        if self.__register.nqubits() <= i_ctrl or i_ctrl < 0:
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

    def simulation_single_gates_dict(self):
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

    def simulation_measure_gates_dict(self):
        def reject(_i, _j, gate):
            return gate.get_name() != MEASURE
        return self.__simulation_gates_dict(reject)

    def simulation_multi_gates_dict(self):
        return collections.OrderedDict(sorted(self.__multi_gates.items()))

    def next_step(self):
        self.__with_initialization(self.__step_simulator.next_step)

    def fast_forward(self, measure=False):
        self.__with_initialization(self.__step_simulator.fast_forward, measure)

    def back_step(self):
        self.__with_initialization(self.__step_simulator.back_step)

    def fast_back(self):
        self.__step_simulator.fast_back()

    def __with_initialization(self, simulator_fun, measure=False):
        single_gates = self.simulation_single_gates_dict()
        measure_gates = self.simulation_measure_gates_dict()
        multi_gates = self.simulation_multi_gates_dict()
        if measure:
            simulator_fun(single_gates, measure_gates, multi_gates, measure)
        else:
            simulator_fun(single_gates, measure_gates, multi_gates)

    def simulation_step(self):
        return self.__step_simulator.simulation_step()

    def get_gate_at(self, i, j):
        grid_i = self.__grid.get(i, None)
        if grid_i is not None:
            return grid_i.get(j, None)

    def get_max_simulation_step(self):
        return self.__step_simulator.get_max_simulation_step()

if __name__ == '__main__':
    reg = Register(nqbits=5, value=5)
    psi = ket("00101")
    reg.print_register_state()
    reg.set_hidden_qubits([False, False, False, True, False])
    reg.print_register_state(psi, with_hidden=False)