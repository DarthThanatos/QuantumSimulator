import wx

class ConnectionPoint:
    def __init__(self, isIn, gateTile, radius):
        self.rect = None
        self.isIn = isIn
        self.gateTile = gateTile
        self.radius = radius
        self.cord = None
        self.initRect()
        self.ij = self.initIJ()

    def filled(self):
        return self.cord is not None

    def initIJ(self):
        cs = self.gateTile.circuitSlot
        i, j = cs.i, cs.j
        return (i,j) if self.isIn else (i, j+1)

    def initRect(self):
        gx, gy = self.gateTile.circuitSlot.rect.GetPosition()
        gw, gh = self.gateTile.circuitSlot.rect.GetSize()
        w = h = 4 * self.radius
        x = gx - w/2 if self.isIn else gx + gw - w/2
        y = gy + gh/2 - h/2
        self.rect = wx.Rect2D(x,y,w,h)

    def drawConnectionPoint(self, dc):
        self.initRect()
        self.ij = self.initIJ()
        dc.SetPen(wx.Pen(wx.BLUE))
        dc.DrawRectangle(*self.rect.GetPosition(), *self.rect.GetSize())