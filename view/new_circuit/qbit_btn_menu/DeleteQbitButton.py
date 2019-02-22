import wx

from util.Utils import newScaledImgBitmap
from view.constants import *


class DeleteQbitButton(wx.Button):

    def __init__(self, parent, index, qbitMenu, gate_mediator, quantumComputer):
        wx.Button.__init__(self, parent, size=(GATE_SIZE, GATE_SIZE))
        self.qbitMenu = qbitMenu
        self.__gate_mediator = gate_mediator
        self.index = index
        self.quantumComputer = quantumComputer
        self.SetBitmap(newScaledImgBitmap("../Images/Circuit/delete.png", (GATE_SIZE, GATE_SIZE)))
        self.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Hide()

    def onMouseLeave(self, ev):
        self.qbitMenu.onMouseLeaveDelete()

    def onClick(self, ev):
        self.quantumComputer.remove_qbit(self.index)
        self.__gate_mediator.register_changed()
