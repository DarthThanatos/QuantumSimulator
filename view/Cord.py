import wx
from networkx import dijkstra_path

class Cord:
    def __init__(self, conn_in_row, conn_in_column, circuit):
        self.connectionPointIn = None
        self.connectionPointOut = None
        self.conn_in_row = conn_in_row
        self.conn_in_column = conn_in_column
        self.circuit = circuit
        self.cordPath = []

    def removeSelf(self):
        if self.connectionPointIn is not None:
            self.connectionPointIn.cord = None
        if self.connectionPointOut is not None:
            self.connectionPointOut.cord = None


    def drawCord(self, dc, meshGraph, outIJ = None, isSelected = False):
        if outIJ is None and self.connectionPointOut is None: return
        outIJ = self.connectionPointOut.ij if outIJ is None else outIJ

        pen = dc.GetPen()
        if isSelected: dc.SetPen(wx.Pen(wx.Colour(127,99,71), 3))

        in_i, in_j = self.connectionPointIn.ij
        out_i, out_j = outIJ
        inId=in_i * self.conn_in_row + in_j
        outId=out_i * self.conn_in_row + out_j
        cordPath = dijkstra_path(meshGraph,inId, outId)
        w,h = self.circuit.GetClientSize()
        g_w, g_h = w / self.circuit.CONNECTIONS_IN_ROW, h/self.circuit.CONNECTIONS_IN_COLUMN
        for k, nodeId in enumerate(cordPath):
            if k < len(cordPath) - 1:
                start_i, start_j = int(nodeId / self.conn_in_row), int(nodeId % self.conn_in_row)
                end_i, end_j = int(cordPath[k+1] / self.conn_in_row), int(cordPath[k+1] % self.conn_in_row)
                start_x, start_y = start_j * g_w, start_i * g_h + g_h
                end_x, end_y = end_j * g_w, end_i * g_h + g_h
                dc.DrawLine(start_x, start_y, end_x, end_y)
        self.cordPath = cordPath
        dc.SetPen(pen)

    def clickedOnCord(self, m_x, m_y):
        w,h = self.circuit.GetClientSize()
        g_w, g_h = w / self.circuit.CONNECTIONS_IN_ROW, h/self.circuit.CONNECTIONS_IN_COLUMN
        for meshPointId in self.cordPath:
            i, j = int(meshPointId / self.conn_in_row), int(meshPointId % self.conn_in_row)
            x, y = j * g_w, i * g_h + g_h
            if abs(m_x - x) < self.circuit.POINT_RADIUS + self.circuit.POINT_MISS_DIST:
                if abs(m_y - y) < self.circuit.POINT_RADIUS + self.circuit.POINT_MISS_DIST:
                    return True
        return False