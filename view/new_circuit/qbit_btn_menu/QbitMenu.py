import wx

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
