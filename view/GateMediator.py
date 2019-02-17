import wx

class GateMediator:

    def __init__(self):
        self.__circuit_inspector = None
        self.__circuit_view = None
        self.__frame = None
        self.__bloch_canvas = None

    def set_bloch_canvas(self, bloch_canvas):
        self.__bloch_canvas = bloch_canvas

    def set_circuit_inspector(self, circuit_inspector):
        self.__circuit_inspector = circuit_inspector

    def set_frame(self, frame):
        self.__frame = frame

    def set_circuit_view(self, circuit_view):
        self.__circuit_view = circuit_view

    def gateSelected(self, gate):
        # self.circuit.stimula(True, gate)
        self.__circuit_view.stimula(True, gate)

    def gateUnselected(self):
        self.__frame.SetCursor(wx.NullCursor)
        self.__circuit_view.stimula(False)

    def register_changed(self):
        self.__circuit_inspector.reset_view()
        self.__circuit_view.resetView()
        self.__bloch_canvas.reset_view()
