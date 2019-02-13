from model.gates.Gate import Gate

class Rotation(Gate):

    def _get_parameters_types(self):
        return [float]
