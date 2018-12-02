import wx
from networkx import Graph
from networkx import dijkstra_path

class GateTile:
    def __init__(self, name, imgPath, inOutIds, coords=None):
        self.name = name
        self.imgPath = imgPath
        self.bmp = self.scale_bitmap(wx.Bitmap(self.imgPath), coords[2], coords[3])
        self.coords = coords
        self.inOutIds = inOutIds
        self.filled = [True, True]

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
        return self.filled[pinId]


    def scale_bitmap(self, bitmap, width, height):
        image = bitmap.ConvertToImage()
        image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        result = wx.Bitmap(image)
        return result

class Cord:
    def __init__(self, inCoords, outCoords, g_w, g_h, conn_in_row, conn_in_column):
        self.inCoords = inCoords
        self.outCoords = outCoords
        self.g_w, self.g_h = g_w, g_h
        self.conn_in_row = conn_in_row
        self.conn_in_column = conn_in_column

    def drawCord(self, dc, meshGraph):
        if self.outCoords is None: return
        in_i, in_j = self.inCoords
        out_i, out_j = self.outCoords
        inId=in_i * self.conn_in_row + in_j
        outId=out_i * self.conn_in_row + out_j
        cordPath = dijkstra_path(meshGraph,inId, outId)
        for k, nodeId in enumerate(cordPath):
            if k < len(cordPath) - 1:
                start_i, start_j = int(nodeId / self.conn_in_row), int(nodeId % self.conn_in_row)
                end_i, end_j = int(cordPath[k+1] / self.conn_in_row), int(cordPath[k+1] % self.conn_in_row)
                start_x, start_y = start_j * self.g_w, start_i * self.g_h + self.g_h
                end_x, end_y = end_j * self.g_w, end_i * self.g_h + self.g_h
                dc.DrawLine(start_x, start_y, end_x, end_y)

class Circuit(wx.Panel):
    CONNECTIONS_IN_ROW = 50
    CONNECTIONS_IN_COLUMN = 30
    POINT_RADIUS = 2
    POINT_MISS_DIST = 4 #distance from the border of a point at which point is considered not selected

    def __init__(self, parent, gateMediator):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_UP, self.on_click)
        self.Bind(wx.EVT_RIGHT_UP, self.on_rclick)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.SetBackgroundColour(wx.WHITE)
        self.shouldStimulate = False
        self.gateMediator = gateMediator
        self.gates = []
        self.cords = []
        self.currentCord = Cord(None, None, *(1393 / 50., 776/30.), self.CONNECTIONS_IN_ROW, self.CONNECTIONS_IN_COLUMN)
        self.gateNameToCreate = None
        self.selectedGate = None
        self.meshGraph = Graph()
        self.initMesh()

    def initMesh(self):
        for i in range(self.CONNECTIONS_IN_COLUMN):
            for j in range(self.CONNECTIONS_IN_ROW):
                meshNodeId = i * self.CONNECTIONS_IN_ROW  + j
                self.meshGraph.add_node(meshNodeId)
                self.meshGraph.add_edge(meshNodeId, (i - 1) * self.CONNECTIONS_IN_ROW  + j)
                self.meshGraph.add_edge(meshNodeId,  i * self.CONNECTIONS_IN_ROW  + j - 1)


    def stimula(self, shouldStimulate, gate=None):
        self.shouldStimulate = shouldStimulate
        self.gateNameToCreate = gate
        self.Refresh()

    def on_rclick(self, event):
        self.currentCord.inCoords = None
        self.gateNameToCreate = None
        self.Refresh()

    def on_size(self, event):
        event.Skip()
        self.Refresh()

    def on_mouse_move(self, event):
        if self.currentCord.inCoords is not None:
            w,h = self.GetClientSize()
            m_x, m_y = event.GetPosition()
            for i in range(self.CONNECTIONS_IN_COLUMN):
                for j in range(self.CONNECTIONS_IN_ROW):
                    x = w / self.CONNECTIONS_IN_ROW * j
                    y = h / self.CONNECTIONS_IN_COLUMN * i
                    g_h = h / self.CONNECTIONS_IN_COLUMN
                    if abs(m_x - x) < self.POINT_RADIUS + self.POINT_MISS_DIST:
                        if abs(m_y - (y + g_h)) < self.POINT_RADIUS + self.POINT_MISS_DIST:
                            if not self.shouldStimulate:
                                self.currentCord.outCoords = (i,j)
                                break
            self.Refresh()

    def on_click(self, event):
        w, h = self.GetClientSize()
        m_x, m_y = event.GetPosition()
        self.placeCord(m_x, m_y, w, h)
        self.placeGate(m_x, m_y, w, h)

    def placeCord(self,m_x, m_y, w, h):
        if not self.shouldStimulate:
            for gate in self.gates:
                if gate.collides(m_x, m_y):
                    if self.currentCord.inCoords is None:
                        if gate.pinFree(m_x):
                            self.selectedGate = gate
                            self.currentCord.inCoords = gate.getInCoords(m_x, m_y)
                    else:
                        if gate.pinFree(m_x):
                            self.currentCord.outCoords = gate.inOutIds[0]
                            self.cords.append(self.currentCord)
                            self.currentCord = Cord(None, None, *(1393 / 50., 776/30.), self.CONNECTIONS_IN_ROW, self.CONNECTIONS_IN_COLUMN)
                            # gate.outFilled = True
                    self.Refresh()
                    break

    def placeGate(self, m_x, m_y, w, h):
        for i in range(self.CONNECTIONS_IN_COLUMN):
            for j in range(self.CONNECTIONS_IN_ROW):
                x = w / self.CONNECTIONS_IN_ROW * j
                y = h / self.CONNECTIONS_IN_COLUMN * i
                if abs(m_x - x) < w / self.CONNECTIONS_IN_ROW:
                    if abs(m_y - y) < h / self.CONNECTIONS_IN_COLUMN:
                        if self.gateNameToCreate is not None:
                            if not self.collisionExists(m_x, m_y):
                                gate_w, gate_h = w / self.CONNECTIONS_IN_ROW, h / self.CONNECTIONS_IN_COLUMN
                                self.gates.append(GateTile(self.gateNameToCreate, '../Images/Palette/{}.png'.format(self.gateNameToCreate), [(i, j), (i, j + 1)], (x, y + gate_h / 2, gate_w, gate_h)))
                                self.gateMediator.gateUnselected()
                                break


    def collisionExists(self, m_x, m_y):
        for gate in self.gates:
            if gate.collides(m_x, m_y): return True
        return False

    def draw_unfinished_cord(self, dc):
        if self.currentCord.inCoords is not None:
            self.currentCord.drawCord(dc, self.meshGraph)

    def on_paint(self, event):
        w, h = self.GetClientSize()
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        if self.shouldStimulate: self.drawGateStimula(dc)
        self.draw_mesh_points(dc, w, h)
        self.draw_unfinished_cord(dc)
        self.drawGates(dc)
        self.drawCords(dc)

    def drawGateStimula(self, dc):
        dc.SetPen(wx.Pen(wx.YELLOW))
        w, h = self.GetClientSize()
        g_w =  w/ self.CONNECTIONS_IN_ROW
        g_h = h/self.CONNECTIONS_IN_COLUMN
        for i in range(self.CONNECTIONS_IN_COLUMN):
            for j in range(self.CONNECTIONS_IN_ROW):
                x = w / self.CONNECTIONS_IN_ROW * j
                y = h / self.CONNECTIONS_IN_COLUMN * i
                dc.DrawRectangle(x,y + g_h/2, g_w, g_h)

    def drawGates(self, dc):
        for gate in self.gates:
            dc.DrawBitmap(gate.bmp, gate.coords[0], gate.coords[1])

    def drawCords(self, dc):
        for cord in self.cords:
            cord.drawCord(dc, self.meshGraph)

    def draw_mesh_points(self, dc, w, h):
        dc.SetPen(wx.Pen(wx.RED, width = 1))
        for i in range(self.CONNECTIONS_IN_COLUMN):
            for j in range(self.CONNECTIONS_IN_ROW):
                x = w / self.CONNECTIONS_IN_ROW * j
                y = h / self.CONNECTIONS_IN_COLUMN * i
                g_h = h / self.CONNECTIONS_IN_COLUMN
                dc.DrawCircle(x, y + g_h, self.POINT_RADIUS)

