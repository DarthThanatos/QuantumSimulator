class QuantumInstance:

    def __init__(self, should_simulate, circuit):
        self.__circuit = circuit
        self.__nqubits = 0
        self.__register_value = 0
        self.__should_simulate = should_simulate

    def init_register(self, nqubits, value):
        self.__nqubits = nqubits
        self.__register_value = value

    def X(self, step, target):
        pass

    def Y(self, step, target):
        pass

    def Z(self, step, target):
        pass

    def r_x(self, step, target, angle):
        pass

    def r_y(self, step, target, angle):
        pass

    def H(self, step, target):
        pass

    def sqrt_x(self, step, target):
        pass

    def phase_kick(self, step, target, angle):
        pass

    def phase_scale(self, step, target, angle):
        pass

    def cphase(self, step, target, k):
        pass

    def inv_cphase(self, step, target, k):
        pass

    def U(self, step, target, matrix):
        pass

    def controlledX(self, step, ctrls, target):
        pass

    def controlledY(self, step, ctrls, target):
        pass

    def controlledZ(self, step, ctrls, target):
        pass

    def controlledr_x(self, step, ctrls, target, angle):
        pass

    def controlledr_y(self, step, ctrls, target, angle):
        pass

    def controlledH(self, step, ctrls, target):
        pass

    def controlledsqrt_x(self, step, ctrls, target):
        pass

    def controlledphase_kick(self, step, ctrls, target, angle):
        pass

    def controlledphase_scale(self, step, ctrls, target, angle):
        pass

    def controlledcphase(self, step, ctrls, target, angle):
        pass

    def controlledinv_cphase(self, step, ctrls, target, angle):
        pass

    def controlledU(self, step, ctrls, target, matrix):
        pass

    def measure(self, step, target):
        pass

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