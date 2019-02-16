
from math import pi

from util.Utils import flatten_dicts


class Gate:

    def __init__(self, qbit, parameters = None):
        self._parameters = parameters if parameters is not None else {}
        self._qbit = qbit

    def set_target(self, qbit):
        self._qbit = qbit

    def parameters(self):
        return dict(self._parameters)

    def target(self):
        return self._qbit

    def qutip_object(self):
        raise Exception("No qutip object")

    def get_parameters_names(self):
        return []

    def get_parameter_default(self, parameter_name):
        raise Exception("no parameter default")

    def _get_parameters_types(self):
        # returns functions that convert a string to the appropriate type
        return {}

    def _map_names_to_values(self, values):
        return flatten_dicts(map(lambda n_t: {n_t[0] : n_t[1]}, zip(self.get_parameters_names(), values)))

    def is_parameter_correct(self, name, value):
        try:
            self._get_parameters_types()[name](eval(value))
            return True
        except Exception:
            return False

    def why_is_parameter_incorrect(self, name, value):
        try:
            self._get_parameters_types()[name](eval(value))
            return ""
        except Exception as e:
            return str(e)

    def are_parameters_correct(self, kwargs):
        # kwargs: dict of {arg_name: arg_value}
        def map_correct(item):
            arg_name, arg_val = item
            try:
                self._get_parameters_types()[arg_name](eval(arg_val))
                return True
            except Exception:
                return False
        bools = list(map(map_correct, kwargs.items()))
        incorrect_params = list(filter(lambda correct: not correct, bools))
        return incorrect_params == []

    def is_gate_correct(self, kwargs):
        return self.are_parameters_correct(kwargs)

    def why_gate_not_correct(self, kwargs):
        incorrect = not self.are_parameters_correct(kwargs)
        error_msg = "Parameters incorrect, please correct them." if incorrect else ""
        return error_msg

    def get_name(self):
        raise Exception("No name")

    def set_parameter_value(self, name, value):
        if name not in self.get_parameters_names():
            return
        type_convertion = self._get_parameters_types()[name]
        self._parameters[name] = type_convertion(eval(value))

    def __str__(self):
        return str(self.get_name()) + " with target qubit at: " + str(self._qbit)

    def transform_vector(self, vector):
        raise Exception("no transformation")