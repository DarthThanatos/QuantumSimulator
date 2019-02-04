import wx

class GateMediator:

    def __init__(self):
        self.upperMenu = None
        self.editor = None
        self.inspector = None
        self.frame = None

    def setViews(self, frame, upperMenu, editor, inspector):
        self.upperMenu = upperMenu
        self.editor = editor
        # self.circuit = self.editor.circuit
        self.circuitStd = self.editor.circuitStd
        self.inspector = inspector
        self.frame = frame

    def gateSelected(self, gate):
        # self.circuit.stimula(True, gate)
        self.circuitStd.stimula(True, gate)

    def gateUnselected(self):
        self.frame.SetCursor(wx.NullCursor)
        self.editor.stimula(False)
