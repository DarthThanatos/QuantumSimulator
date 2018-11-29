import re

import time
import wx
import wx.html
import wx.lib.wxpTag

import sys
from threading import Thread

wxID_ABOUTBOX = wx.NewId()


about_html = '''
<html>
<body bgcolor="#4488FF">
<center>
<table cellpadding="5" bgcolor="#FFFFFF" width="100%%">
  <tr>
    <td align="center"><br>
    <img src="%s"><br>
    <font color="#006600" size="+4"><b>Constructor</b></font><br><strong>v%s</strong>%s</td>
  </tr>
</table>
%s
</body>
</html>
'''

progress_text = '''<p>
<wxp module="wx" class="StaticText">
  <param name="label" value="  ">
  <param name="id"    value="%d">
  <param name="size"  value="(352, 20)">
</wxp>
<wxp module="wx" class="Window">
  <param name="id"    value="%d">
  <param name="size"  value="(352, 16)">
</wxp>'''

wx.FileSystem.AddHandler(wx.MemoryFSHandler())

def addImagesToFS():
    PNG = wx.BITMAP_TYPE_PNG
    for name, path, type in [('Simul.jpg', '../Images/Shared/Simul.jpg', wx.BITMAP_TYPE_JPEG)]:
        if name not in addImagesToFS.addedImages:
            # wx.MemoryFSHandler.AddFile(name, Preferences.IS.load(path), type)
            wx.MemoryFSHandler.AddFile(name, wx.Image(path, type).ConvertToBitmap(),type)
            addImagesToFS.addedImages.append(name)
            print("Added " + name)

addImagesToFS.addedImages = []

class LoadingScreen(wx.Frame):

    border = 7
    progressBorder = 1
    fileOpeningFactor = 10
    # noinspection PyPropertyAccess
    def __init__(self, parent, onLoaded):
        wx.Frame.__init__(self, size=wx.Size(418, 320), pos=(-1, -1),
              id=wxID_ABOUTBOX, title='Loading', parent=parent,
              name='LoadingScreen', style=wx.SIMPLE_BORDER)
        self.init_ctrls()
        addImagesToFS()
        self.black_background = wx.Window(self, -1, pos=(0, 0), size=self.GetClientSize(), style=wx.CLIP_CHILDREN)
        self.black_background.SetBackgroundColour(wx.BLACK)
        self.html = wx.html.HtmlWindow(self.black_background, -1, style=wx.CLIP_CHILDREN | wx.html.HW_NO_SELECTION | wx.html.HW_SCROLLBAR_NEVER)
        self.onLoaded = onLoaded
        self.setPage()
        self.black_background.SetAutoLayout(True)
        lc = wx.LayoutConstraints()
        lc.top.SameAs(self.black_background, wx.Top, self.border)
        lc.left.SameAs(self.black_background, wx.Left, self.border)
        lc.bottom.SameAs(self.black_background, wx.Bottom, self.border)
        lc.right.SameAs(self.black_background, wx.Right, self.border)
        self.html.SetConstraints(lc)
        self.black_background.Layout()
        self.Center(wx.BOTH)
        self.SetAcceleratorTable(wx.AcceleratorTable([(0, wx.WXK_ESCAPE, wx.ID_OK)]))

    def init_ctrls(self):
        self.progressId = wx.NewId()
        self.gaugePId = wx.NewId()
        self.SetBackgroundColour(wx.Colour(0x44, 0x88, 0xFF))

    def setPage(self):
        txt = about_html % ('memory:Simul.jpg',  '0.7.2', progress_text % (self.progressId, self.gaugePId), '')
        self.html.SetPage(txt)
        self.initCtrlNames()

    def initCtrlNames(self):
        self.label = self.FindWindowById(self.progressId)
        self.label.SetWindowStyle(wx.ALIGN_CENTER | wx.CLIP_CHILDREN | wx.ST_NO_AUTORESIZE)
        self.label.SetBackgroundColour(wx.WHITE)
        parentWidth = self.label.GetParent().GetClientSize().x
        self.label.SetSize((parentWidth - 40, self.label.GetSize().y))

        gaugePrnt = self.FindWindowById(self.gaugePId)
        gaugePrnt.SetBackgroundColour(wx.BLACK)  # wx.Colour(0x99, 0xcc, 0xff))
        gaugeSze = gaugePrnt.GetClientSize()
        self.gauge = wx.Gauge(gaugePrnt, -1,
              range= 100,
              style=wx.GA_HORIZONTAL | wx.GA_SMOOTH,
              pos=(self.progressBorder, self.progressBorder),
              size=(gaugeSze.x - 2 * self.progressBorder,
                    gaugeSze.y - 2 * self.progressBorder))
        self.gauge.SetBackgroundColour(wx.Colour(0xff, 0x33, 0x00))

        # route all printing thru the text on the splash screen
        sys.stdout = StaticTextPF(self.label)

        self.cnt = 0
        self.cntTotal = 100
        Thread(target=self.monitorModuleCount).start()
        self.Bind(EVT_MOD_CNT_UPD, self.OnUpdateProgress)

    def monitorModuleCount(self):
        self._live = True
        step = 25
        cur = 0
        logListIndex = 0
        logList = ["Menu", "Inspector", "Editor","Shell", "Simulator"]
        while self._live:
            time.sleep(.25)
            if cur >= 100: self.Destroy()
            cur += step
            val = self.cntTotal if cur >= self.cntTotal else cur
            print ("Imported " + str(logList[logListIndex]))
            logListIndex+=1
            wx.PostEvent(self, ModCntUpdateEvent(val, 'importing'))


    def OnUpdateProgress(self, event):
        self._live = event.tpe == 'importing' and self._live
        if self.gauge:
            cnt = event.cnt
            val = min(self.gauge.GetRange(), cnt)
            self.gauge.SetValue(val)
        self.Update()

    def Destroy(self):
        self._live = False
        self.gauge = None
        if sys:
            sys.stdout = sys.__stdout__
        wx.CallAfter(self.onLoaded)
        wx.Frame.Destroy(self)

class StaticTextPF:

    prog_update = re.compile('<<(?P<cnt>[0-9]+)/(?P<tot>[0-9]+)>>')

    def __init__(self, output = None):
        if output is None: output = []
        self.output = output

    def writelines(self, l):
        map(self.write, l)

    def flush(self):
        pass

    def isatty(self):
        return False

    def write(self, s):
        res = self.prog_update.search(s)
        if res:
            cnt = int(res.group('cnt'))
            wx.PostEvent(self.output.GetGrandParent().GetParent(),
                         ModCntUpdateEvent(cnt, 'opening'))
            s = s[:res.start()]

        ss = s.strip()
        if ss:
            self.output.SetLabel(ss)

        if sys:
            try:
                sys.__stdout__.write(s)
            except UnicodeEncodeError:
                s = s.encode(sys.getdefaultencoding(), 'replace')
                sys.__stdout__.write(s)

        wx.Yield()

wxEVT_MOD_CNT_UPD = wx.NewId()
EVT_MOD_CNT_UPD = wx.PyEventBinder(wxEVT_MOD_CNT_UPD)

class ModCntUpdateEvent(wx.PyEvent):
    def __init__(self, cnt, tpe):
        wx.PyEvent.__init__(self)
        self.SetEventType(wxEVT_MOD_CNT_UPD)
        self.cnt = cnt
        self.tpe = tpe
