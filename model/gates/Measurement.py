from model.constants import MEASURE
from model.gates.Gate import Gate
import numpy as np


class MeasurementGate(Gate):

    def get_name(self):
        return MEASURE

    def qutip_object(self):

        raise Exception("No qutip object")