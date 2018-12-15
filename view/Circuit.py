import wx

from view.CordPlacer import CordPlacer
from view.GateDragger import GateDragger
from view.GatePlacer import GatePlacer
from view.MeshPlacer import MeshPlacer


class Circuit(wx.Panel):
    CONNECTIONS_IN_ROW = 20
    CONNECTIONS_IN_COLUMN = 10
    POINT_RADIUS = 2
    POINT_MISS_DIST = 4 #distance from the border of a point at which point is considered not selected

    def __init__(self, parent, gateMediator):
        wx.Panel.__init__(self, parent)
        self.shouldStimulate = False
        self.gateMediator = gateMediator
        self.meshPlacer = MeshPlacer(self.CONNECTIONS_IN_ROW, self.CONNECTIONS_IN_COLUMN, self.POINT_RADIUS)
        self.cordPlacer = CordPlacer(self, self.CONNECTIONS_IN_ROW, self.CONNECTIONS_IN_COLUMN, self.POINT_RADIUS, self.POINT_MISS_DIST)
        self.gatePlacer = GatePlacer(self,  self.CONNECTIONS_IN_ROW, self.CONNECTIONS_IN_COLUMN, self.POINT_RADIUS, self.POINT_MISS_DIST)
        self.gateDragger = GateDragger(self)
        self.selectedGate = None
        self.selectedCord = None
        self.bind()
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetBackgroundColour(wx.WHITE)

    def bind(self):
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.Bind(wx.EVT_LEFT_UP, self.on_endclick)
        self.Bind(wx.EVT_RIGHT_UP, self.on_rclick)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.GetParent().Bind(wx.EVT_CHAR, self.on_keyboard)

    def on_keyboard(self, event):
        keyCode = event.GetKeyCode()
        if keyCode == wx.WXK_DELETE:
            self.cordPlacer.removeSelectedCord()
            self.gatePlacer.removeSelectedGate()
            self.Refresh()


    def on_endclick(self, event):
        self.gateDragger.stopDraggingGate(*event.GetPosition())

    def stimula(self, shouldStimulate, gate=None):
        self.shouldStimulate = shouldStimulate
        self.gatePlacer.gateNameToCreate = gate
        self.Refresh()

    def on_rclick(self, event):
        self.cordPlacer.unselectCord()
        self.selectedGate = None
        self.gatePlacer.gateNameToCreate = None
        self.Refresh()

    def on_size(self, event):
        event.Skip()
        self.Refresh()

    def on_mouse_move(self, event):
        if not self.shouldStimulate: self.cordPlacer.moveCord(event)
        self.gateDragger.dragGate(event, self.selectedGate)
        self.Refresh()

    def on_click(self, event):
        m_x, m_y = event.GetPosition()
        if not self.shouldStimulate: self.cordPlacer.placeCord(self.gatePlacer.gates, m_x, m_y)
        self.gatePlacer.placeGate(m_x, m_y, self.meshPlacer.meshGraph, self.gateMediator)
        self.selectedGate = self.gatePlacer.detectGateSelection(m_x, m_y)
        self.selectedCord = self.cordPlacer.detectCordSelection(m_x, m_y)
        self.gateDragger.initDraggingGate(event, self.selectedGate)
        self.Refresh()

    def on_paint(self, event):
        w, h = self.GetClientSize()
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        if self.shouldStimulate: self.gatePlacer.drawGateStimula(dc)
        self.meshPlacer.draw_mesh_points(dc, w, h)
        self.cordPlacer.draw_unfinished_cord(dc, self.meshPlacer.meshGraph)
        self.gatePlacer.drawGates(dc)
        self.cordPlacer.drawCords(dc, self.meshPlacer.meshGraph)
        if self.selectedGate is not None: self.selectedGate.drawSelectionIndicator(dc)


