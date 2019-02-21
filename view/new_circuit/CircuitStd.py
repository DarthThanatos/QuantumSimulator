import wx

from wx.lib.scrolledpanel import ScrolledPanel

from util.Utils import newIconButton, mouse_to_grid_coordinates
from view.Inspector import CircuitInspector
from view.new_circuit.GateDragger import GateDragger
from view.new_circuit.GatePlacer import GatePlacer
from view.new_circuit.MultiqbitGatePlacer import MultiqbitGatePlacer
from view.new_circuit.SingleGateTile import SingleGateTile

from view.new_circuit.constants import *
from view.new_circuit.qbit_btn_menu.DeleteQbitButton import DeleteQbitButton
from view.new_circuit.qbit_btn_menu.QbitButton import QbitButton
from view.new_circuit.qbit_btn_menu.QbitMenu import QbitMenu
from view.new_circuit.simulation_panel.GenerateCodeButton import GenerateCodeButton
from view.new_circuit.simulation_panel.SimulationPanel import FastBackActionPanel, NextActionPanel, \
    FastForwardActionPanel, BackActionPanel


class CircuitPanel(wx.Panel):

    def __init__(self, parent, quantum_computer, gate_mediator):
        size = (self.getW(), self.getH())
        wx.Panel.__init__(self, parent, size=size)
        self.__gate_mediator = gate_mediator
        gate_mediator.set_circuit_view(self)
        self.__quantum_computer = quantum_computer
        self.shouldStimulate = False
        self.filled_slots = {} # (i,j) => gateTile
        self.flattened_multigates = {}  # {(ctrl1, j1) -> (name_1, target_i_1), (ctrl2, j2) -> (name_2, target_i_2)...}
        self.gateDragger = GateDragger(self, self.__quantum_computer)
        self.multiqbitPlacer = MultiqbitGatePlacer(self, self.__quantum_computer)
        self.gatePlacer = GatePlacer(self, gate_mediator, self.__quantum_computer)
        self.gateName = None
        self.showDeleteMsg = False
        self.gateMediator = gate_mediator
        self.__qbit_register_views = []

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

    def __mouse_inside_simulation_area(self, event):
        m_x, m_y = event.GetPosition()
        _, j = mouse_to_grid_coordinates(m_x, m_y)
        return self.__quantum_computer.step_already_simulated(j)

    def on_right_click(self, event):
        if self.__mouse_inside_simulation_area(event): return
        self.multiqbitPlacer.cancel_drawing_control_line()

    def on_doubleclick(self, event):
        if self.__mouse_inside_simulation_area(event): return
        self.multiqbitPlacer.place_control_bit(*event.GetPosition(), self.filled_slots)

    def on_left_click(self, event):
        if self.__mouse_inside_simulation_area(event): return
        m_x, m_y = event.GetPosition()
        if self.gateName is not None:
            self.gatePlacer.placeGate(m_x,m_y)
        selectedGateTile = self.detectGateSelection(m_x, m_y)
        if selectedGateTile is not None:
            self.gateDragger.initDraggingGate(event, selectedGateTile)
        self.multiqbitPlacer.place_target(*event.GetPosition())
        self.Refresh()

    def on_mouse_move(self, event):
        if self.__mouse_inside_simulation_area(event): return
        self.gateDragger.dragGate(event)
        self.multiqbitPlacer.update_control_line(event)

    def on_endclick(self, event):
        if self.__mouse_inside_simulation_area(event): return
        self.gateDragger.stopDraggingGate(*event.GetPosition())

    def detectGateSelection(self, m_x, m_y):
        i,j = mouse_to_grid_coordinates(m_x, m_y)
        if (i, j) in self.filled_slots:
            return self.filled_slots[(i,j)]
        return None

    def resetView(self):
        self.Freeze()
        self.DestroyChildren()
        self.rootSizer.Clear()
        self.rootSizer.Add(self.new_QbitsReg())
        self.rootSizer.Layout()
        self.__enable_qubits_register_view()
        self.multiqbitPlacer.cancel_drawing_control_line()
        self.filled_slots = self.gridToGateTiles()
        self.flattened_multigates = self.__quantum_computer.flattened_multi_gates()
        self.Refresh()
        self.Thaw()

    def gridToGateTiles(self):
        flattened_grid = self.__quantum_computer.flattened_grid()
        return {(i,j): SingleGateTile(i, j, flattened_grid[(i,j)]) for (i,j) in flattened_grid}

    def new_QbitsReg(self):
        qbitRegSizer = wx.BoxSizer(wx.VERTICAL)
        self.__qbit_register_views = []
        for i in range(self.__quantum_computer.circuit_qubits_number()):
            qbitRegSizer.Add(self.newQbitRow(i))
        qbitRegSizer.Add(self.newAddQbitRow())
        return qbitRegSizer

    def newAddQbitRow(self):
        addbtnsizer = wx.BoxSizer(wx.HORIZONTAL)
        addbtnsizer.AddSpacer(GATE_SIZE)
        add_btn = self.newAddQbitBtn()
        addbtnsizer.Add(add_btn)
        self.__qbit_register_views.append(add_btn)
        return addbtnsizer

    def newQbitRow(self, i):
        qbitHorizontalBox = wx.GridSizer(3)
        qbitHorizontalBox.Add(self.newQbitLabel(i), 0, wx.CENTER)
        qbitMenu = QbitMenu()
        delBtn = DeleteQbitButton(self, i, qbitMenu, self.__gate_mediator, self.__quantum_computer)
        qbtn = QbitButton(self, i, qbitMenu, self.__gate_mediator, self.__quantum_computer)
        qbitMenu.setViews(qbtn, delBtn, qbitHorizontalBox)
        qbitHorizontalBox.Add(qbtn)
        qbitHorizontalBox.Add(delBtn)
        self.__qbit_register_views.append(qbtn)
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
        self.__quantum_computer.add_qbit()
        self.__gate_mediator.register_changed()

    def getW(self):
        return (MAX_COLUMNS + GRID_OFFSET) * GATE_SIZE + MAX_COLUMNS * GATE_H_SPACE

    def getH(self, qbitAreaOnly = False):
        return MAX_ROWS * GATE_SIZE if not qbitAreaOnly else self.__quantum_computer.circuit_qubits_number() * GATE_SIZE

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

    def ij_to_slot_center_xy(self, i, j):
        x = (GATE_SIZE + GATE_H_SPACE) * j + GATE_SIZE/2 + GRID_OFFSET * GATE_SIZE
        y = GATE_SIZE * i + GATE_SIZE/2
        return x,y

    def drawStimula(self, dc):
        if not self.shouldStimulate: return
        dc.SetPen(wx.Pen(wx.BLUE))
        for i in range(self.__quantum_computer.circuit_qubits_number()):
            for j in range(MAX_COLUMNS):
                if self.__quantum_computer.can_add_gate_at(i, j):
                    x,y = self.ij_to_slot_center_xy(i, j)
                    dc.DrawCircle(x, y, 3)

    def drawCords(self, dc):
        for i in range(self.__quantum_computer.circuit_qubits_number()):
            middle = GATE_SIZE * i + GATE_SIZE/2
            dc.DrawLine(GRID_OFFSET*GATE_SIZE, middle, self.getW(), middle)

    def drawGates(self, dc):
        dc.SetBrush(wx.Brush(wx.WHITE))
        for gateTile in self.filled_slots.values():
            gateTile.drawSelf(dc)

    def drawSimulationMark(self):
        width, height = self.__get_simulated_area_size()
        dc = wx.GCDC(wx.PaintDC(self))
        dc.SetBrush(wx.Brush(wx.Colour(255, 255, 255, 200)))
        dc.SetPen(wx.Pen(wx.WHITE))
        dc.DrawRectangle(0, 0, width, height)
        dc.SetPen(wx.Pen(wx.BLUE))
        dc.DrawLine(width, 0, width, height)

    def __get_simulated_area_size(self):
        step = self.__quantum_computer.simulation_step()
        width = (GATE_SIZE + GATE_H_SPACE) * (step+1) + GRID_OFFSET * GATE_SIZE
        height = GATE_SIZE * (self.__quantum_computer.circuit_qubits_number())
        return width, height

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

    def __enable_qubits_register_view(self):
        enable = self.__quantum_computer.simulation_step() == -1
        for view in self.__qbit_register_views:
            view.Enable(enable)


class CircuitStd(wx.Panel):

    def __init__(self, parent, gateMediator, quantum_computer):
        wx.Panel.__init__(self, parent)
        self.__gate_mediator = gateMediator
        self.__quantum_computer = quantum_computer
        self.__circuit_panel = None
        self.__fast_forward = None
        self.__fast_back = None
        self.__back = None
        self.__next = None
        self.__generate = None
        self.shouldStimulate = False
        rootSizer = wx.BoxSizer(wx.VERTICAL)
        rootSizer.AddSpacer(30)
        rootSizer.Add(self.newSimulationActionPanels(), 0, wx.CENTER)
        rootSizer.AddSpacer(30)
        rootSizer.Add(self.newCircuitScroll())
        self.SetSizer(rootSizer)
        self.__pass_circuit()

    def newCircuitScroll(self):
        circuitScroll = ScrolledPanel(self, size=(1500, 700))
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.__circuit_panel = CircuitPanel(circuitScroll, self.__quantum_computer, self.__gate_mediator)
        vbox.Add(self.__circuit_panel)
        circuitScroll.SetSizer(vbox)
        circuitScroll.SetupScrolling()
        return circuitScroll

    def newSimulationActionPanels(self):
        simulSizer = wx.BoxSizer(wx.HORIZONTAL)
        simulSizer.Add(self.__new_fast_back_btn())
        simulSizer.AddSpacer(20)
        simulSizer.Add(self.__new_back_btn())
        simulSizer.AddSpacer(20)
        simulSizer.Add(self.__new_next_btn())
        simulSizer.AddSpacer(20)
        simulSizer.Add(self.__new_fast_forward_btn())
        simulSizer.AddSpacer(20)
        simulSizer.Add(self.__new_generate_code_btn())
        return simulSizer

    def __new_fast_forward_btn(self):
        self.__fast_forward = FastForwardActionPanel(self, self.__gate_mediator, self.__quantum_computer)
        return self.__fast_forward

    def __new_fast_back_btn(self):
        self.__fast_back = FastBackActionPanel(self, self.__gate_mediator, self.__quantum_computer)
        return self.__fast_back

    def __new_next_btn(self):
        self.__next = NextActionPanel(self, self.__gate_mediator, self.__quantum_computer)
        return self.__next

    def __new_back_btn(self):
        self.__back = BackActionPanel(self, self.__gate_mediator, self.__quantum_computer)
        return self.__back

    def __new_generate_code_btn(self):
        self.__generate = GenerateCodeButton(self, self.__gate_mediator, self.__quantum_computer)
        return self.__generate

    def __pass_circuit(self):
        self.__back.set_circuit(self.__circuit_panel)
        self.__next.set_circuit(self.__circuit_panel)
        self.__fast_back.set_circuit(self.__circuit_panel)
        self.__fast_forward.set_circuit(self.__circuit_panel)

    def circuit_view(self):
        return self.__circuit_panel

class CircuitStd_(wx.Panel):

    def __init__(self, parent, gate_mediator, quantum_computer):
        wx.Panel.__init__(self, parent)
        root_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__inspector = CircuitInspector(parent=self, gate_mediator=gate_mediator, quantum_computer=quantum_computer)
        self.__circuit = CircuitStd(self, gate_mediator, quantum_computer)
        root_sizer.Add(self.__inspector)
        root_sizer.Add(self.__circuit)
        self.SetSizer(root_sizer)

    def circuit_view(self):
        return self.__circuit.circuit_view()