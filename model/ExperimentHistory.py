import datetime


from model.SchodringerExperiment import SchodringerExperiment


class CircuitExpriment:

    def __init__(self, circuit, index):
        self.__circuit__ = circuit
        self.__date = datetime.datetime.now()
        self.__index = index

    def date(self):
        return self.__date

    def index(self):
        return self.__index

    def circuit(self):
        return self.__circuit__


class ExperimentHistory:

    def __init__(self, quantum_computer):
        self.__quantum_computer = quantum_computer
        self.__circuit_experiments = []
        self.__schodringer_experiments = {}
        self.__current_experment_index = -1

    def store_cricuit_experiment(self, circuit):
        index = len(self.__circuit_experiments)
        circuit_experiment = CircuitExpriment(circuit, index)
        self.__circuit_experiments.append(circuit_experiment)
        return index

    def restore_circuit_experiment(self, experiment_index):
        circuit_experiment = self.__circuit_experiments[experiment_index]
        circuit = circuit_experiment.circuit()
        self.__quantum_computer.set_circuit(circuit)
        self.__current_experment_index = experiment_index
        circuit.update_schodringer_experiments()

    def all_experiments(self):
        return self.__circuit_experiments[:]

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