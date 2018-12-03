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
                self.movedGateShadow.BeginDrag(self.movedShadowStartPos - selectedGate.coords[:2], self.circuit, False)
            self.movedGateShadow.Move(event.GetPosition())
            self.movedGateShadow.Show()