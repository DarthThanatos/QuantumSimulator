from view.Cord import Cord


class CordPlacer:

    def __init__(self, circuit, conn_in_row, conn_in_col, pointRad, point_miss_dist):
        self.circuit = circuit
        self.CONNECTIONS_IN_ROW = conn_in_row
        self.CONNECTIONS_IN_COLUMN = conn_in_col
        self.POINT_RADIUS = pointRad
        self.POINT_MISS_DIST = point_miss_dist
        self.currentCord = Cord(None, None, self.CONNECTIONS_IN_ROW, self.CONNECTIONS_IN_COLUMN, self)
        self.cords = []
        self.selectedGate = None

    def unselectCord(self):
        self.currentCord.inCoords = None

    def placeCord(self, gates, m_x, m_y):
        for gate in gates:
            if gate.collides(m_x, m_y):
                if self.currentCord.inCoords is None:
                    self.createNewGatesConnection(gate)
                else:
                    self.endGatesConnection(gate)
                break

    def createNewGatesConnection(self, gate):
        if not gate.filled[1]:
            self.selectedGate = gate
            self.currentCord.inCoords = gate.inOutIds[1]

    def endGatesConnection(self, gate):
        if not gate.filled[0]:
            self.currentCord.outCoords = gate.inOutIds[0]
            gate.filled[0] = True
            self.selectedGate.filled[1] = True
            self.cords.append(self.currentCord)
            self.currentCord = Cord(None, None, self.CONNECTIONS_IN_ROW, self.CONNECTIONS_IN_COLUMN, self)


    def GetClientSize(self):
        return self.circuit.GetClientSize()

    def moveCord(self,event):
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
                                self.currentCord.outCoords = (i,j)
                                break


    def draw_unfinished_cord(self, dc, meshGraph):
        if self.currentCord.inCoords is not None:
            self.currentCord.drawCord(dc, meshGraph)

    def drawCords(self, dc, meshGraph):
        for cord in self.cords:
            cord.drawCord(dc, meshGraph)