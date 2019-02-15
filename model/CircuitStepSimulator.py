import collections

from functools import reduce


class CircuitStepSimulator:

    def __init__(self, quantum_computer):
        # single_gates: dict of dicts {j -> {i -> gate}}
        # multi_gates: dict of dicts {j -> {ctrl_i_tuple -> gate}}
        # please note that gates in single_gates and multi_gates should be disjoint
        self.__single_gates = None
        self.__measure_gates = None
        self.__multi_gates = None
        self.__simulation_on = False
        self.__step = -1
        self.__quantum_computer = quantum_computer
        self.__current_psi = quantum_computer.initial_register_ket()

    def is_simulation_on(self):
        return self.__simulation_on

    def simulation_step(self):
        return self.__step

    def fast_forward(self, single_gates, measure_gates, multi_gates):
        self.__initialize(single_gates, measure_gates, multi_gates)
        next_j = self.__find_next_step()
        while next_j != self.__step:
            print("fast forward", next_j)
            self.__step = next_j
            next_j = self.__find_next_step()

    def next_step(self, single_gates, measure_gates, multi_gates):
        self.__initialize(single_gates, measure_gates, multi_gates)
        next_j = self.__find_next_step()
        if next_j != self.__step:
            self.__step = next_j
            print("next step", next_j)

    def __initialize(self, single_gates, measure_gates, multi_gates):
        self.__single_gates = single_gates
        self.__measure_gates = measure_gates
        self.__multi_gates = multi_gates
        self.__simulation_on = True

    def back_step(self, single_gates, measure_gates, multi_gates):
        self.__initialize(single_gates, measure_gates, multi_gates)
        if self.__measure_gates.__contains__(self.__step) or self.__step == -1:
            return
        self.__step = self.__find_previous_step()
        # do some rollback simulation here
        print("back step", self.__step)

    def fast_back(self):
        self.__simulation_on = False
        self.__step = -1
        print("fast back")

    def __find_next_step(self):
        gates_dicts = [self.__single_gates, self.__measure_gates, self.__multi_gates]
        smallest_steps = list(map(lambda x: self.__min_step_bigger_than_current(x), gates_dicts))
        smallest_steps = list(filter(lambda x: x != self.__step, smallest_steps))
        if len(smallest_steps) == 0: return self.__step
        min_step = reduce(lambda acc, x: x if acc > x else acc, smallest_steps)
        return min_step

    def __find_previous_step(self):
        gates_dicts = [self.__single_gates, self.__measure_gates, self.__multi_gates]
        biggest_steps = list(map(lambda x: self.__max_step_smaller_than_current(x), gates_dicts))
        biggest_steps = list(filter(lambda x: x != self.__step, biggest_steps))
        if len(biggest_steps) == 0: return -1
        max_step = reduce(lambda acc, x: x if acc < x < self.__step else acc, biggest_steps)
        return max_step

    def __min_step_bigger_than_current(self, gates_dict):
        steps_bigger_than = list(filter(lambda x: x> self.__step, gates_dict.keys()))
        return steps_bigger_than[0] if len(steps_bigger_than) > 0 else self.__step

    def __max_step_smaller_than_current(self, gates_dict):
        steps_smaller_than = list(filter(lambda x: x < self.__step, sorted(gates_dict.keys(), reverse=True)))
        return steps_smaller_than[0] if len(steps_smaller_than) > 0 else self.__step

    def __str__(self):
        return "single gates: {}\nmeasure gates: {}\nmulti gates: {}".format(
            self.__single_gates,
            self.__measure_gates,
            self.__multi_gates
        )
