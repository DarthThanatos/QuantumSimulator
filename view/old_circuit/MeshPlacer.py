import wx

from networkx import Graph

class MeshPlacer:

    def __init__(self, conn_in_row, conn_in_col, pointRad):
        self.CONNECTIONS_IN_ROW = conn_in_row
        self.CONNECTIONS_IN_COLUMN = conn_in_col
        self.POINT_RADIUS = pointRad
        self.meshGraph = Graph()
        self.initMesh()

    def initMesh(self):
        for i in range(self.CONNECTIONS_IN_COLUMN):
            for j in range(self.CONNECTIONS_IN_ROW):
                meshNodeId = i * self.CONNECTIONS_IN_ROW  + j
                self.meshGraph.add_node(meshNodeId)
                self.meshGraph.add_edge(meshNodeId, (i - 1) * self.CONNECTIONS_IN_ROW  + j)
                self.meshGraph.add_edge(meshNodeId,  i * self.CONNECTIONS_IN_ROW  + j - 1)

    def draw_mesh_points(self, dc, w, h):
        dc.SetPen(wx.Pen(wx.RED, width = 1))
        for i in range(self.CONNECTIONS_IN_COLUMN):
            for j in range(self.CONNECTIONS_IN_ROW):
                x = w / self.CONNECTIONS_IN_ROW * j
                y = h / self.CONNECTIONS_IN_COLUMN * i
                g_h = h / self.CONNECTIONS_IN_COLUMN
                dc.DrawCircle(x, y + g_h, self.POINT_RADIUS)
