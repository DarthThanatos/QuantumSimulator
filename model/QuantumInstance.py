import traceback

from model.constants import *
from model.gates.CPhase import CPhaseKick
from model.gates.PhaseKick import PhaseKickGate
from model.gates.PhaseScale import PhaseScaleGate
from model.gates.Rotation import Rotation
from model.gates.RotationX import RotationXGate
from model.gates.RotationY import RotationYGate
from model.gates.RotationZ import RotationZGate
from model.gates.U import UGate
from util.Utils import eprint, is_iterable

class QuantumInstance:

    def __init__(self, should_simulate, circuit):
        self.__circuit = circuit
        self.__should_simulate = should_simulate

    def init_register(self, nqubits, value):
        self.__circuit.init_register(nqubits, value)

    def current_simulation_psi(self):
        return self.__circuit.current_simulation_psi()

    def set_to(self, value):
        if not type(value) is int:
            msg = "argument of set_to must be an integer"
            eprint(msg)
            raise Exception(msg)
        nqubits = self.__circuit.circuit_qubits_number()
        if value > (2 ** nqubits) - 1:
            msg = "setting register to value {} would cause an overflow with number of qubits = {}".format(value, nqubits)
            eprint(msg)
            raise Exception(msg)
        self.__circuit.set_to(value)

    def __try_add_single_gate(self, i, j, name, parameters=None):
        if self.__circuit.step_already_simulated(j):
            msg = "step {} has already been simulated".format(j)
            eprint(msg)
            raise Exception(msg)
        if not self.__circuit.can_add_gate_at(i, j):
            msg = "can't add {} gate at target {} step: {}".format(name, i, j)
            eprint(msg)
            raise Exception(msg)
        gate = self.__circuit.add_gate(i, j, name)
        correct = True
        msg = ""
        if parameters is not None:
            for parameter_name, value in parameters.items():
                correct &= gate.is_parameter_correct(parameter_name, value)
                if not correct:
                    msg += gate.why_is_parameter_incorrect(parameter_name, value) + "\n"
            gate_correct = gate.is_gate_correct(parameters)
            if not gate_correct:
                msg += gate.why_gate_not_correct(parameters) + '\n'
            else:
                for parameter_name, value in parameters.items():
                    gate.set_parameter_value(parameter_name, value)
            correct &= gate_correct
        if not correct:
            self.__circuit.remove_gate(i, j)
            eprint(msg)
            raise Exception(msg)
        return True

    def __add_controlled_gate(self, j, ctrls, target, name, parameters=None):
        if not is_iterable(ctrls):
            msg = 'controls must be iterable'
            eprint(msg)
            raise Exception(msg)
        is_added = self.__try_add_single_gate(target, j, name, parameters)
        if not is_added:
            msg = "gate is not added at {}, {}".format(target, j)
            eprint(msg)
            raise Exception(msg)
        for ctrl in ctrls:
            if not self.__circuit.can_add_gate_at(ctrl, j):
                msg = "can't place {} control at {} step: {}".format(name, ctrl, j)
                self.__circuit.remove_gate(target, j)
                eprint(msg)
                raise Exception(msg)
            if not self.__circuit.can_put_target(ctrl, j, target, j):
                msg = "can't connect {} control {} to target {} at step {}".format(name, ctrl, target, j)
                self.__circuit.remove_gate(target, j)
                eprint(msg)
                raise Exception(msg)
        for ctrl in ctrls:
            self.__circuit.put_ctrl(ctrl, target, j)

    def X(self, step, target):
        self.__try_add_single_gate(i=target, j=step, name=X)

    def Y(self, step, target):
        self.__try_add_single_gate(i=target, j=step, name=Y)

    def Z(self, step, target):
        self.__try_add_single_gate(i=target, j=step, name=Z)

    def H(self, step, target):
        self.__try_add_single_gate(i=target, j=step, name=H)

    def sqrt_x(self, step, target):
        self.__try_add_single_gate(i=target, j=step, name=SQRT_X)

    def measure(self, step, target):
        self.__try_add_single_gate(i=target, j=step, name=MEASURE)

    def r_x(self, step, target, angle):
        parameters = Rotation.stringified_parameters_from(angle, RotationXGate.axis())
        self.__try_add_single_gate(target, step, ROTATION_X, parameters)

    def r_y(self, step, target, angle):
        parameters = Rotation.stringified_parameters_from(angle, RotationYGate.axis())
        self.__try_add_single_gate(target, step, ROTATION_Y, parameters)

    def r_z(self, step, target, angle):
        parameters = Rotation.stringified_parameters_from(angle, RotationZGate.axis())
        self.__try_add_single_gate(target, step, ROTATION_Z, parameters)

    def cphase(self, step, target, k):
        parameters = CPhaseKick.stringified_parameters_from(k)
        self.__try_add_single_gate(target, step, C_PHASE_KICK, parameters)

    def inv_cphase(self, step, target, k):
        parameters = CPhaseKick.stringified_parameters_from(k)
        self.__try_add_single_gate(target, step, INV_C_PHASE_KICK, parameters)

    def phase_kick(self, step, target, angle):
        parameters = PhaseKickGate.stringified_parameters_from(angle)
        self.__try_add_single_gate(target, step, PHASE_KICK, parameters)

    def phase_scale(self, step, target, angle):
        parameters = PhaseScaleGate.stringified_parameters_from(angle)
        self.__try_add_single_gate(target, step, PHASE_SCALE, parameters)

    def U(self, step, target, matrix):
        try:
            parameters = UGate.stringified_parameters_from(matrix)
            self.__try_add_single_gate(target, step, U, parameters)
        except Exception:
            traceback.print_exc()
            raise

    def controlledX(self, step, ctrls, target):
        self.__add_controlled_gate(step, ctrls, target, X)

    def controlledY(self, step, ctrls, target):
        self.__add_controlled_gate(step, ctrls, target, Y)

    def controlledZ(self, step, ctrls, target):
        self.__add_controlled_gate(step, ctrls, target, Z)

    def controlledH(self, step, ctrls, target):
        self.__add_controlled_gate(step, ctrls, target, H)

    def controlledsqrt_x(self, step, ctrls, target):
        self.__add_controlled_gate(step, ctrls, target, SQRT_X)

    def controlledr_x(self, step, ctrls, target, angle):
        parameters = Rotation.stringified_parameters_from(angle, RotationXGate.axis())
        self.__add_controlled_gate(step, ctrls, target, ROTATION_X, parameters)

    def controlledr_y(self, step, ctrls, target, angle):
        parameters = Rotation.stringified_parameters_from(angle, RotationYGate.axis())
        self.__add_controlled_gate(step, ctrls, target, ROTATION_Y, parameters)

    def controlledr_Z(self, step, ctrls, target, angle):
        parameters = Rotation.stringified_parameters_from(angle, RotationZGate.axis())
        self.__add_controlled_gate(step, ctrls, target, ROTATION_Z, parameters)

    def controlledphase_kick(self, step, ctrls, target, angle):
        parameters = PhaseKickGate.stringified_parameters_from(angle)
        self.__add_controlled_gate(step, ctrls, target, PHASE_KICK, parameters)

    def controlledphase_scale(self, step, ctrls, target, angle):
        parameters = PhaseScaleGate.stringified_parameters_from(angle)
        self.__add_controlled_gate(step, ctrls, target, PHASE_SCALE, parameters)

    def controlledcphase(self, step, ctrls, target, k):
        parameters = CPhaseKick.stringified_parameters_from(k)
        self.__add_controlled_gate(step, ctrls, target, C_PHASE_KICK, parameters)

    def controlledinv_cphase(self, step, ctrls, target, k):
        parameters = CPhaseKick.stringified_parameters_from(k)
        self.__add_controlled_gate(step, ctrls, target, INV_C_PHASE_KICK, parameters)

    def controlledU(self, step, ctrls, target, matrix):
        try:
            parameters = UGate.stringified_parameters_from(matrix)
            self.__add_controlled_gate(step, ctrls, target, U, parameters)
        except Exception:
            traceback.print_exc()

    def next_step(self):
        self.__circuit.next_step()

    def back_step(self):
        self.__circuit.back_step()

    def fast_forward(self):
        self.__circuit.fast_forward()

    def fast_back(self):
        self.__circuit.fast_back()

    def are_steps_free_at_qubit(self, from_q, to_q, qubit):
        for j in range(from_q, to_q):
            if not self.__circuit.can_add_gate_at(qubit, j):
                return False
        return True

    def get_measured(self):
        self.__circuit.fast_forward(measure=True)
        measured = self.__circuit.current_simulation_psi()
        return measured.data.tocoo().row[0]

    def set_hidden_qubits(self, hidden_qubits):
        # here we expect a list of numbers indicating valid indices of qubits
        nqubits = self.__circuit.circuit_qubits_number()
        assert all(type(x) == int and 0 <= x < nqubits for x in hidden_qubits), "hidden_qubits should be a list of ints in range(0, nqubits), where nqubits is the number of qubits in the original register"
        hidden_qubits = [True if i in hidden_qubits else False for i in range(nqubits)]
        self.__circuit.set_hidden_qubits(hidden_qubits)

    def print_register_state(self, with_hidden=True):
        self.__circuit.print_register_state(with_hidden)
