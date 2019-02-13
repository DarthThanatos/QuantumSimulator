from qutip import Qobj
import numpy as np
from model.gates.Gate import Gate
from model.constants import *


class UGate(Gate):

    def __init__(self, qbit):
        super().__init__(qbit)
        self.__types_dict = self.__get_types_dict()
        self.__defaults_dict = self.get_parameters_defaults()

    def get_name(self):
        return U

    def get_parameters_names(self):
        return ["m[0][0]", "m[0][1]", "m[1][0]", "m[1][1]"]

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
