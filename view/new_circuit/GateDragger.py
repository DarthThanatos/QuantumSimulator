import wx

from util.Utils import euclDist
from view.new_circuit.constants import *

class GateDragger:

    DELETE_PROMPT_TRESHOLD = 5

    def __init__(self, circuit, quantumComputer):
        self.movedGateShadow = None
        self.movedShadowStartPos = (0,0)
        self.circuit = circuit
        self.dragging = False
        self.draggedGateTile = None
        self.movedDist = 0
        self.promptedDelete = False
        self.quantumComputer = quantumComputer

    def initDraggingGate(self, event, draggedGateTile):
        if draggedGateTile is not None:
            self.dragging = True
            self.promptedDelete = False
            self.movedDist = 0
            self.movedShadowStartPos = event.GetPosition()
            self.draggedGateTile = draggedGateTile

    def dragGate(self, event):
        if event.Dragging():
            if self.draggedGateTile is None: return
            if not self.movedGateShadow:
                self.movedGateShadow = wx.DragImage(self.draggedGateTile.bmp)
                coords = self.draggedGateTile.rect.GetLeft(), self.draggedGateTile.rect.GetTop()
                self.movedGateShadow.BeginDrag(self.movedShadowStartPos - coords, self.circuit, False)
                self.circuit.shouldStimulate = True
                self.circuit.Refresh()
            self.movedGateShadow.Move(event.GetPosition())
            self.movedGateShadow.Show()
            self.promptDeleteMsg(event)

    def promptDeleteMsg(self, event):
        self.movedDist = euclDist(self.movedShadowStartPos, event.GetPosition())
        if self.movedDist > self.DELETE_PROMPT_TRESHOLD:
            if not self.promptedDelete:
                self.promptedDelete = True
                self.circuit.Refresh()

    def stopDraggingGate(self, mx, my):
        if not self.movedGateShadow:
            return
        self.movedGateShadow.Hide()
        self.movedGateShadow.EndDrag()
        self.movedGateShadow = None
        self.swapSlotsIfPossible(mx, my)
        self.circuit.shouldStimulate = False
        self.dragging = False
        self.circuit.Refresh()


    def swapSlotsIfPossible(self, m_x, m_y):
        i,j = int(m_y / GATE_SIZE), int(m_x / (GATE_SIZE + GATE_H_SPACE))
        if not self.quantumComputer.can_add_gate_at(i, j):
            return
        self.quantumComputer.removeGate(*self.draggedGateTile.ij)
        if m_x >= self.circuit.getW() or m_x < 2 * GATE_SIZE or \
             m_y >= self.circuit.getH(qbitAreaOnly=True) or m_y < 0:
                self.draggedGateTile = None
                self.circuit.resetView()
                return
        self.quantumComputer.add_gate(i, j, self.draggedGateTile.gateName)
        self.draggedGateTile = None
        self.circuit.resetView()
