import wx

from view.GateTile import GateTile


class CircuitSlot:
    def __init__(self, i, j, coords, gate = None):
        self.rect = wx.Rect2D(*coords)
        self.gate = gate
        self.i = i
        self.j = j

    def drawStimula(self, dc):
        if self.gate is None:
            dc.DrawRectangle(*self.rect.GetPosition(), *self.rect.GetSize())


class GatePlacer:

    def __init__(self, circuit, conn_in_row, conn_in_column, pointRad, point_miss_dist):
        self.circuit = circuit
        self.CONNECTIONS_IN_ROW = conn_in_row
        self.CONNECTIONS_IN_COLUMN = conn_in_column
        self.gateNameToCreate = None
        self.POINT_RADIUS = pointRad
        self.POINT_MISS_DIST = point_miss_dist
        self.gates = []
        self.circuitSlots = []

    def GetClientSize(self):
        return self.circuit.GetClientSize()

    def drawGates(self, dc):
        for gate in self.gates:
            dc.DrawBitmap(gate.bmp, gate.coords[0], gate.coords[1])
            if gate.filled[0]:
                x = gate.inOutIds[0][1] * self.GetClientSize()[0] / self.CONNECTIONS_IN_ROW
                y = gate.inOutIds[0][0] * self.GetClientSize()[1] / self.CONNECTIONS_IN_COLUMN
                g_h = self.GetClientSize()[1] / self.CONNECTIONS_IN_COLUMN
                dc.SetPen(wx.Pen(wx.BLUE))
                dc.DrawCircle(x, y+ g_h, self.POINT_RADIUS)
            if gate.filled[1]:
                x = gate.inOutIds[1][1] * self.GetClientSize()[0] / self.CONNECTIONS_IN_ROW
                y = gate.inOutIds[1][0] * self.GetClientSize()[1] / self.CONNECTIONS_IN_COLUMN
                g_h = self.GetClientSize()[1] / self.CONNECTIONS_IN_COLUMN
                dc.SetPen(wx.Pen(wx.BLUE))
                dc.DrawCircle(x, y + g_h, self.POINT_RADIUS)

    def coordsToId(self, coords):
        i,j = coords
        return i * self.CONNECTIONS_IN_ROW + j

    def placeGate(self, m_x, m_y, w, h, meshGraph, gateMediator):
        for i in range(self.CONNECTIONS_IN_COLUMN):
            for j in range(self.CONNECTIONS_IN_ROW):
                x = w / self.CONNECTIONS_IN_ROW * j
                y = h / self.CONNECTIONS_IN_COLUMN * i
                if abs(m_x - x) < w / self.CONNECTIONS_IN_ROW:
                    if abs(m_y - y) < h / self.CONNECTIONS_IN_COLUMN:
                        if self.gateNameToCreate is not None:
                            if not self.collisionExists(m_x, m_y):
                                gate_w, gate_h = w / self.CONNECTIONS_IN_ROW, h / self.CONNECTIONS_IN_COLUMN
                                self.gates.append(
                                    GateTile(
                                        self.gateNameToCreate,
                                        '../Images/Palette/{}.png'.format(self.gateNameToCreate),
                                        [(i, j), (i, j + 1)],
                                        (x, y + gate_h / 2, gate_w, gate_h)
                                    )
                                )
                                meshGraph.remove_edge(self.coordsToId((i,j)), self.coordsToId((i, j+1)))
                                gateMediator.gateUnselected()
                                break

    def collisionExists(self, m_x, m_y):
        for gate in self.gates:
            if gate.collides(m_x, m_y): return True
        return False

    def initCircuitSlots(self):
        w, h = self.GetClientSize()
        s_w =  w/ self.CONNECTIONS_IN_ROW
        s_h = h/self.CONNECTIONS_IN_COLUMN
        for i in range(self.CONNECTIONS_IN_COLUMN):
            self.circuitSlots.append([])
            for j in range(self.CONNECTIONS_IN_ROW):
                x = w / self.CONNECTIONS_IN_ROW * j
                y = h / self.CONNECTIONS_IN_COLUMN * i
                circuitSlot = CircuitSlot(i, j, (x, y + s_h/2, s_w, s_h))
                self.circuitSlots[i].append(circuitSlot)


    def drawGateStimula(self, dc):
        if self.circuitSlots == []:
            self.initCircuitSlots()
        dc.SetPen(wx.Pen(wx.YELLOW))
        for i in range(self.CONNECTIONS_IN_COLUMN):
             for j in range(self.CONNECTIONS_IN_ROW):
                self.circuitSlots[i][j].drawStimula(dc)


        # w, h = self.GetClientSize()
        # g_w =  w/ self.CONNECTIONS_IN_ROW
        # g_h = h/self.CONNECTIONS_IN_COLUMN
        # for i in range(self.CONNECTIONS_IN_COLUMN):
        #     for j in range(self.CONNECTIONS_IN_ROW):
        #         x = w / self.CONNECTIONS_IN_ROW * j
        #         y = h / self.CONNECTIONS_IN_COLUMN * i
        #         dc.DrawRectangle(x,y + g_h/2, g_w, g_h)