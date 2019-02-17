import wx
from util.Utils import newScaledImgBitmap
from view.new_circuit.constants import *


class SimulActionPanel(wx.Panel):
    def __init__(self, parent, gate_mediator, quantum_computer):
        wx.Panel.__init__(self, parent)
        self.__gate_mediator = gate_mediator
        self._quantum_computer = quantum_computer
        self.__circuit = None
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel_width = 150
        btn = wx.Button(self, size = (panel_width, 25))
        btn.SetBitmap(newScaledImgBitmap("../Images/Circuit/{}.png".format(self.bmpFile()), (GATE_SIZE, GATE_SIZE)))
        btn.Bind(wx.EVT_BUTTON, self.onclick)

        sizer.Add(btn, 0, wx.CENTER)
        sizer.Add(wx.TextCtrl(self, value=self.shortDesc(), style=wx.TE_READONLY | wx.TE_CENTER | wx.TE_MULTILINE | wx.NO_BORDER | wx.TE_NO_VSCROLL, size=(panel_width, 50)), 0, wx.CENTER)
        self.SetSizer(sizer)

    def set_circuit(self, circuit):
        self.__circuit = circuit

    def shortDesc(self):
        raise Exception("Not implemented")

    def onclick(self, ev):
        self.controlSimulation()
        self.__gate_mediator.register_changed()

    def controlSimulation(self):
        raise Exception("control simulation not implemented")

    def bmpFile(self):
        raise Exception("bmp path not implemented")


class BackActionPanel(SimulActionPanel):
    def bmpFile(self):
        return "back"

    def shortDesc(self):
        return "Step back"

    def controlSimulation(self):
        self._quantum_computer.back_step()


class NextActionPanel(SimulActionPanel):
    def bmpFile(self):
        return "next"

    def shortDesc(self):
        return "Go to next Step"

    def controlSimulation(self):
        self._quantum_computer.next_step()


class FastBackActionPanel(SimulActionPanel):
    def bmpFile(self):
        return "fast_back"

    def shortDesc(self):
        return "Break simulation"

    def controlSimulation(self):
        self._quantum_computer.fast_back()


class FastForwardActionPanel(SimulActionPanel):
    def bmpFile(self):
        return "fast_forward"

    def shortDesc(self):
        return "Fast forward to the end"

    def controlSimulation(self):
        self._quantum_computer.fast_forward()
