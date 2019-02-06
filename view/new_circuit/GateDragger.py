import wx

from util.Utils import euclDist


class GateDragger:

    DELETE_PROMPT_TRESHOLD = 5

    def __init__(self, circuit):
        self.movedGateShadow = None
        self.movedShadowStartPos = (0,0)
        self.circuit = circuit
        self.startIJ = None
        self.dragging = False
        self.movedDist = 0
        self.promptedDelete = False

    def initDraggingGate(self, event, selectedGateTile):
        if selectedGateTile is not None:
            self.dragging = True
            self.promptedDelete = False
            self.movedDist = 0
            self.movedShadowStartPos = event.GetPosition()
            self.startIJ = selectedGateTile.ij

    def dragGate(self, event, selectedGateTile):
        if event.Dragging():
            if selectedGateTile is None: return
            if not self.movedGateShadow:
                self.movedGateShadow = wx.DragImage(selectedGateTile.bmp)
                coords = selectedGateTile.rect.GetLeft(), selectedGateTile.rect.GetTop()
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
        self.circuit.swapSlotsIfPossible(mx, my)
        self.circuit.shouldStimulate = False
        self.dragging = False