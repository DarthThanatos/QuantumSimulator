class QuantumInstance:

    def __init__(self, should_simulate, circuit):
        self.__circuit = circuit
        self.__nqubits = 0
        self.__register_value = 0
        self.__should_simulate = should_simulate

    def __private_meth(self):
        print("private")

    def hello_world(self):
        print("hello world")
        print(self.__should_simulate)
        print("simulating" if self.__should_simulate else "just building circuit yo")

    def init_register(self, nqubits, register_value):
        self.__nqubits = nqubits
        self.__register_value = register_value

    def next_step(self):
        pass

    def prev_step(self):
        pass

    def fast_forward(self):
        pass

    def fast_back(self):
        pass

    def __str__(self):
        return "quantum instance with nqubits: {}, and register value: {}".format(self.__nqubits, self.__register_value)