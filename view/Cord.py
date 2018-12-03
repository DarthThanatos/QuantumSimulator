
from networkx import dijkstra_path

class Cord:
    def __init__(self, inCoords, outCoords, conn_in_row, conn_in_column, circuit):
        self.inCoords = inCoords
        self.outCoords = outCoords
        self.conn_in_row = conn_in_row
        self.conn_in_column = conn_in_column
        self.circuit = circuit
        self.gateIn = None
        self.gateOut = None

    def drawCord(self, dc, meshGraph):
        if self.outCoords is None: return
        in_i, in_j = self.inCoords
        out_i, out_j = self.outCoords
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
