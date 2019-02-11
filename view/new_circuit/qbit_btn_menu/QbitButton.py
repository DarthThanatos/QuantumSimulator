import wx
from view.new_circuit.constants import *
from util.Utils import newScaledImgBitmap

class QbitButton(wx.Button):
    def __init__(self, parent,  index, qbitMenu, quantumComputer):
        wx.Button.__init__(self, parent= parent, size=(GATE_SIZE, GATE_SIZE))
        self.quantumComputer = quantumComputer
        self.value = quantumComputer.qbitValueAt(index)
        self.index = index
        self.qbitMenu = qbitMenu
        self.setValueView()
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Bind(wx.EVT_ENTER_WINDOW, self.onMouseHover)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)

    def onMouseHover(self, ev):
        self.qbitMenu.onMouseHoverOnQbit()

    def onMouseLeave(self, ev):
        self.qbitMenu.onMouseLeaveQbit()

    def onClick(self, ev):
        self.quantumComputer.swapQbitValueAt(self.index)
        self.GetParent().resetView()

    def setValueView(self):
        self.SetBitmap(newScaledImgBitmap(KET_0 if self.value == 0 else KET_1, (GATE_SIZE, GATE_SIZE)))
