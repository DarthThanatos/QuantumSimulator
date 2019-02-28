import datetime
import uuid

from model.SchodringerExperiment import SchodringerExperiment


class CircuitExpriment:

    def __init__(self, circuit, index):
        self.__circuit__ = circuit
        self.__date = datetime.datetime.now()
        self.__index = index
        self.__name = ""

    def name(self):
        return self.__name

    def set_name(self, name):
        self.__name = name

    def date(self):
        return self.__date

    def index(self):
        return self.__index

    def circuit(self):
        return self.__circuit__


class ExperimentHistory:

    def __init__(self, quantum_computer):
        self.__quantum_computer = quantum_computer
        self.__circuit_experiments = {}
        self.__schodringer_experiments = {}
        self.__current_experment_index = -1

    def store_cricuit_experiment(self, circuit):
        index = uuid.uuid4()
        circuit_experiment = CircuitExpriment(circuit, index)
        self.__circuit_experiments[index] = circuit_experiment
        return index

    def restore_circuit_experiment(self, experiment_index):
        circuit_experiment = self.__circuit_experiments[experiment_index]
        circuit = circuit_experiment.circuit()
        self.__quantum_computer.set_circuit(circuit)
        self.__current_experment_index = experiment_index
        circuit.update_schodringer_experiments()

    def all_experiments(self):
        return self.__circuit_experiments.values()

    def add_schodringer_experiment_if_not_exists(self):
        index = self.__current_experment_index
        sch_exps = self.__schodringer_experiments
        if index not in sch_exps:
            circuit = self.__circuit_experiments[index].circuit()
            experiment = SchodringerExperiment(circuit)
            sch_exps[index] = experiment

    def remove_schodringer_experiment_if_exists(self):
        index = self.__current_experment_index
        sch_exps = self.__schodringer_experiments
        if index in sch_exps:
            sch_exps.__delitem__(index)

    def get_current_schodringer_experiment(self):
        return self.__schodringer_experiments.get(self.__current_experment_index, None)

    def rename_experiment(self, index, new_name):
        circuit_experiment = self.__circuit_experiments[index]
        circuit_experiment.set_name(new_name)

    def remove_experiment(self, index):
        if self.__circuit_experiments.keys().__len__() == 1:
            raise Exception("There must be at least one existing experiment at a time")
        if self.__circuit_experiments.__contains__(index):
            self.__circuit_experiments.__delitem__(index)
        if self.__schodringer_experiments.__contains__(index):
            self.__schodringer_experiments.__delitem__(index)
        if self.__circuit_experiments.keys().__len__() == 1:
            key = list(self.__circuit_experiments.keys())[0]
            self.restore_circuit_experiment(key)