import wx
import wx.lib.newevent
from util.Utils import mouse_to_grid_coordinates
from view.ParametersDialog import ParametersDialog, ParameterMediator, APPLY_STYLE
from view.constants import *


class GatePlacer:

    def __init__(self, circuit, gate_mediator, quantum_computer):
        self.__circuit = circuit
        self.__gate_mediator = gate_mediator
        self.__quantum_computer = quantum_computer
        self.__parameters_dialog = None

    def placeGate(self, m_x, m_y):
        if self.__circuit.getW() > m_x > 2 * GATE_SIZE:
            if self.__circuit.getH(qbitAreaOnly=True) > m_y > 0:
                i,j = mouse_to_grid_coordinates(m_x, m_y)
                if self.__quantum_computer.can_add_gate_at(i, j):
                    self.__query_gate_parameters(self.__circuit.gateName, i, j)
        self.__gate_mediator.gateUnselected()
        self.__circuit.resetView()

    def __query_gate_parameters(self, gate_name, i, j):
        gate = self.__quantum_computer.add_gate(i, j, gate_name)
        if len(gate.get_parameters_names()) == 0:
            self.__gate_mediator.circuit_grid_changed()
            return
        dialog = ParametersDialog(
            self.__circuit,
            gate.get_name(),
            gate.get_parameters_names(),
            gate.get_parameters_defaults(),
            ParameterMediator(gate)
        )
        status = dialog.ShowModal()
        if status == wx.OK:
            self.__gate_mediator.circuit_grid_changed()
        else:
            self.__quantum_computer.remove_gate(i, j)
        dialog.Destroy()
