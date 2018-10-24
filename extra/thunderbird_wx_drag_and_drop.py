import wx


class DropTarget(wx.DropTarget):
    def __init__(self, textCtrl, *args, **kwargs):
        super(DropTarget, self).__init__(*args, **kwargs)
        self.textCtrl = textCtrl
        self.composite = wx.DataObjectComposite()
        self.textDropData = wx.TextDataObject()
        self.fileDropData = wx.FileDataObject()
        self.thunderbirdDropData = wx.CustomDataObject('text/x-moz-message')
        self.composite.Add(self.thunderbirdDropData)
        self.composite.Add(self.textDropData)
        self.composite.Add(self.fileDropData)
        self.SetDataObject(self.composite)

    def OnDrop(self, x, y):
        return True

    def OnData(self, x, y, result):
        self.GetData()
        formatType, formatId = self.GetReceivedFormatAndId()
        if formatId == 'text/x-moz-message':
            return self.OnThunderbirdDrop()
        elif formatType in (wx.DF_TEXT, wx.DF_UNICODETEXT):
            return self.OnTextDrop()
        elif formatType == wx.DF_FILENAME:
            return self.OnFileDrop()

    def GetReceivedFormatAndId(self):
        format = self.composite.GetReceivedFormat()
        formatType = format.GetType()
        try:
            formatId = format.GetId() # May throw exception on unknown formats
        except:
            formatId = None
        return formatType, formatId

    def OnThunderbirdDrop(self):
        self.textCtrl.AppendText(self.thunderbirdDropData.GetData().decode('utf-16'))
        self.textCtrl.AppendText('\n')
        return wx.DragCopy

    def OnTextDrop(self):
        self.textCtrl.AppendText(self.textDropData.GetText() + '\n')
        return wx.DragCopy

    def OnFileDrop(self):
        for filename in self.fileDropData.GetFilenames():
            self.textCtrl.AppendText(filename + '\n')
        return wx.DragCopy


class Frame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(Frame, self).__init__(*args, **kwargs)
        textCtrl = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        textCtrl.SetDropTarget(DropTarget(textCtrl))


app = wx.App(False)
frame = Frame(None)
frame.Show()
app.MainLoop()