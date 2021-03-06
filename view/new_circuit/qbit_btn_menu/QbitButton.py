import wx

from util.Utils import newScaledImgBitmap
from view.constants import *


class QbitButton(wx.Button):
    def __init__(self, parent,  index, qbitMenu, gate_mediator, quantumComputer):
        wx.Button.__init__(self, parent= parent, size=(GATE_SIZE, GATE_SIZE))
        self.quantumComputer = quantumComputer
        self.__gate_mediator = gate_mediator
        self.value = quantumComputer.qbit_value_at(index)
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
        self.quantumComputer.swap_qbit_value_at(self.index)
        self.__gate_mediator.register_changed()

    def setValueView(self):
        self.SetBitmap(newScaledImgBitmap(KET_0 if self.value == 0 else KET_1, (GATE_SIZE, GATE_SIZE)))
