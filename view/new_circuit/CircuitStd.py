import wx

from wx.lib.scrolledpanel import ScrolledPanel
from util.Utils import newScaledImgBitmap
from view.new_circuit.GateDragger import GateDragger

KET_0 = "../Images/Circuit/ket_0.png"
KET_1 = "../Images/Circuit/ket_1.png"

GATE_SIZE = 32
GATE_H_SPACE = 3
MAX_ROWS = 15
MAX_COLUMNS = 300

class QbitButton(wx.Button):
    def __init__(self, parent, value = 0):
        wx.Button.__init__(self, parent= parent, size=(GATE_SIZE, GATE_SIZE))
        self.value = value
        self.changeValueView()
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, ev):
        self.value = 0 if self.value == 1 else 1
        self.changeValueView()

    def changeValueView(self):
        self.SetBitmap(newScaledImgBitmap(KET_0 if self.value == 0 else KET_1, (GATE_SIZE, GATE_SIZE)))

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

        self.nqubits = nqubits
        self.shouldStimulate = False
        self.gateName = None
        self.filled_slots = {}
        self.gateDragger = GateDragger(self)
        self.selectedGate = None
        self.deleteMsg = False
        self.gateMediator = gateMediator

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.new_QbitsReg(nqubits))
        self.SetSizer(hbox)

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
        self.selectedGate = self.detectGateSelection(m_x, m_y)
        if self.selectedGate is not None:
            self.gateDragger.initDraggingGate(event, self.selectedGate)
        self.Refresh()

    def on_mouse_move(self, event):
        self.gateDragger.dragGate(event, self.selectedGate)

    def on_endclick(self, event):
        self.gateDragger.stopDraggingGate(*event.GetPosition())
        self.Refresh()

    def exchangeSlotsIfPossibleOnSelected(self, m_x, m_y):
        i,j = int(m_y / GATE_SIZE), int(m_x / (GATE_SIZE + GATE_H_SPACE))
        if (i, j) in self.filled_slots: return
        self.selectedGate.removeSelf(self.filled_slots)
        if m_x >= self.getW() or m_y >= self.getH(qbitAreaOnly=True): return
        self.filled_slots[(i,j)] = SingleGateTile(i, j, self.selectedGate.gateName)

    def detectGateSelection(self, m_x, m_y):
        i,j = int(m_y / GATE_SIZE), int(m_x / (GATE_SIZE + GATE_H_SPACE))
        if (i, j) in self.filled_slots:
            return self.filled_slots[(i,j)]
        return None

    def placeGate(self, m_x, m_y):
        if m_x < self.getW() and m_y < self.getH(qbitAreaOnly=True):
            i,j = int(m_y / GATE_SIZE), int(m_x / (GATE_SIZE + GATE_H_SPACE))
            if not (i,j) in self.filled_slots:
                self.filled_slots[(i,j)] = SingleGateTile(i, j, self.gateName)
        self.gateMediator.gateUnselected()

    def getW(self):
        return (MAX_COLUMNS + 1) * GATE_SIZE + MAX_COLUMNS * GATE_H_SPACE

    def getH(self, qbitAreaOnly = False):
        return MAX_ROWS * GATE_SIZE if not qbitAreaOnly else self.nqubits * GATE_SIZE

    def new_QbitsReg(self, N):
        vbox = wx.BoxSizer(wx.VERTICAL)
        for i in range(N):
            vbox.Add(QbitButton(self))
        return vbox

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

    def drawCords(self, dc):
        for i in range(self.nqubits):
            middle = GATE_SIZE * i + GATE_SIZE/2
            dc.DrawLine(GATE_SIZE, middle, self.getW(), middle)

    def drawStimula(self, dc):
        if not self.shouldStimulate: return
        dc.SetPen(wx.Pen(wx.BLUE))
        for i in range(self.nqubits):
            for j in range(1, MAX_COLUMNS):
                if not (i,j) in self.filled_slots:
                    x = GATE_SIZE * j + GATE_SIZE/2 + j * GATE_H_SPACE
                    y = GATE_SIZE * i + GATE_SIZE/2
                    dc.DrawCircle(x, y, 3)

    def drawGates(self, dc):
        for gateTile in self.filled_slots.values():
            gateTile.drawSelf(dc)

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