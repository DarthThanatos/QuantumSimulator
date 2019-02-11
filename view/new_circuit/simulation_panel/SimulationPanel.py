import wx
from util.Utils import newScaledImgBitmap
from view.new_circuit.constants import *

class SimulActionPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel_width = 150
        btn = wx.Button(self, size = (panel_width, 25))
        btn.SetBitmap(newScaledImgBitmap("../Images/Circuit/{}.png".format(self.bmpFile()), (GATE_SIZE, GATE_SIZE)))
        btn.Bind(wx.EVT_BUTTON, self.onclick)

        sizer.Add(btn, 0, wx.CENTER)
        sizer.Add(wx.TextCtrl(self, value=self.shortDesc(), style=wx.TE_READONLY | wx.TE_CENTER | wx.TE_MULTILINE | wx.NO_BORDER | wx.TE_NO_VSCROLL, size=(panel_width, 50)), 0, wx.CENTER)
        self.SetSizer(sizer)

    def shortDesc(self):
        raise Exception("Not implemented")

    def onclick(self, ev):
        self.controlSimulation()

    def controlSimulation(self):
        raise Exception("control simulation not implemented")

    def bmpFile(self):
        raise Exception("bmp path not implemented")


class NextActionPanel(SimulActionPanel):
    def bmpFile(self):
        return "next"

    def shortDesc(self):
        return "Go to next Step"

    def controlSimulation(self):
        print("nb control simul")

class BackActionPanel(SimulActionPanel):
    def bmpFile(self):
        return "back"

    def shortDesc(self):
        return "Break simulation"

    def controlSimulation(self):
        print("back control simul")

class FastForwardActionPanel(SimulActionPanel):
    def bmpFile(self):
        return "fast_forward"

    def shortDesc(self):
        return "Fast forward to the end"

    def controlSimulation(self):
        print("ff control simul")
