import wx

class GateDragger:

    def __init__(self, circuit):
        self.movedGateShadow = None
        self.movedShadowStartPos = (0,0)
        self.circuit = circuit

    def initDraggingGate(self, event, selectedGate):
        if selectedGate is not None:
            self.movedShadowStartPos = event.GetPosition()


    def dragGate(self, event, selectedGate):
        if event.Dragging():
            if selectedGate is None: return
            if not self.movedGateShadow:
                self.movedGateShadow = wx.DragImage(selectedGate.bmp)
                self.movedGateShadow.BeginDrag(self.movedShadowStartPos - selectedGate.circuitSlot.coords[:2], self.circuit, False)
                self.circuit.shouldStimulate = True
            self.movedGateShadow.Move(event.GetPosition())
            self.movedGateShadow.Show()

    def stopDraggingGate(self, mx, my):
        if not self.movedGateShadow:
            return
        self.movedGateShadow.Hide()
        self.movedGateShadow.EndDrag()
        self.movedGateShadow = None
        self.circuit.gatePlacer.swapSlotsIfPossible(mx, my)
        self.circuit.shouldStimulate = False