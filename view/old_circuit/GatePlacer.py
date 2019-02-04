import wx

from view.old_circuit.GateTile import GateTile


class CircuitSlot:
    def __init__(self, i, j, coords, gate = None):
        self.rect = wx.Rect2D(*coords)
        self.gate = gate
        self.coords = coords
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
            gate.drawGate(dc)

    def coordsToId(self, coords):
        i,j = coords
        return i * self.CONNECTIONS_IN_ROW + j

    def placeGate(self, m_x, m_y,meshGraph, gateMediator):
        if self.gateNameToCreate is not None:
            cs = self.mposToCircuitSlot(m_x, m_y)
            if cs is not None and cs.gate is None:
                self.gates.append(self.newGate(cs))
                meshGraph.remove_edge(self.coordsToId((cs.i,cs.j)), self.coordsToId((cs.i, cs.j+1)))
                gateMediator.gateUnselected()

    def mposToCircuitSlot(self, mx, my):
        for i in range(self.circuitSlots.__len__()):
            for j in range(self.circuitSlots[i].__len__()):
                cs = self.circuitSlots[i][j]
                if cs.rect.Contains((mx, my)):
                    return cs
        return None

    def exchangeSlotsIfPossibleOnSelected(self, mx, my):
        cs = self.mposToCircuitSlot(mx, my)
        if cs is None:
            return
        if cs.gate is not None:
            return
        if self.circuit.selectedGate is None:
            return

        prev_cs = self.circuit.selectedGate.circuitSlot
        prev_cs.gate = None
        cs.gate = self.circuit.selectedGate
        self.circuit.selectedGate.circuitSlot = cs

        meshGraph = self.circuit.meshPlacer.meshGraph
        meshGraph.add_edge(self.coordsToId((prev_cs.i, prev_cs.j)), self.coordsToId((prev_cs.i, prev_cs.j + 1)))
        meshGraph.remove_edge(self.coordsToId((cs.i, cs.j)), self.coordsToId((cs.i, cs.j + 1)))

    def newGate(self, circuitSlot):
        gateTile = \
        GateTile(
            self.gateNameToCreate,
            '../Images/Palette/{}.png'.format(self.gateNameToCreate),
             self.circuit
        )
        gateTile.initGateTile(circuitSlot, self.POINT_RADIUS)
        circuitSlot.gate = gateTile
        return gateTile

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

    def detectGateSelection(self, mx, my):
        for gate in self.gates:
            if gate.circuitSlot.rect.Contains((mx,my)): return gate
        return None

    def removeSelectedGate(self):
        selectedGate = self.circuit.selectedGate
        if selectedGate is None:
            return
        selectedGate.removeSelf()
        self.gates.remove(selectedGate)
        self.circuit.selectedGate = None
