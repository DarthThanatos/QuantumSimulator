import wx


class MyDialog(wx.Dialog):
    def __init__(self, parent, title):
        super(MyDialog, self).__init__(parent, title=title, size=(250, 150))
        panel = wx.Panel(self)
        # self.btn = wx.Button(panel, wx.ID_OK, label="ok", size=(50, 20), pos=(75, 50))
        label = wx.StaticText(panel, pos = (0,0), size = (50,20), label="val")
        label.SetBackgroundColour(wx.RED)
        self.ok = wx.Button(panel, label = "ok", size=(50, 20), pos=(75, 50))
        self.ok.Bind(wx.EVT_BUTTON, self.on_click_ok)
        self.cancel = wx.Button(panel, label = "cancel", size=(50, 20), pos=(130, 50))
        self.cancel.Bind(wx.EVT_BUTTON, self.on_click_cancel)

    def on_click_ok(self, ev):
        print("clicked ok")
        self.EndModal(200)

    def on_click_cancel(self, ev):
        print("clicked cancel")
        self.EndModal(100)


class Mywin(wx.Frame):
    def __init__(self, parent, title):
        super(Mywin, self).__init__(parent, title=title, size=(250, 150))
        self.InitUI()

    def InitUI(self):
        panel = wx.Panel(self)
        btn = wx.Button(panel, label="Modal Dialog", pos=(75, 10))
        btn1 = wx.Button(panel, label="Modeless Dialog", pos=(75, 40))
        btn2 = wx.Button(panel, label="MessageBox", pos=(75, 70))
        btn.Bind(wx.EVT_BUTTON, self.OnModal)

        a = btn1.Bind(wx.EVT_BUTTON, self.OnModeless)
        btn2.Bind(wx.EVT_BUTTON, self.Onmsgbox)
        self.Centre()
        self.Show(True)

    def OnModal(self, event):
        a = MyDialog(self, "Dialog showmodal").ShowModal()
        print(a)

    def OnModeless(self, event):
        a = MyDialog(self, "Dialog modeless show").Show()
        print(a)

    def Onmsgbox(self, event):
        wx.MessageBox("This is a Message Box", "Message", wx.OK | wx.ICON_INFORMATION)


ex = wx.App()
Mywin(None, 'MenuBar demo')
ex.MainLoop()