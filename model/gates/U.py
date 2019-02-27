from qutip import Qobj
import numpy as np
from model.gates.Gate import Gate
from model.constants import *
from util.Utils import is_iterable


class UGate(Gate):

    def __init__(self, qbit, parameters=None):
        super().__init__(qbit, parameters)
        self.__types_dict = self.__get_types_dict()
        self.__defaults_dict = self.get_parameters_defaults()

    def get_name(self):
        return U

    def get_parameters_names(self):
        return UGate.parameters_names()

    def _get_parameters_types(self):
        return self.__types_dict

    def get_parameters_defaults(self):
        defaults = ["0+0j"] * 4
        return self._map_names_to_values(defaults)

    def get_parameter_default(self, parameter_name):
        return self.__defaults_dict[parameter_name]

    def __get_types_dict(self):
        types = [complex] * 4
        return self._map_names_to_values(types)

    def is_gate_correct(self, kwargs):
        return self.__is_unitary(kwargs) if super().is_gate_correct(kwargs) else False

    def __is_unitary(self, kwargs):
        e_0, e_1, e_2, e_3 = list(map(lambda name: kwargs[name], self.get_parameters_names()))
        qobj = Qobj([[e_0, e_1], [e_2, e_3]])
        M = (qobj * qobj.conj()).full()
        return (M.shape[0] == M.shape[1]) and (M == np.eye(M.shape[0])).all()

    def why_gate_not_correct(self, kwargs):
        error_msg = super().why_gate_not_correct(kwargs)
        if error_msg == "":
            return "Gate is not unitary" if not self.__is_unitary(kwargs) else ""
        return error_msg

    def qutip_object(self):
        e_0, e_1, e_2, e_3 = list(map(lambda name: self._parameters[name], self.get_parameters_names()))
        return Qobj([[e_0, e_1], [e_2, e_3]])

    def generate_single_gate_code(self, step):
        e_0, e_1, e_2, e_3 = list(map(lambda name: self._parameters[name], self.get_parameters_names()))
        return "{0}.{1}(step={2}, target={3}, matrix=[{4:.2f}, {5:.3f}, {6:.3f}, {7:.3f}])\n"\
            .format(QUANTUM_INSTANCE, self.get_name(), step, self.target(), e_0, e_1, e_2, e_3)

    def generate_controlled_gate_code(self, step, controls):
        e_0, e_1, e_2, e_3 = list(map(lambda name: self._parameters[name], self.get_parameters_names()))
        return "{0}.{1}{2}(step={3}, ctrls={4}, target={5}, matrix=[{6:.2f}, {7:.3f}, {8:.3f}, {9:.3f}])\n".format(
            QUANTUM_INSTANCE, CONTROLLED, self.get_name(),
            step, controls, self.target(),
            e_0, e_1, e_2, e_3
        )

    @staticmethod
    def parameters_names():
        return ["m[0][0]", "m[0][1]", "m[1][0]", "m[1][1]"]

    @staticmethod
    def stringified_parameters_from(matrix):
        if not is_iterable(matrix) or len(list(matrix)) != 4:
            raise Exception("matrix should be an iterable of exactly 4 elements")
        parameters_names = UGate.parameters_names()
        parameters = {}
        for i, param_name in enumerate(parameters_names):
            parameters[param_name] = str(matrix[i])
        return parameters

    def latex_symbol(self):
        return "U"