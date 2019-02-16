import qutip

from model.constants import IDENTITY
from model.gates.Gate import Gate


class Identity(Gate):

    def qutip_object(self):
        return qutip.identity(2)

    def get_name(self):
        return IDENTITY