import wx

from wx.lib.scrolledpanel import ScrolledPanel

from model.QuantumComputer import QuantumComputer
from util.Utils import newScaledImgBitmap, newIconButton
from view.new_circuit.GateDragger import GateDragger

KET_0 = "../Images/Circuit/ket_0.png"
KET_1 = "../Images/Circuit/ket_1.png"

GATE_SIZE = 32
GATE_H_SPACE = 3
MAX_ROWS = 15
MAX_COLUMNS = 300

class QbitMenu:

    def __init__(self):
        self.qbitButton = None
        self.deleteButton = None
        self.rowSizer = None

    def setViews(self, qbitBtn, deleteBtn, rowSizer):
        self.qbitButton = qbitBtn
        self.deleteButton = deleteBtn
        self.rowSizer = rowSizer
        self.timer = wx.Timer(self.qbitButton)
        qbitBtn.Bind(wx.EVT_TIMER, self.onMouseLeaveExpired, self.timer)

    def onMouseHoverOnQbit(self):
        self.deleteButton.Show()
        self.rowSizer.Layout()

    def onMouseLeaveQbit(self):
        self.timer.StartOnce(100)

    def onMouseLeaveExpired(self, ev):
        rect = self.deleteButton.GetRect()
        if not rect.Contains(self.qbitButton.GetParent().ScreenToClient(wx.GetMousePosition())):
            self.deleteButton.Hide()
            self.rowSizer.Layout()

    def onMouseLeaveDelete(self):
        self.deleteButton.Hide()
        self.rowSizer.Layout()

class QbitButton(wx.Button):
    def __init__(self, parent,  index, qbitMenu, quantumComputer):
        wx.Button.__init__(self, parent= parent, size=(GATE_SIZE, GATE_SIZE))
        self.quantumComputer = quantumComputer
        self.value = quantumComputer.qbitValueAt(index)
        self.index = index
        self.qbitMenu = qbitMenu
        self.setValueView()
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Bind(wx.EVT_ENTER_WINDOW, self.onMouseHover)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)

    def onMouseHover(self, ev):
        self.qbitMenu.onMouseHoverOnQbit()

    def onMouseLeave(self, ev):
        self.qbitMenu.onMouseLeaveQbit()

    def onClick(self, ev):
        self.quantumComputer.swapQbitValueAt(self.index)
        self.GetParent().resetView()

    def setValueView(self):
        self.SetBitmap(newScaledImgBitmap(KET_0 if self.value == 0 else KET_1, (GATE_SIZE, GATE_SIZE)))

class DeleteQbitButton(wx.Button):

    def __init__(self, parent, index, qbitMenu, quantumComputer):
        wx.Button.__init__(self, parent, size=(GATE_SIZE, GATE_SIZE))
        self.qbitMenu = qbitMenu
        self.index = index
        self.quantumComputer = quantumComputer
        self.SetBitmap(newScaledImgBitmap("../Images/Circuit/delete.png", (GATE_SIZE, GATE_SIZE)))
        self.Bind(wx.EVT_LEAVE_WINDOW, self.onMouseLeave)
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Hide()

    def onMouseLeave(self, ev):
        self.qbitMenu.onMouseLeaveDelete()

    def onClick(self, ev):
        self.quantumComputer.removeQbit(self.index)
        self.GetParent().resetView()

class SingleGateTile:
    def __init__(self, i, j, gateName):
        self.rect = wx.Rect2D(j * (GATE_SIZE + GATE_H_SPACE), i * GATE_SIZE, GATE_SIZE, GATE_SIZE)
        self.gateName = gateName
        self.ij = (i, j)
        self.bmp = newScaledImgBitmap('../Images/Palette/{}.png'.format(self.gateName), (GATE_SIZE, GATE_SIZE))

    def drawSelf(self, dc):
        x, y = self.rect.GetLeft(), self.rect.GetTop()
        dc.DrawRectangle(*self.rect.GetPosition(), *self.rect.GetSize())
        dc.DrawBitmap(self.bmp, x, y)

    def removeSelf(self, filledSlots):
        filledSlots.__delitem__(self.ij)

class CircuitPanel(wx.Panel):

    def __init__(self, parent, nqubits, gateMediator):
        size = (self.getW(), self.getH())
        wx.Panel.__init__(self, parent, size=size)

        self.quantumComputer = QuantumComputer(nqbits=nqubits)
        self.shouldStimulate = False
        self.filled_slots = {} # (i,j) => gateTile
        self.gateDragger = GateDragger(self)
        self.draggedGateTile = None
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

    def on_left_click(self,  event):
        m_x, m_y = event.GetPosition()
        if self.gateName is not None:
            self.placeGate(m_x,m_y)
        self.draggedGateTile = self.detectGateSelection(m_x, m_y)
        if self.draggedGateTile is not None:
            self.gateDragger.initDraggingGate(event, self.draggedGateTile)
        self.Refresh()

    def on_mouse_move(self, event):
        self.gateDragger.dragGate(event, self.draggedGateTile)

    def on_endclick(self, event):
        self.gateDragger.stopDraggingGate(*event.GetPosition())
        self.Refresh()

    def detectGateSelection(self, m_x, m_y):
        i,j = int(m_y / GATE_SIZE), int(m_x / (GATE_SIZE + GATE_H_SPACE))
        if (i, j) in self.filled_slots:
            return self.filled_slots[(i,j)]
        return None

    def swapSlotsIfPossible(self, m_x, m_y):
        i,j = int(m_y / GATE_SIZE), int(m_x / (GATE_SIZE + GATE_H_SPACE))
        if (i, j) in self.filled_slots: return
        self.quantumComputer.removeGate(*self.draggedGateTile.ij)
        if m_x >= self.getW() or m_x < 2 * GATE_SIZE or \
             m_y >= self.getH(qbitAreaOnly=True) or m_y < 0:
                self.draggedGateTile = None
                self.resetView()
                return
        self.quantumComputer.addGate(i, j, self.draggedGateTile.gateName)
        self.draggedGateTile = None
        self.resetView()

    def placeGate(self, m_x, m_y):
        if m_x < self.getW() and m_x > 2 * GATE_SIZE:
            if m_y < self.getH(qbitAreaOnly=True) and m_y > 0:
                i,j = int(m_y / GATE_SIZE), int(m_x / (GATE_SIZE + GATE_H_SPACE))
                if not (i,j) in self.filled_slots:
                    self.quantumComputer.addGate(i,j, self.gateName)
        self.gateMediator.gateUnselected()
        self.resetView()

    def resetView(self):
        self.Freeze()
        self.DestroyChildren()
        self.rootSizer.Clear()
        self.rootSizer.Add(self.new_QbitsReg())
        self.rootSizer.Layout()
        self.filled_slots = self.gridToGateTiles()
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
        self.drawGates(dc)
        if self.gateDragger.dragging:
            self.drawDeleteMsg(dc)
        del dc # so that it is deallocated and we can create a new configuration below
        self.drawSimulationMark()

    def drawStimula(self, dc):
        if not self.shouldStimulate: return
        dc.SetPen(wx.Pen(wx.BLUE))
        for i in range(self.quantumComputer.register.nqubits):
            for j in range(2, MAX_COLUMNS + 2):
                if not (i,j) in self.filled_slots:
                    x = GATE_SIZE * j + GATE_SIZE/2 + j * GATE_H_SPACE
                    y = GATE_SIZE * i + GATE_SIZE/2
                    dc.DrawCircle(x, y, 3)

    def drawCords(self, dc):
        for i in range(self.quantumComputer.register.nqubits):
            middle = GATE_SIZE * i + GATE_SIZE/2
            dc.DrawLine(2*GATE_SIZE, middle, self.getW(), middle)

    def drawGates(self, dc):
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

class SimulActionPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel_width = 150
        btn = wx.Button(self, size = (panel_width, 25))
        btn.SetBitmap(newScaledImgBitmap("../Images/Circuit/{}.png".format(self.bmpFile()), (GATE_SIZE, GATE_SIZE)))
        btn.Bind(wx.EVT_BUTTON, self.onclick)

        sizer.Add(btn, 0, wx.CENTER)
        sizer.Add(wx.TextCtrl(self, value=self.shortDesc(), style=wx.TE_READONLY | wx.TE_CENTER | wx.TE_MULTILINE | wx.NO_BORDER | wx.TE_NO_VSCROLL, size=(panel_width, 50)), 0, wx.CENTER)
        self.SetSizer(sizer)

    def shortDesc(self):
        raise Exception("Not implemented")

    def onclick(self, ev):
        self.controlSimulation()

    def controlSimulation(self):
        raise Exception("control simulation not implemented")

    def bmpFile(self):
        raise Exception("bmp path not implemented")



class NextActionPanel(SimulActionPanel):
    def bmpFile(self):
        return "next"

    def shortDesc(self):
        return "Go to next Step"

    def controlSimulation(self):
        print("nb control simul")

class BackActionPanel(SimulActionPanel):
    def bmpFile(self):
        return "back"

    def shortDesc(self):
        return "Break simulation"

    def controlSimulation(self):
        print("back control simul")

class FastForwardActionPanel(SimulActionPanel):
    def bmpFile(self):
        return "fast_forward"

    def shortDesc(self):
        return "Fast forward to the end"

    def controlSimulation(self):
        print("ff control simul")

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