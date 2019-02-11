from view.new_circuit.constants import *
import wx
from util.Utils import newScaledImgBitmap

class SingleGateTile:
    def __init__(self, i, j, gateName):
        self.rect = wx.Rect2D(j * (GATE_SIZE + GATE_H_SPACE), i * GATE_SIZE, GATE_SIZE, GATE_SIZE)
        self.gateName = gateName
        self.ij = (i, j)
        self.bmp = newScaledImgBitmap('../Images/Palette/{}.png'.format(self.gateName), (GATE_SIZE, GATE_SIZE))

    def drawSelf(self, dc):
        x, y = self.rect.GetLeft(), self.rect.GetTop()
        dc.DrawRectangle(*self.rect.GetPosition(), *self.rect.GetSize())
        dc.DrawBitmap(self.bmp, x, y)

    def removeSelf(self, filledSlots):
        filledSlots.__delitem__(self.ij)
