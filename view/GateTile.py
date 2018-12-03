import wx

class GateTile:
    def __init__(self, name, imgPath, inOutIds, coords=None):
        self.name = name
        self.imgPath = imgPath
        self.bmp = self.scale_bitmap(wx.Bitmap(self.imgPath), coords[2], coords[3])
        self.coords = coords
        self.inOutIds = inOutIds #(i,j), (i, j+1)
        self.filled = [False, False]
        self.cordIn = None
        self.cordOut = None

    def collides(self, m_x, m_y):
        g_x, g_y, g_w, g_h = self.coords
        if abs(g_x - m_x) < g_w:
            if abs(g_y - m_y + g_h/2) < g_h:
                return True
        return False

    def getInCoords(self, m_x, m_y):
        g_x, g_y, g_w, g_h = self.coords
        center_x = g_x + g_w / 2
        return self.inOutIds[0] if m_x < center_x else self.inOutIds[1]

    def pinFree(self, m_x):
        g_x, g_y, g_w, g_h = self.coords
        center_x = g_x + g_w / 2
        pinId = 0 if m_x < center_x else 1
        return not self.filled[pinId]


    def scale_bitmap(self, bitmap, width, height):
        image = bitmap.ConvertToImage()
        image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        result = wx.Bitmap(image)
        return result
