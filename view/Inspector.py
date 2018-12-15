
from util.Utils import *

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

class Inspector(wx.MDIChildFrame):

    inspWidth = 0
    bottomHeight = 0

    def __init__(self, parent, gateMediator):

        wx.MDIChildFrame.__init__(self, id=wxID_INSPECTORFRAME, name='', parent=parent,
              pos=wx.Point(363, 272), style=wx.SIMPLE_BORDER,
              title='Inspector')

        self.gateMediator = gateMediator
        self.up_bmp = wx.Image('../Images/Inspector/Up.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        self.paletteImages = wx.ImageList(height=24, width=24)

        self.toolBar = wx.ToolBar(id=wxID_INSPECTORFRAMETOOLBAR, name='toolBar',
              parent=self, style=wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.CLIP_CHILDREN)
        self.SetToolBar(self.toolBar)

        self.statusBar = wx.StatusBar(id=wxID_INSPECTORFRAMESTATUSBAR,
              name='statusBar', parent=self, style=wx.STB_SIZEGRIP)
        self.statusBar.SetFont(wx.Font(wx.FontInfo(10).Bold()))
        self._init_coll_statusBar_Fields(self.statusBar)
        self.SetStatusBar(self.statusBar)

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
        self.SetIcon(wx.Icon('../Images/Icons/Inspector.ico'))

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
        page3 = EventsWindow(parent = parent, id = -1)

        parent.AddPage(page3, "Page 3")
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

class DefinitionsWindow(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow. __init__(self, parent, -1,
                          style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        self.figure = Figure()
        FigureCanvas(self, -1, self.figure)
        b = Bloch(self.figure)
        b.make_sphere()

    def initSize(self):
        w,h = self.GetClientSize()
        if w == 0 or h == 0: return
        ppiw, ppih = wx.GetDisplayPPI()
        self.figure.set_size_inches( (w / ppiw, w / ppiw))

class EventsWindow(wx.SplitterWindow):
    """ Window that hosts event name values and event category selection """
    def __init__(self, *_args, **_kwargs):
        wx.SplitterWindow.__init__(self, _kwargs['parent'], _kwargs['id'],
          style = wx.SP_LIVE_UPDATE | wx.SP_3DSASH )

        self.categories = wx.SplitterWindow(self, -1,
              style = wx.SP_3D | wx.SP_LIVE_UPDATE)
        self.definitions = DefinitionsWindow(self)

        self.SetMinimumPaneSize(20)
        self.SplitHorizontally(self.categories, self.definitions)
        self.SetSashPosition(100)

        self.categoryClasses = wx.ListCtrl(self.categories, wxID_EVTCATS, style=wx.LC_LIST)
        self.selCatClass = -1
        self.categoryClasses.Bind(wx.EVT_LIST_ITEM_SELECTED,
              self.OnCatClassSelect, id=wxID_EVTCATS)
        self.categoryClasses.Bind(wx.EVT_LIST_ITEM_DESELECTED,
              self.OnCatClassDeselect, id=wxID_EVTCATS)

        self.categoryMacros = wx.ListCtrl(self.categories, wxID_EVTMACS, style=wx.LC_LIST)
        self.categoryMacros.Bind(wx.EVT_LIST_ITEM_SELECTED,
              self.OnMacClassSelect, id=wxID_EVTMACS)
        self.categoryMacros.Bind(wx.EVT_LIST_ITEM_DESELECTED,
              self.OnMacClassDeselect, id=wxID_EVTMACS)
        self.categoryMacros.Bind(wx.EVT_LEFT_DCLICK, self.OnMacroSelect)
        self.Bind(wx.EVT_SIZE, self.onresize)

        self.selMacClass = -1

        self.categories.SetMinimumPaneSize(20)
        self.categories.SplitVertically(self.categoryClasses, self.categoryMacros)
        self.categories.SetSashPosition(80)

    def onresize(self, ev):
        self.definitions.initSize()
        ev.Skip()

    def setInspector(self, inspector):
        self.inspector = inspector

    def readObject(self):
        #clean up all previous items
        self.cleanup()

        # List available categories
        for catCls in self.inspector.selCmp.events():
            self.categoryClasses.InsertStringItem(0, catCls)

    def cleanup(self):
        self.categoryClasses.DeleteAllItems()
        self.categoryMacros.DeleteAllItems()

    def destroy(self):
        self.inspector = None

    def addEvent(self, name, value, wid = None):
        self.inspector.selCmp.persistEvt(name, value, wid)
        self.inspector.selCmp.evtSetter(name, value)


    def macroNameToEvtName(self, macName):
        flds = macName.split('_')
        del flds[0] #remove 'EVT'
        cmpName = self.inspector.selCmp.evtName()
        evtName = 'On'+cmpName[0].upper()+cmpName[1:]
        for fld in flds:
            evtName = evtName + fld.capitalize()
        return evtName

    def extendHelpUrl(self, wxClass, url):
        return wxClass, url

    def initSash(self):
        self.categories.SetSashPosition(80)

        oiEventSelectionHeight = 140
        self.SetSashPosition(oiEventSelectionHeight)

    def OnCatClassSelect(self, event):
        pass

    def OnCatClassDeselect(self, event):
        self.selCatClass = -1
        self.selMacClass = -1
        self.categoryMacros.DeleteAllItems()

    def OnMacClassSelect(self, event):
        self.selMacClass = event.m_itemIndex

    def OnMacClassDeselect(self, event):
        self.selMacClass = -1

    def doAddEvent(self, catClassName, macName):
        pass


    def OnMacroSelect(self, event):
        pass