import wx

from wx.lib.scrolledpanel import ScrolledPanel

from model.QuantumComputer import QuantumComputer
from util.Utils import newIconButton
from view.new_circuit.GateDragger import GateDragger
from view.new_circuit.GatePlacer import GatePlacer
from view.new_circuit.MultiqbitGatePlacer import MultiqbitGatePlacer
from view.new_circuit.SingleGateTile import SingleGateTile

from view.new_circuit.constants import *
from view.new_circuit.qbit_btn_menu.DeleteQbitButton import DeleteQbitButton
from view.new_circuit.qbit_btn_menu.QbitButton import QbitButton
from view.new_circuit.qbit_btn_menu.QbitMenu import QbitMenu
from view.new_circuit.simulation_panel.SimulationPanel import BackActionPanel, NextActionPanel, FastForwardActionPanel


class CircuitPanel(wx.Panel):

    def __init__(self, parent, nqubits, gateMediator):
        size = (self.getW(), self.getH())
        wx.Panel.__init__(self, parent, size=size)

        self.quantumComputer = QuantumComputer(nqbits=nqubits)
        self.shouldStimulate = False
        self.filled_slots = {} # (i,j) => gateTile
        self.flattened_multigates = {}  # {(ctrl1, j1) -> (name_1, target_i_1), (ctrl2, j2) -> (name_2, target_i_2)...}
        self.gateDragger = GateDragger(self, self.quantumComputer)
        self.multiqbitPlacer = MultiqbitGatePlacer(self, self.quantumComputer)
        self.gatePlacer = GatePlacer(self, gateMediator, self.quantumComputer)
        self.gateName = None
        self.showDeleteMsg = False
        self.gateMediator = gateMediator

        self.rootSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.rootSizer.Add(self.new_QbitsReg())
        self.SetSizer(self.rootSizer)

        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetBackgroundColour(wx.WHITE)
        self.bindEvs()

    def bindEvs(self):
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_click)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.Bind(wx.EVT_LEFT_UP, self.on_endclick)
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_doubleclick)
        self.Bind(wx.EVT_RIGHT_UP, self.on_right_click)

    def on_right_click(self, ev):
        self.multiqbitPlacer.cancel_drawing_control_line()

    def on_doubleclick(self, event):
        self.multiqbitPlacer.place_control_bit(*event.GetPosition(), self.filled_slots)

    def on_left_click(self, event):
        m_x, m_y = event.GetPosition()
        if self.gateName is not None:
            self.gatePlacer.placeGate(m_x,m_y)
        selectedGateTile = self.detectGateSelection(m_x, m_y)
        if selectedGateTile is not None:
            self.gateDragger.initDraggingGate(event, selectedGateTile)
        self.multiqbitPlacer.place_target(*event.GetPosition())
        self.Refresh()

    def on_mouse_move(self, event):
        self.gateDragger.dragGate(event)
        self.multiqbitPlacer.update_control_line(event)

    def on_endclick(self, event):
        self.gateDragger.stopDraggingGate(*event.GetPosition())

    def detectGateSelection(self, m_x, m_y):
        i,j = int(m_y / GATE_SIZE), int(m_x / (GATE_SIZE + GATE_H_SPACE))
        if (i, j) in self.filled_slots:
            return self.filled_slots[(i,j)]
        return None

    def resetView(self):
        self.Freeze()
        self.DestroyChildren()
        self.rootSizer.Clear()
        self.rootSizer.Add(self.new_QbitsReg())
        self.rootSizer.Layout()
        self.multiqbitPlacer.cancel_drawing_control_line()
        self.filled_slots = self.gridToGateTiles()
        self.flattened_multigates = self.quantumComputer.flattenedMultiGates()
        self.Refresh()
        self.Thaw()

    def gridToGateTiles(self):
        flattenedGrid = self.quantumComputer.flattenedGrid()
        return {(i,j): SingleGateTile(i, j, flattenedGrid[(i,j)]) for (i,j) in flattenedGrid}

    def new_QbitsReg(self):
        qbitRegSizer = wx.BoxSizer(wx.VERTICAL)
        for i in range(self.quantumComputer.register.nqubits):
            qbitRegSizer.Add(self.newQbitRow(i))
        qbitRegSizer.Add(self.newAddQbitRow())
        return qbitRegSizer

    def newAddQbitRow(self):
        addbtnsizer = wx.BoxSizer(wx.HORIZONTAL)
        addbtnsizer.AddSpacer(GATE_SIZE)
        addbtnsizer.Add(self.newAddQbitBtn())
        return addbtnsizer

    def newQbitRow(self, i):
        qbitHorizontalBox = wx.GridSizer(3)
        qbitHorizontalBox.Add(self.newQbitLabel(i), 0, wx.CENTER)
        qbitMenu = QbitMenu()
        delBtn = DeleteQbitButton(self, i, qbitMenu, self.quantumComputer)
        qbtn = QbitButton(self, i, qbitMenu, self.quantumComputer)
        qbitMenu.setViews(qbtn, delBtn, qbitHorizontalBox)
        qbitHorizontalBox.Add(qbtn)
        qbitHorizontalBox.Add(delBtn)
        return qbitHorizontalBox

    def newQbitLabel(self, i):
        return wx.StaticText(self, label="q[{}]".format(i), size=(GATE_SIZE, GATE_SIZE), style=wx.ALIGN_CENTRE)

    def newAddQbitBtn(self):
        return newIconButton(
            parent = self,
            size=(GATE_SIZE, GATE_SIZE),
            icon_path="../Images/Circuit/add.png",
            on_click=self.onAddQbit
        )

    def onAddQbit(self, ev):
        self.quantumComputer.addQbit()
        self.resetView()

    def getW(self):
        return (MAX_COLUMNS + 2) * GATE_SIZE + MAX_COLUMNS * GATE_H_SPACE

    def getH(self, qbitAreaOnly = False):
        return MAX_ROWS * GATE_SIZE if not qbitAreaOnly else self.quantumComputer.register.nqubits * GATE_SIZE

    def on_paint(self, ev):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        self.drawCords(dc)
        self.drawStimula(dc)
        self.multiqbitPlacer.draw_control_line(dc)
        self.multiqbitPlacer.draw_multiqubit_gates(dc, self.flattened_multigates)
        self.drawGates(dc)
        if self.gateDragger.dragging:
            self.drawDeleteMsg(dc)
        del dc  # so that it is deallocated and we can create a new configuration below
        self.drawSimulationMark()

    def ij_to_xy(self, i, j):
        x = GATE_SIZE * j + GATE_SIZE/2 + j * GATE_H_SPACE
        y = GATE_SIZE * i + GATE_SIZE/2
        return x,y

    def drawStimula(self, dc):
        if not self.shouldStimulate: return
        dc.SetPen(wx.Pen(wx.BLUE))
        for i in range(self.quantumComputer.register.nqubits):
            for j in range(2, MAX_COLUMNS + 2):
                if self.quantumComputer.can_add_gate_at(i, j):
                    x,y = self.ij_to_xy(i, j)
                    dc.DrawCircle(x, y, 3)

    def drawCords(self, dc):
        for i in range(self.quantumComputer.register.nqubits):
            middle = GATE_SIZE * i + GATE_SIZE/2
            dc.DrawLine(2*GATE_SIZE, middle, self.getW(), middle)

    def drawGates(self, dc):
        dc.SetBrush(wx.Brush(wx.WHITE))
        for gateTile in self.filled_slots.values():
            gateTile.drawSelf(dc)

    def drawSimulationMark(self):
        dc = wx.GCDC(wx.PaintDC(self))
        dc.SetBrush(wx.Brush(wx.Colour(255, 255, 255, 200)))
        dc.SetPen(wx.Pen(wx.WHITE))
        dc.DrawRectangle(0, 0, 200, 200)

    def drawDeleteMsg(self, dc):
        if self.gateDragger.movedDist < self.gateDragger.DELETE_PROMPT_TRESHOLD: return
        x = self.GetParent().GetScrollPos(wx.HORIZONTAL) * self.GetParent().GetScrollPixelsPerUnit()[0]
        x += self.GetParent().GetSize()[0]/2
        y = self.getH(qbitAreaOnly=True)
        dc.DrawTextList("Drop here to delete this gate", [(x, y)], [wx.BLUE])

    def stimula(self, shouldStimulate, gateName=None):
        self.gateName = gateName
        self.shouldStimulate = shouldStimulate
        self.Refresh()

class CircuitStd(wx.Panel):

    def __init__(self, parent, gateMediator):
        wx.Panel.__init__(self, parent)
        self.gateMediator = gateMediator
        self.shouldStimulate = False
        rootSizer = wx.BoxSizer(wx.VERTICAL)
        rootSizer.AddSpacer(30)
        rootSizer.Add(self.newSimulationActionPanels(), 0, wx.CENTER)
        rootSizer.AddSpacer(30)
        rootSizer.Add(self.newCircuitScroll())
        self.SetSizer(rootSizer)

    def newCircuitScroll(self):
        circuitScroll = ScrolledPanel(self, size=(1500, 700))
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.circuitPanel = CircuitPanel(circuitScroll, 5, self.gateMediator)
        vbox.Add(self.circuitPanel)
        circuitScroll.SetSizer(vbox)
        circuitScroll.SetupScrolling()
        return circuitScroll

    def newSimulationActionPanels(self):
        simulSizer = wx.BoxSizer(wx.HORIZONTAL)
        simulSizer.Add(BackActionPanel(self))
        simulSizer.AddSpacer(20)
        simulSizer.Add(NextActionPanel(self))
        simulSizer.AddSpacer(20)
        simulSizer.Add(FastForwardActionPanel(self))
        return simulSizer

    def stimula(self, shouldStimulate, gateName=None):
        self.circuitPanel.stimula(shouldStimulate, gateName)