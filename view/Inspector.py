
from util.Utils import *
from wx.lib.scrolledpanel import ScrolledPanel

wxID_INSPECTORFRAME = wx.NewId()
wxID_SWITCHEDITOR = wx.NewId()
wxID_SWITCHDESIGNER = wx.NewId()
wxID_INDEXHELP = wx.NewId()
wxID_INSPECTORFRAMETOOLBAR = wx.NewId()
wxID_INSPECTORFRAMESTATUSBAR = wx.NewId()
wxID_INSPECTORFRAMETOOLBARTOOLS0 = wx.NewId()
wxID_INSPECTORFRAMEPAGES = wx.NewId()
wxID_INSPECTORFRAMECONSTR = wx.NewId()
wxID_INSPECTORFRAMEPROPS = wx.NewId()
wxID_INSPECTORFRAMEEVENTS = wx.NewId()

from qutip import Bloch
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

class Inspector(wx.Panel):

    inspWidth = 0
    bottomHeight = 0

    def __init__(self, parent, gateMediator):

        wx.Panel.__init__(self,  name='', parent=parent,
              pos=wx.Point(363, 272), style=wx.SIMPLE_BORDER,
              )

        self.gateMediator = gateMediator
        self.up_bmp = wx.Image('../Images/Inspector/Up.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.paletteImages = wx.ImageList(height=24, width=24)

        self.toolBar = wx.ToolBar(id=wxID_INSPECTORFRAMETOOLBAR, name='toolBar',
              parent=self, style=wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.CLIP_CHILDREN)
        # self.SetToolBar(self.toolBar)

        self.statusBar = wx.StatusBar(id=wxID_INSPECTORFRAMESTATUSBAR,
              name='statusBar', parent=self, style=wx.STB_SIZEGRIP)
        self.statusBar.SetFont(wx.Font(wx.FontInfo(10).Bold()))
        self._init_coll_statusBar_Fields(self.statusBar)
        # self.SetStatusBar(self.statusBar)

        self._init_coll_toolBar_Tools(self.toolBar)
        del self.up_bmp

        self.setDefaultSize()

        self.pages = InspectorNotebook(id=wxID_INSPECTORFRAMEPAGES,
              name='pages', parent=self)
        sizer = wx.BoxSizer()
        sizer.Add(self.pages, 1, wx.ALL | wx.EXPAND)
        sizer.SetDimension(0, 0, self.inspWidth, self.bottomHeight)
        self.SetSizer(sizer)

        self._init_coll_pages_Pages(self.pages)
        # self.SetIcon(wx.Icon('../Images/Icons/Inspector.ico'))

        self.selCmp = None
        self.sessionHandler = None

        self.toolBar.AddSeparator()
        AddToolButtonBmpIS(self, self.toolBar,
          '../Images/Shared/Delete.png', 'Delete selection', self.OnDelete)
        AddToolButtonBmpIS(self, self.toolBar,
          '../Images/Shared/Cut.png', 'Cut selection', self.OnCut)
        AddToolButtonBmpIS(self, self.toolBar,
          '../Images/Shared/Copy.png', 'Copy selection', self.OnCopy)
        AddToolButtonBmpIS(self, self.toolBar,
          '../Images/Shared/Paste.png', 'Paste selection', self.OnPaste)
        AddToolButtonBmpIS(self, self.toolBar,
          '../Images/Editor/Refresh.png', 'Recreate selection', self.OnRecreateSelection)
        self.toolBar.AddSeparator()
        self.wxID_POST = AddToolButtonBmpIS(self, self.toolBar,
          '../Images/Inspector/Post.png', 'Post the session', self.OnPost)
        self.wxID_CANCEL = AddToolButtonBmpIS(self, self.toolBar,
          '../Images/Inspector/Cancel.png', 'Cancel the session', self.OnCancel)
        self.toolBar.AddSeparator()
        self.wxID_ADDITEM = AddToolButtonBmpIS(self, self.toolBar,
              '../Images/Shared/NewItem.png', 'New item', self.OnNewItem)
        self.wxID_DELITEM = AddToolButtonBmpIS(self, self.toolBar,
          '../Images/Shared/DeleteItem.png', 'Delete item', self.OnDelItem)
        self.toolBar.AddSeparator()
        AddToolButtonBmpIS(self, self.toolBar,
          '../Images/Shared/Help.png', 'Show help', self.OnHelp)
        self.toolBar.Realize()

        self.Bind(wx.EVT_MENU, self.OnSwitchEditor, id=wxID_SWITCHEDITOR)
        self.Bind(wx.EVT_MENU, self.OnSwitchDesigner, id=wxID_SWITCHDESIGNER)
        self.Bind(wx.EVT_MENU, self.OnIndexHelp, id=wxID_INDEXHELP)
        self.Bind(wx.EVT_SIZE, self.OnSizing)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.updateToolBarState()

    def _init_coll_statusBar_Fields(self, parent):
        parent.SetFieldsCount(2)

        parent.SetStatusText('Nothing selected', 0)
        parent.SetStatusText('', 1)

        parent.SetStatusWidths([-1, -1])


    def _init_coll_toolBar_Tools(self, parent):
        parent.AddTool(bitmap=self.up_bmp, toolId =wxID_INSPECTORFRAMETOOLBARTOOLS0,
              label = "", shortHelp='Select parent')
        self.Bind(wx.EVT_TOOL, self.OnUp, id=wxID_INSPECTORFRAMETOOLBARTOOLS0)

        parent.Realize()

    def _init_coll_pages_Pages(self, parent):
        # create the page windows as children of the notebook
        page1 = PageOne(parent)
        page2 = PageTwo(parent)
        # page3 = CircuitInspector(parent = parent, id = -1)

        # parent.AddPage(page3, "Page 3")
        parent.AddPage(page1, "Page 1")
        parent.AddPage(page2, "Page 2")

    def updateToolBarState(self):
        canAddDel = self.selCmp is not None and \
              hasattr(self.selCmp, 'propItems') and \
              hasattr(self.selCmp, 'updateZopeProps')
        self.toolBar.EnableTool(self.wxID_ADDITEM, canAddDel)
        self.toolBar.EnableTool(self.wxID_DELITEM, canAddDel)

        hasSessionHandler = self.sessionHandler is not None
        self.toolBar.EnableTool(self.wxID_POST, hasSessionHandler)
        self.toolBar.EnableTool(self.wxID_CANCEL, hasSessionHandler)

    def setDefaultSize(self):
        screenX, screenY, screenWidth, screenHeight = wx.GetClientDisplayRect()
        paletteHeight = 120
        underPalette = paletteHeight + screenY
        editorScreenWidthPerc = 0.73
        edWidth = int(screenWidth * editorScreenWidthPerc)
        inspWidth = screenWidth - edWidth + 1
        bottomHeight = screenHeight - paletteHeight - 65
        self.SetSize(screenX, underPalette + screenY,
                           inspWidth, bottomHeight)
        self.inspWidth = inspWidth
        self.bottomHeight = bottomHeight

    def OnDelete(self, ev):
        pass

    def OnCut(self, ev):
        pass

    def OnCopy(self, ev):
        pass

    def OnPaste(self, ev):
        pass


    def OnRecreateSelection(self, ev):
        pass

    def OnCancel(self, ev):
        pass

    def OnPost(self, ev):
        pass

    def OnNewItem(self, ev):
        pass

    def OnDelItem(self, ev):
        pass

    def OnHelp(self, ev):
        pass

    def OnSwitchEditor(self, evt):
        pass

    def OnSwitchDesigner(self, evt):
        pass

    def OnIndexHelp(self, evt):
        pass

    def OnSizing(self, evt):
        pass

    def OnCloseWindow(self, evt):
        pass

    def OnUp(self, evt):
        pass

class PageOne(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "This is a PageOne object", (20,20))

class PageTwo(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "This is a PageTwo object", (40,40))

class PageThree(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "This is a PageThree object", (60,60))


wxID_ENTER= wx.NewId()
wxID_UNDOEDIT= wx.NewId()
wxID_CRSUP= wx.NewId()
wxID_CRSDOWN=wx.NewId()
wxID_CONTEXTHELP= wx.NewId()
wxID_OPENITEM= wx.NewId()
wxID_CLOSEITEM = wx.NewId()


class InspectorNotebook(wx.Notebook):
    """ Notebook that hosts Inspector pages """
    def __init__(self, *_args, **_kwargs):
        wx.Notebook.__init__(self, _kwargs['parent'], _kwargs['id'],
            style = 0)
        self.pages = {}
        self.inspector = _kwargs['parent']

    def destroy(self):
        self.pages = None
        self.inspector = None

    def AddPage(self, page, text, select=False, imageId=-1):
        wx.Notebook.AddPage(self, page, text)
        self.pages[text] = page

    def extendHelpUrl(self, cls):
        return self.pages[self.GetPageText(self.GetSelection())].extendHelpUrl(cls, '')

wxID_EVTCATS = wx.NewId()
wxID_EVTMACS = wx.NewId()


class BlochCanvas(wx.ScrolledWindow):
    def __init__(self, parent, gate_mediator, quantum_computer):
        wx.ScrolledWindow. __init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        self.__gate_mediator = gate_mediator
        gate_mediator.set_bloch_canvas(self)
        self.__quantum_computer = quantum_computer
        self.figure = Figure()
        FigureCanvas(self, -1, self.figure)
        b = Bloch(self.figure)
        b.make_sphere()
        self.__bloch = b

    def reset_view(self):
        nqubits = self.__quantum_computer.circuit_qubits_number()
        psi = self.__quantum_computer.current_simulation_psi()
        if nqubits != 1:
            return
        self.__bloch.clear()
        self.__bloch.add_states(psi)
        self.__bloch.make_sphere()
        self.__bloch.fig.canvas.draw()

    def initSize(self):
        w,h = self.GetClientSize()
        if w == 0 or h == 0: return
        ppiw, ppih = wx.GetDisplayPPI()
        self.figure.set_size_inches( (w / ppiw, w / ppiw))


class RestoreExperimentButton(wx.Button):

    def __init__(self, parent, label, experiment_index, gate_mediator, quantum_computer):
        wx.Button.__init__(self, parent, label = label, size=(-1, 50))
        self.__gate_mediator = gate_mediator
        self.__experiment_index = experiment_index
        self.__quantum_computer = quantum_computer
        self.Bind(wx.EVT_BUTTON, self.__on_click)

    def __on_click(self, event):
        self.__quantum_computer.restore_experiment_at(self.__experiment_index)
        self.__gate_mediator.history_changed()


class HistoryPanel(ScrolledPanel):

    def __init__(self, parent, gate_mediator, quantum_computer):
        super().__init__(parent)
        self.__quantum_computer = quantum_computer
        self.__gate_mediator = gate_mediator
        gate_mediator.set_history_panel(self)
        self.__root_sizer = wx.BoxSizer(wx.VERTICAL)
        self.__create_new_history_view()
        self.SetSizer(self.__root_sizer)

    def __create_new_history_view(self):
        self.__root_sizer.AddSpacer(20)
        self.__root_sizer.Add(new_big_font_label(self, "History of experiments"), 0, wx.CENTER)
        self.__root_sizer.AddSpacer(20)
        for experiment in self.__quantum_computer.all_experiments():
            label = "restore experiment {} created at {}".format(experiment.index(), experiment.date())
            self.__root_sizer.Add(RestoreExperimentButton(self, label, experiment.index(), self.__gate_mediator, self.__quantum_computer), 0, wx.CENTER)
        self.__root_sizer.Layout()

    def reset_view(self):
        self.DestroyChildren()
        self.__root_sizer.Clear()
        self.__create_new_history_view()


class CircuitInspector(wx.SplitterWindow):
    """ Window that hosts event name values and event category selection """
    def __init__(self, parent, gate_mediator, quantum_computer):
        wx.SplitterWindow.__init__(self, parent, style=wx.SP_LIVE_UPDATE | wx.SP_3DSASH, size=(450, 1000))
        self.__quantum_computer = quantum_computer
        self.__gate_mediator = gate_mediator
        gate_mediator.set_circuit_inspector(self)

        self.__bloch_canvas = BlochCanvas(self, gate_mediator, quantum_computer)
        self.__probs_area = None

        self.SplitHorizontally(self.__new_probs_history_splitter(), self.__bloch_canvas)
        self.__sash_pos = 800
        self.SetSashPosition(self.__sash_pos)

        self.__should_show = False

        self.Bind(wx.EVT_SIZE, self.onresize)

        self.__timer = wx.Timer(self.__bloch_canvas)
        self.__bloch_canvas.Bind(wx.EVT_TIMER, self.__show_bloch, self.__timer)
        self.__bind()

    def __new_probs_history_splitter(self):
        probs_history_splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE | wx.SP_3DSASH)
        probs_panel = self.__new_probs_panel(probs_history_splitter)
        history_panel = HistoryPanel(probs_history_splitter, self.__gate_mediator, self.__quantum_computer)
        probs_history_splitter.SplitHorizontally(probs_panel, history_panel, 375)
        return probs_history_splitter

    def __new_probs_panel(self, parent):
        panel = ScrolledPanel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(new_big_font_label(panel, "State of the register"), 0, wx.CENTER)
        sizer.AddSpacer(20)
        self.__probs_area = wx.TextCtrl(panel, style=wx.TE_READONLY | wx.TE_CENTRE | wx.TE_MULTILINE | wx.NO_BORDER)
        self.__probs_area.SetValue(self.__quantum_computer.current_simulation_psi_str())
        sizer.Add(self.__probs_area, wx.EXPAND, wx.EXPAND)
        sizer.Layout()
        panel.SetSizer(sizer)
        return panel

    def __bind(self):
        self.Bind(wx.EVT_SPLITTER_DCLICK, self.__dev_null)
        self.Bind(wx.EVT_SPLITTER_DOUBLECLICKED, self.__dev_null)
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.__dev_null)
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.__dev_null)
        self.Bind(wx.EVT_SPLITTER_UNSPLIT, self.__dev_null)

    def __dev_null(self, event):
        event.Veto()

    def reset_view(self):
        nqubits = self.__quantum_computer.circuit_qubits_number()
        self.__should_show = nqubits == 1
        self.__timer.Start(20)
        self.__probs_area.SetValue(self.__quantum_computer.current_simulation_psi_str())

    def __show_bloch(self, _):
        if not self.__should_show:
            if self.__sash_pos < 800:
                self.__sash_pos += 40
            else:
                self.__timer.Stop()
        else:
            if self.__sash_pos > 375:
                self.__sash_pos -= 40
            else:
                self.__timer.Stop()
        self.SetSashPosition(self.__sash_pos)

    def onresize(self, ev):
        self.__bloch_canvas.initSize()
        ev.Skip()

    def setInspector(self, inspector):
        self.inspector = inspector

    def destroy(self):
        self.inspector = None
