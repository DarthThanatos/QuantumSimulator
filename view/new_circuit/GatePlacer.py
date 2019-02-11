
from view.new_circuit.constants import *

class GatePlacer:

    def __init__(self, circuit, gateMediator, quantumComputer):
        self.circuit = circuit
        self.gateMediator = gateMediator
        self.quantumComputer = quantumComputer

    def placeGate(self, m_x, m_y):
        if self.circuit.getW() > m_x > 2 * GATE_SIZE:
            if self.circuit.getH(qbitAreaOnly=True) > m_y > 0:
                i,j = int(m_y / GATE_SIZE), int(m_x / (GATE_SIZE + GATE_H_SPACE))
                if self.quantumComputer.can_add_gate_at(i,j):
                    self.quantumComputer.addGate(i, j, self.circuit.gateName)
        self.gateMediator.gateUnselected()
        self.circuit.resetView()
