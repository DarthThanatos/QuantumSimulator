import wx

from view.ConnectionPoint import ConnectionPoint

class GateTile:
    def __init__(self, name, imgPath, circuit):
        self.name = name
        self.imgPath = imgPath
        self.circuitSlot = None
        self.bmp = None
        self.connectionPointIn = None
        self.connectionPointOut = None
        self.circuit = circuit

    def initGateTile(self, circuitSlot, conn_radius):
        self.circuitSlot = circuitSlot
        self.bmp = self.scale_bitmap(
            wx.Bitmap(self.imgPath),
            *circuitSlot.rect.GetSize()
        )
        self.connectionPointIn = \
            ConnectionPoint(True, self, conn_radius)
        self.connectionPointOut = \
            ConnectionPoint(False, self, conn_radius)


    def scale_bitmap(self, bitmap, width, height):
        image = bitmap.ConvertToImage()
        image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        result = wx.Bitmap(image)
        return result

    def removeSelf(self):
        self.circuit.cordPlacer.removeCord(self.connectionPointIn.cord)
        self.circuit.cordPlacer.removeCord(self.connectionPointOut.cord)
        self.circuitSlot.gate = None

    def drawSelectionIndicator(self, dc):
        sgr = self.circuitSlot.rect
        WRAPPING_RECT_OFFSET = 5
        x,y = sgr.GetPosition()
        w,h = sgr.GetSize()
        x -= WRAPPING_RECT_OFFSET
        y -= WRAPPING_RECT_OFFSET
        w += 2 * WRAPPING_RECT_OFFSET
        h += 2 * WRAPPING_RECT_OFFSET
        dc.SetBrush(wx.Brush(wx.GREEN, style=wx.BRUSHSTYLE_TRANSPARENT))
        dc.SetPen(wx.Pen(wx.GREEN))
        dc.DrawRectangle(x,y,w,h)
        dc.SetPen(wx.Pen(wx.RED, style=wx.PENSTYLE_SOLID))

    def drawGate(self, dc):
        x, y = self.circuitSlot.rect.GetPosition()
        dc.DrawBitmap(self.bmp, x, y)
        self.connectionPointIn.drawConnectionPoint(dc)
        self.connectionPointOut.drawConnectionPoint(dc)

    def inputClicked(self, mx, my):
        return self.connectionPointIn.rect.Contains((mx, my))

    def outputClicked(self, mx, my):
        return self.connectionPointOut.rect.Contains((mx, my))