import datetime

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

    def __init__(self, quantum_computer, initial_circuit):
        self.__quantum_computer = quantum_computer
        self.__circuit_experiments = []
        self.store_cricuit_experiment(initial_circuit)

    def store_cricuit_experiment(self, circuit):
        index = len(self.__circuit_experiments)
        circuit_experiment = CircuitExpriment(circuit, index)
        self.__circuit_experiments.append(circuit_experiment)
        return index

    def restore_circuit_experiment(self, experiment_index):
        circuit_experiment = self.__circuit_experiments[experiment_index]
        self.__quantum_computer.set_circuit(circuit_experiment.circuit())

    def all_experiments(self):
        return self.__circuit_experiments[:]