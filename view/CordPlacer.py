from view.Cord import Cord


class CordPlacer:

    def __init__(self, circuit, conn_in_row, conn_in_col, pointRad, point_miss_dist):
        self.circuit = circuit
        self.CONNECTIONS_IN_ROW = conn_in_row
        self.CONNECTIONS_IN_COLUMN = conn_in_col
        self.POINT_RADIUS = pointRad
        self.POINT_MISS_DIST = point_miss_dist
        self.currentCord = Cord(self.CONNECTIONS_IN_ROW, self.CONNECTIONS_IN_COLUMN, self)
        self.cords = []
        self.selectedStartConnectionPoint = None
        self.currentUnfinishedCordMeshIJ = None

    def unselectCord(self):
        self.currentCord.connectionPointIn = None

    def placeCord(self, gates, m_x, m_y):
        for gate in gates:
            if gate.outputClicked(m_x, m_y):
                if self.currentCord.connectionPointIn is None:
                    self.createNewGatesConnection(gate)
            if gate.inputClicked(m_x, m_y):
                if self.currentCord.connectionPointIn is not None:
                    if self.currentCord.connectionPointOut is None:
                        self.endGatesConnection(gate)
                break

    def createNewGatesConnection(self, gate):
        if not gate.connectionPointOut.filled():
            self.selectedStartConnectionPoint = gate.connectionPointOut
            self.currentCord.connectionPointIn = gate.connectionPointOut

    def endGatesConnection(self, gate):
        if not gate.connectionPointIn.filled():
            self.currentCord.connectionPointOut = gate.connectionPointIn
            gate.connectionPointIn.cord = self.currentCord
            self.selectedStartConnectionPoint.cord = self.currentCord
            self.cords.append(self.currentCord)
            self.currentCord = Cord(self.CONNECTIONS_IN_ROW, self.CONNECTIONS_IN_COLUMN, self)


    def GetClientSize(self):
        return self.circuit.GetClientSize()

    def moveCord(self,event):
        if self.currentCord.connectionPointIn is not None:
            w,h = self.GetClientSize()
            m_x, m_y = event.GetPosition()
            for i in range(self.CONNECTIONS_IN_COLUMN):
                for j in range(self.CONNECTIONS_IN_ROW):
                    x = w / self.CONNECTIONS_IN_ROW * j
                    y = h / self.CONNECTIONS_IN_COLUMN * i
                    g_h = h / self.CONNECTIONS_IN_COLUMN
                    if abs(m_x - x) < self.POINT_RADIUS + self.POINT_MISS_DIST:
                        if abs(m_y - (y + g_h)) < self.POINT_RADIUS + self.POINT_MISS_DIST:
                            self.currentUnfinishedCordMeshIJ = (i, j)
                            break

    def draw_unfinished_cord(self, dc, meshGraph):
        if self.currentCord.connectionPointIn is not None:
            self.currentCord.drawCord(dc, meshGraph, self.currentUnfinishedCordMeshIJ)

    def drawCords(self, dc, meshGraph):
        for cord in self.cords:
            cord.drawCord(dc, meshGraph, isSelected=cord == self.circuit.selectedCord)

    def removeCord(self, cord):
        if cord is None:
            return
        cord.removeSelf()
        self.cords.remove(cord)

    def removeSelectedCord(self):
        selectedCord = self.circuit.selectedCord
        if selectedCord is None:
            return
        self.removeCord(selectedCord)
        self.circuit.selectedCord = None

    def detectCordSelection(self, m_x, m_y):
        if self.currentCord.connectionPointIn is None:
            for cord in self.cords:
                if cord.clickedOnCord(m_x, m_y):
                    return cord
        return None
