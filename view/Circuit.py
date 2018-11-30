import wx

class Circuit(wx.Panel):
    CONNECTIONS_IN_ROW = 50
    CONNECTIONS_IN_COLUMN = 30
    POINT_RADIUS = 2
    POINT_MISS_DIST = 4 #distance from the border of a point at which point is considered not selected

    def __init__(self, parent, editor):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_UP, self.on_click)
        self.Bind(wx.EVT_RIGHT_UP, self.on_rclick)
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_dclick)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.editor = editor
        self.cord_start_point = None
        self.current_gate = None

    def on_rclick(self, event):
        self.cord_start_point = None
        self.current_gate = None
        self.Refresh()

    def on_size(self, event):
        event.Skip()
        self.Refresh()

    def on_mouse_move(self, event):
        if self.cord_start_point is not None:
            self.Refresh()

    def on_dclick(self, event):
        w, h = self.GetClientSize()
        m_x, m_y = event.GetPosition()
        for i in range(self.CONNECTIONS_IN_COLUMN):
            for j in range(self.CONNECTIONS_IN_ROW):
                x = w / self.CONNECTIONS_IN_ROW * j
                y = h / self.CONNECTIONS_IN_COLUMN * i
                if abs(m_x - x) < self.POINT_RADIUS + self.POINT_MISS_DIST:
                    if abs(m_y - y) < self.POINT_RADIUS + self.POINT_MISS_DIST:
                        self.cord_start_point = (x,y)
                        break

    def on_click(self, event):
        w, h = self.GetClientSize()
        m_x, m_y = event.GetPosition()
        for i in range(self.CONNECTIONS_IN_COLUMN):
            for j in range(self.CONNECTIONS_IN_ROW):
                x = w / self.CONNECTIONS_IN_ROW * j
                y = h / self.CONNECTIONS_IN_COLUMN * i
                if abs(m_x - x) < self.POINT_RADIUS + self.POINT_MISS_DIST:
                    if abs(m_y - y) < self.POINT_RADIUS + self.POINT_MISS_DIST:
                        self.cord_start_point = (x, y)
                        break

    def draw_unfinished_cord(self, dc):
        if self.cord_start_point is not None:
            # w, h = self.GetClientSize()
            end_coord = self.ScreenToClient(wx.GetMousePosition())
            dc.DrawLine(self.cord_start_point[0], self.cord_start_point[1], end_coord[0], end_coord[1])

    def on_paint(self, event):
        w, h = self.GetClientSize()
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        self.draw_mesh_points(dc, w, h)
        self.draw_unfinished_cord(dc)

    def draw_mesh_points(self, dc, w, h):
        dc.SetPen(wx.Pen(wx.RED, width = 1))
        for i in range(self.CONNECTIONS_IN_COLUMN):
            for j in range(self.CONNECTIONS_IN_ROW):
                x = w / self.CONNECTIONS_IN_ROW * j
                y = h / self.CONNECTIONS_IN_COLUMN * i
                dc.DrawCircle(x, y, self.POINT_RADIUS)