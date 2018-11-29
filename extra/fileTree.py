import  wx

#----------------------------------------------------------------------

class TestPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        txt1 = wx.StaticText(self, -1, "style=0")
        dir1 = wx.GenericDirCtrl(self, -1, size=(200,225), style=0)

        txt2 = wx.StaticText(self, -1, "wx.DIRCTRL_DIR_ONLY")
        dir2 = wx.GenericDirCtrl(self, -1, size=(200,225), style=wx.DIRCTRL_DIR_ONLY|wx.DIRCTRL_MULTIPLE)

        txt3 = wx.StaticText(self, -1, "wx.DIRCTRL_SHOW_FILTERS")
        dir3 = wx.GenericDirCtrl(self, -1, size=(200,225), style=wx.DIRCTRL_SHOW_FILTERS,
                                filter="All files (*.*)|*.*|Python files (*.py)|*.py")

        sz = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)
        sz.Add((35, 35))  # some space above
        sz.Add((35, 35))
        sz.Add((35, 35))

        sz.Add(txt1)
        sz.Add(txt2)
        sz.Add(txt3)

        sz.Add(dir1, 0, wx.EXPAND)
        sz.Add(dir2, 0, wx.EXPAND)
        sz.Add(dir3, 0, wx.EXPAND)

        sz.Add((35,35))  # some space below

        sz.AddGrowableRow(2)
        sz.AddGrowableCol(0)
        sz.AddGrowableCol(1)
        sz.AddGrowableCol(2)

        self.SetSizer(sz)
        self.SetAutoLayout(True)

class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None)
        self.SetTitle('My Title')
        self.SetClientSize((500, 500))
        self.Center()
        self.view = TestPanel(self)

def main():
    app = wx.App(False)
    frame = Frame()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()