import threading

from util.Utils import *
from view.Notepad import Notepad
from view.new_circuit.CircuitStd import CircuitStd
from view.old_circuit.Circuit import Circuit

[wxID_EDITORFRAME, wxID_EDITORFRAMESTATUSBAR, wxID_EDITORFRAMETABS,
 wxID_EDITORFRAMETABSSPLITTER, wxID_EDITORFRAMETOOLBAR,
] = [wx.NewId() for _init_ctrls in range(5)]

(wxID_EDITOROPEN, wxID_EDITORSAVE, wxID_EDITORSAVEAS, wxID_EDITORCLOSEPAGE,
 wxID_EDITORREFRESH, wxID_EDITORDESIGNER, wxID_EDITORDEBUG, wxID_EDITORHELP,
 wxID_DEFAULTVIEWS, wxID_EDITORSWITCHTO, wxID_EDITORDIFF, wxID_EDITORPATCH,
 wxID_EDITORTOGGLEVIEW, wxID_EDITORSWITCHEXPLORER, wxID_EDITORSWITCHSHELL,
 wxID_EDITORSWITCHPALETTE, wxID_EDITORSWITCHINSPECTOR,
 wxID_EDITORTOGGLERO, wxID_EDITORHELPFIND, wxID_EDITORRELOAD,
 wxID_EDITORHELPABOUT, wxID_EDITORHELPGUIDE, wxID_EDITORHELPTIPS,
 wxID_EDITORHELPOPENEX,
 wxID_EDITORPREVPAGE, wxID_EDITORNEXTPAGE,
 wxID_EDITORBROWSEFWD, wxID_EDITORBROWSEBACK,
 wxID_EDITOREXITBOA, wxID_EDITOROPENRECENT,
 wxID_EDITORHIDEPALETTE, wxID_EDITORWINDIMS, wxID_EDITORWINDIMSLOAD,
 wxID_EDITORWINDIMSSAVE, wxID_EDITORWINDIMSRESDEFS,
 wxID_EDITORSWITCHPREFS,
) = [wx.NewId() for x in range(36)]

suSocketFileOpenServer = True

keyDefs = {
#--Source View------------------------------------------------------------------
  'Refresh'     : (wx.ACCEL_CTRL, ord('R'), 'Ctrl-R'),
  'Find'        : (wx.ACCEL_CTRL, ord('F'), 'Ctrl-F'),
  'FindAgain'   : (wx.ACCEL_NORMAL, wx.WXK_F3, 'F3'),
  'FindAgainPrev' : (wx.ACCEL_SHIFT, wx.WXK_F3, 'Shift-F3'),
  'ToggleBrk'   : (wx.ACCEL_NORMAL, wx.WXK_F5, 'F5'),
  'Indent'      : (wx.ACCEL_CTRL, ord('I'), 'Ctrl-I'),
  'Dedent'      : (wx.ACCEL_CTRL, ord('U'), 'Ctrl-U'),
  'Comment'     : (wx.ACCEL_ALT, ord('3'), 'Alt-3'),
  'Uncomment'   : (wx.ACCEL_ALT, ord('4'), 'Alt-4'),
  'DashLine'    : (wx.ACCEL_CTRL, ord('B'), 'Ctrl-B'),
  'MarkPlace'   : (wx.ACCEL_CTRL, ord('M'), 'Ctrl-M'),
  'CodeComplete': (wx.ACCEL_CTRL, wx.WXK_SPACE, 'Ctrl-Space'),
  'CallTips'    : (wx.ACCEL_SHIFT|wx.ACCEL_CTRL, wx.WXK_SPACE, 'Ctrl-Shift-Space'),
  'CodeXform'   : (wx.ACCEL_ALT, ord('C'), 'Alt-C'),
  'BrowseTo'    : (wx.ACCEL_CTRL, wx.WXK_RETURN, 'Ctrl-Return'),
  'BrowseFwd'   : (wx.ACCEL_SHIFT|wx.ACCEL_CTRL, ord('K'), 'Ctrl-K'),
  'BrowseBack'  : (wx.ACCEL_SHIFT|wx.ACCEL_CTRL, ord('J'), 'Ctrl-J'),
#-Modules-----------------------------------------------------------------------
  'RunApp'      : (wx.ACCEL_NORMAL, wx.WXK_F9, 'F9'),
  'RunMod'      : (wx.ACCEL_NORMAL, wx.WXK_F10, 'F10'),
  'Close'       : (wx.ACCEL_CTRL, ord('W'), 'Ctrl-W'),
  'Save'        : (wx.ACCEL_CTRL, ord('S'), 'Ctrl-S'),
  'SaveAs'      : (wx.ACCEL_ALT, ord('S'), 'Alt-S'),
  'CheckSource' : (wx.ACCEL_NORMAL, wx.WXK_F2, 'F2'),
  'Debug'       : (wx.ACCEL_NORMAL, wx.WXK_F4, 'F4'),
  'DebugOut'    : (wx.ACCEL_NORMAL, wx.WXK_F6, 'F6'),
  'DebugStep'   : (wx.ACCEL_NORMAL, wx.WXK_F7, 'F7'),
  'DebugOver'   : (wx.ACCEL_NORMAL, wx.WXK_F8, 'F8'),
  'DebugPause'  : (wx.ACCEL_SHIFT, wx.WXK_F4, 'Shift-F4'),
  'DebugStop'   : (wx.ACCEL_CTRL|wx.ACCEL_SHIFT, wx.WXK_F4, 'Ctrl-Shift-F4'),
  'SwitchToApp' : (wx.ACCEL_ALT, ord('A'), 'Alt-A'),
#--General----------------------------------------------------------------------
  'ContextHelp' : (wx.ACCEL_NORMAL, wx.WXK_F1, 'F1'),
  'Open'        : (wx.ACCEL_CTRL, ord('O'), 'Ctrl-O'),
  'Insert'      : (wx.ACCEL_NORMAL, wx.WXK_INSERT, 'Ins'),
  'Delete'      : (wx.ACCEL_NORMAL, wx.WXK_DELETE, 'Del'),
  'Escape'      : (wx.ACCEL_NORMAL, wx.WXK_ESCAPE, 'Esc'),
  'NextPage'    : (wx.ACCEL_CTRL, ord('K'), 'Ctrl-K'),
  'PrevPage'    : (wx.ACCEL_CTRL, ord('J'), 'Ctrl-J'),
  'Inspector'   : (wx.ACCEL_NORMAL, wx.WXK_F11, 'F11'),
  'Designer'    : (wx.ACCEL_NORMAL, wx.WXK_F12, 'F12'),
  'Editor'      : (wx.ACCEL_NORMAL, wx.WXK_F12, 'F12'),
  'GotoLine'    : (wx.ACCEL_CTRL, ord('G'), 'Ctrl-G'),
  'HelpFind'    : (wx.ACCEL_CTRL, ord('H'), 'Ctrl-H'),
  'GotoExplorer': (wx.ACCEL_CTRL, ord('E'), 'Ctrl-E'),
  'GotoShell'   : (wx.ACCEL_CTRL, ord('P'), 'Ctrl-P'),
  'CloseView'   : (wx.ACCEL_CTRL, ord('Q'), 'Ctrl-Q'),
#--Clipboard--------------------------------------------------------------------
  'Cut'         : (wx.ACCEL_SHIFT, wx.WXK_DELETE, 'Shift-Del'),
  'Copy'        : (wx.ACCEL_CTRL, wx.WXK_INSERT, 'Ctrl-Ins'),
  'Paste'       : (wx.ACCEL_SHIFT, wx.WXK_INSERT, 'Shift-Ins'),
#--Designer---------------------------------------------------------------------
  'MoveLeft'    : (wx.ACCEL_CTRL, wx.WXK_LEFT, 'Ctrl-Left'),
  'MoveRight'   : (wx.ACCEL_CTRL, wx.WXK_RIGHT, 'Ctrl-Right'),
  'MoveUp'      : (wx.ACCEL_CTRL, wx.WXK_UP, 'Ctrl-Up'),
  'MoveDown'    : (wx.ACCEL_CTRL, wx.WXK_DOWN, 'Ctrl-Down'),
  'WidthDec'    : (wx.ACCEL_SHIFT, wx.WXK_LEFT, 'Shift-Left'),
  'WidthInc'    : (wx.ACCEL_SHIFT, wx.WXK_RIGHT, 'Shift-Right'),
  'HeightInc'   : (wx.ACCEL_SHIFT, wx.WXK_DOWN, 'Shift-Down'),
  'HeightDec'   : (wx.ACCEL_SHIFT, wx.WXK_UP, 'Shift-Up'),
  'SelectLeft'  : (wx.ACCEL_NORMAL, wx.WXK_LEFT, 'Left'),
  'SelectRight' : (wx.ACCEL_NORMAL, wx.WXK_RIGHT, 'Right'),
  'SelectDown'  : (wx.ACCEL_NORMAL, wx.WXK_DOWN, 'Down'),
  'SelectUp'    : (wx.ACCEL_NORMAL, wx.WXK_UP, 'Up'),
#--Shell------------------------------------------------------------------------
  'HistoryUp'   : (wx.ACCEL_CTRL, wx.WXK_UP, 'Ctrl-Up'),
  'HistoryDown' : (wx.ACCEL_CTRL, wx.WXK_DOWN, 'Ctrl-Down'),
}

def socketFileOpenServerListen(editor):
    # self.closed, self.listener = socketFileOpenServerListen(self)
    closed = threading.Event()
    listener = Listener(editor, closed)
    listener.start()
    return closed, listener


socketPort = 50007
selectTimeout = 0.25
class Listener(threading.Thread):
    def __init__(self, editor, closed):
        #self.queue = queue
        self.editor = editor
        self.closed = closed
        threading.Thread.__init__(self)

    def run(self, host='127.0.0.1', port=socketPort):
        import socket
        from select import select
        # Open a socket and listen.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((host, port))
        except socket.error as err:
            self.closed.set()
            return

        s.listen(5)
        while 1:
            while 1:
                # Listen for 0.25 s, then check if closed is set. In that case,
                # end thread by returning.
                ready, dummy, dummy = select([s],[],[], selectTimeout)
                if self.closed.isSet():
                    return
                if ready:
                    break

            # Accept a connection, read the data and put it into the queue.
            conn, addr = s.accept()
            l = []
            while 1:
                data = conn.recv(1024)
                if not data: break
                l.append(data)
            name = ''.join(l)
            if name.strip():
                wx.CallAfter(self.editor.openOrGotoModule, name)
            conn.close()


class Editor(wx.MDIChildFrame):
    """ Source code editor and host for the Model/View/Controller classes"""

    editorTitle = 'Editor'
    editorIcon = '../Images/Icons/Editor.ico'

    openBmp = 'Images/Editor/Open.png'
    backBmp = '../Images/Shared/Previous.png'
    forwBmp = '../Images/Shared/Next.png'
    recentBmp = 'Images/Editor/RecentFiles.png'
    helpBmp = '../Images/Shared/Help.png'
    helpIdxBmp = '../Images/Shared/CustomHelp.png'
    ctxHelpBmp = 'Images/Shared/ContextHelp.png'
    tipBmp = '../Images/Shared/Tip.png'
    aboutBmp = '../Images/Shared/About.png'
    shellBmp = 'Images/Editor/Shell.png'
    explBmp = '../Images/Editor/Explorer.png'
    inspBmp = '../Images/Shared/Inspector.png'
    paletteBmp = '../Images/Shared/Palette.png'
    prefsBmp = '../Images/Modules/PrefsFolder.png'



    def __init__(self, parent, gateMediator, quantum_computer):

        wx.MDIChildFrame.__init__(self, id=wxID_EDITORFRAME, name='', parent=parent,
              pos=wx.Point(68, 72), size=wx.Size(810, 515),
                                  style=wx.SIMPLE_BORDER,
              title='Editor')
        self.gateMediator = gateMediator

        self.setDefaultSize()
        self.modelImageList = wx.ImageList(height=16, width=16)
        self.blankEditMenu = wx.Menu(title='')
        self.blankViewMenu = wx.Menu(title='')
        self.helpMenu = wx.Menu(title='')
        self.toolsMenu = wx.Menu(title='')

        self.mainMenu = wx.MenuBar()
        self.mainMenu.Append(menu=wx.Menu(), title='File')
        self.mainMenu.Append(menu=wx.Menu(), title='Edit')
        self.mainMenu.Append(menu=wx.Menu(), title='Views')
        self.mainMenu.Append(menu=self.toolsMenu, title='Tools')
        self.SetMenuBar(self.mainMenu)

        self.statusBar = EditorStatusBar(id=wxID_EDITORFRAMESTATUSBAR,
              name='statusBar', parent=self, style=0)

        self.toolBar = EditorToolBar(id=wxID_EDITORFRAMETOOLBAR, name='toolBar',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(802, 250),
              style=wx.TB_HORIZONTAL | wx.NO_BORDER)

        self.tabs = wx.Notebook(id=wxID_EDITORFRAMETABS, name='tabs',
              parent=self, pos=wx.Point(2, 2), size=wx.Size(798,
              417), style=wx.CLIP_CHILDREN)

        self.tabs.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED,
              self.OnTabsNotebookPageChanged, id=wxID_EDITORFRAMETABS)


        self.SetStatusBar(self.statusBar)
        self.SetToolBar(self.toolBar)
        self.SetIcon(wx.Icon(self.editorIcon))

        self.toolAccels = []
        self.tools = {}
        self.numFixedPages = 0

        # Explorer
        self.circuitStd = self.addExplorerPage('CircuitStd', gateMediator=gateMediator, Page=CircuitStd, quantum_computer=quantum_computer)
        self.notepad = self.addExplorerPage('Explorer', gateMediator=gateMediator, Page=Notepad, quantum_computer=quantum_computer)
        # self.circuit = self.addExplorerPage('Circuit', gateMediator, Page=Circuit)

        self.winDimsMenu = wx.Menu()
        self.winDimsMenu.Append(wxID_EDITORWINDIMSLOAD, 'Load',
              'Load window dimensions from the config.')
        self.winDimsMenu.Append(wxID_EDITORWINDIMSSAVE, 'Save',
              'Save window dimensions to the config.')
        self.winDimsMenu.Append(wxID_EDITORWINDIMSRESDEFS,
              'Restore defaults', 'Restore dimensions to defaults')

        self.winMenu =wx.Menu()
        appendMenuItem(self.winMenu, wxID_EDITORSWITCHPALETTE,
              'Palette', '', self.paletteBmp, 'Switch to the Palette frame.')
        appendMenuItem(self.winMenu, wxID_EDITORSWITCHINSPECTOR,
              'Inspector', keyDefs['Inspector'], self.inspBmp,
              'Switch to the Inspector frame.')
        self.winMenu.AppendSeparator()

        appendMenuItem(self.winMenu, wxID_EDITORBROWSEBACK,
              'Browse back', (), self.backBmp, #\t%s'%keyDefs['BrowseBack'][2],
              'Go back in browsing history stack')
        appendMenuItem(self.winMenu, wxID_EDITORBROWSEFWD,
              'Browse forward', (), self.forwBmp, #\t%s'%keyDefs['BrowseFwd'][2],
              'Go forward in browsing history stack')
        appendMenuItem(self.winMenu, wxID_EDITORPREVPAGE,
              'Previous page', keyDefs['PrevPage'], '-',
              'Switch to the previous page of the main notebook')
        appendMenuItem(self.winMenu, wxID_EDITORNEXTPAGE,
              'Next page', keyDefs['NextPage'], '-',
              'Switch to the next page of the main notebook')
        self.winMenu.AppendSeparator()
        self.winMenu.Append(wxID_EDITORWINDIMS,
              'All window dimensions', self.winDimsMenu,
              'Load, save or restore IDE windows dimensions')
        self.winMenu.Append(wxID_EDITORHIDEPALETTE,
              'Hide Palette', 'Hide the Palette frame')
        self.winMenu.AppendSeparator()
        self.mainMenu.Append(self.winMenu, 'Windows')

        # Help menu
        appendMenuItem(self.helpMenu, wxID_EDITORHELP, 'Help',
              (), self.helpBmp, 'Opens help for the Editor')
        self.helpMenu.Append(wxID_EDITORHELPGUIDE,
              'Getting started guide', 'Opens the Getting started guide')
        self.helpMenu.AppendSeparator()
        appendMenuItem(self.helpMenu, wxID_EDITORHELPFIND,
              'Find in index...', keyDefs['HelpFind'], self.helpIdxBmp,
              'Pops up a text input for starting a search of the help indexes')
        self.helpMenu.Append(wxID_EDITORHELPOPENEX, 'Open an example...',
              'Opens file dialog in the Examples directory')
        appendMenuItem(self.helpMenu, wxID_EDITORHELPTIPS,
              'Tips', (), self.tipBmp, 'Opens the "Tip of the Day" window')
        self.helpMenu.AppendSeparator()
        appendMenuItem(self.helpMenu, wxID_EDITORHELPABOUT,
              'About', (), self.aboutBmp, 'Opens the About box')

        helpMenuTitleName = 'Help'
        self.mainMenu.Append(self.helpMenu, helpMenuTitleName)

        # create initial toolbar buttons and menus
        dt = FileDropTarget(self)
        self.SetDropTarget(dt)

        self.tabs.SetMinSize(wx.DefaultSize)

    def stimula(self, shouldStimulate, gate = None):
        self.circuitStd.stimula(shouldStimulate, gate)

    def setDefaultSize(self):
        paletteHeight = 120
        editorScreenWidthPerc = 0.73
        screenX, screenY, screenWidth, screenHeight = wx.GetClientDisplayRect()
        edWidth = int(screenWidth * editorScreenWidthPerc)
        inspWidth = screenWidth - edWidth + 1
        underPalette = paletteHeight + screenY
        bottomHeight = screenHeight - paletteHeight - 65
        windowManagerSide = 5
        self.SetSize(inspWidth + windowManagerSide*2 + screenX - 10, underPalette + screenY,
              edWidth, bottomHeight)

    def OnTabsNotebookPageChanged(self, ev):
        pass


    def OnHelpToolClick(self, ev):
        pass

    def OnWxWinHelpToolClick(self, ev):
        pass

    def OnPythonHelpToolClick(self, ev):
        pass

    def addExplorerPage(self, name, gateMediator, Page, quantum_computer):
        explorerPage = Page(self.tabs, gateMediator, quantum_computer)
        self.tabs.AddPage(explorerPage, name, imageId=wx.NewId())
        self.numFixedPages += 1
        return explorerPage


sbfIcon, sbfBrwsBtns, sbfStatus, sbfCrsInfo, sbfProgress = range(5)

class EditorStatusBar(wx.StatusBar):
    """ Displays information about the current view. Also global stats/
        progress bar etc. """
    maxHistorySize = 250
    def __init__(self, *_args, **_kwargs):
        wx.StatusBar.__init__(self, _kwargs['parent'], _kwargs['id'], style=wx.STB_SIZEGRIP)
        self.SetFieldsCount(6)
        imgWidth = 16

        self.SetStatusWidths([imgWidth, 36, 400, 25, 150, -1])

        rect = self.GetFieldRect(sbfIcon)
        self.img = wx.StaticBitmap(self, -1,
            wx.Image('../Images/Shared/BoaLogo.png').ConvertToBitmap(),
            (rect.x+1, rect.y+1), (16, 16))

        rect = self.GetFieldRect(sbfBrwsBtns)
        self.historyBtnBack = wx.BitmapButton(self, -1,
              wx.Image('../Images/Shared/PreviousSmall.png').ConvertToBitmap(),
              (rect.x+1, rect.y+1), (int(round(rect.width/2.0))-1, rect.height-2))
        self.historyBtnFwd = wx.BitmapButton(self, -1,
              wx.Image('../Images/Shared/NextSmall.png',wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
              (rect.x+1+int(round(rect.width/2.0)), rect.y+1), (int(round(rect.width/2.0))-1, rect.height-2))

        tip = 'Browse the Traceback/Error/Output window history.'
        self.historyBtnBack.SetToolTip(tip)
        self.historyBtnFwd.SetToolTip(tip)

        self.erroutFrm = None

        self.progress = wx.Gauge(self, -1, 100)
        self.linkProgressToStatusBar()

        self.images = {'Info': wx.Image('../Images/Shared/Info.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
                       'Warning': wx.Image('../Images/Shared/Warning.png',wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
                       'Error': wx.Image('../Images/Shared/Error.png',wx.BITMAP_TYPE_PNG).ConvertToBitmap()}
        self.history = []
        self._histcnt = 0

    def linkProgressToStatusBar(self):
        rect = self.GetFieldRect(sbfProgress)
        self.progress.SetSize(rect.x+1, rect.y+1, rect.width -2, rect.height -2)


class EditorToolBar(wx.ToolBar):
    def __init__(self, *_args, **_kwargs):
        frame = _kwargs['parent']
        wx.ToolBar.__init__(self, frame, _kwargs['id'],
          style=wx.TB_HORIZONTAL | wx.NO_BORDER|wx.TB_FLAT)
        self.toolLst = []
        self.toolCount = 0
        self.SetToolBitmapSize((16, 16))
        AddToolButtonBmpObject(frame, self,wx.Image('../Images/Shared/Previous.png').ConvertToBitmap(), 'Python help', frame.OnPythonHelpToolClick)
        AddToolButtonBmpObject(frame, self,wx.Image('../Images/Shared/Next.png').ConvertToBitmap(), 'Python help', frame.OnPythonHelpToolClick)
        AddToolButtonBmpObject(frame, self,wx.Image('../Images/Shared/Delete.png').ConvertToBitmap(), 'Python help', frame.OnPythonHelpToolClick)
        AddToolButtonBmpObject(frame, self, wx.Image('../Images/Shared/Help.png').ConvertToBitmap(), 'Simulator or selected component help', frame.OnHelpToolClick)
        AddToolButtonBmpObject(frame, self, wx.Image('../Images/Shared/wxWinHelp.png').ConvertToBitmap(), 'wxPython help', frame.OnWxWinHelpToolClick)
        AddToolButtonBmpObject(frame, self,wx.Image('../Images/Shared/PythonHelp.png').ConvertToBitmap(), 'Python help', frame.OnPythonHelpToolClick)
        self.Realize()

    def AddSeparator(self):
        wx.ToolBar.AddSeparator(self)
        self.toolLst.append(-1)
        self.toolCount = self.toolCount + 1

    def DeleteTool(self, id):
        wx.ToolBar.DeleteTool(self, id)
        self.toolLst.remove(id)
        self.toolCount = self.toolCount - 1

    def ClearTools(self):
        posLst = range(self.toolCount)
        # posLst.reverse()
        for pos in posLst:
            self.DeleteToolByPos(pos)

        self.DisconnectToolIds()

        self.toolLst = []
        self.toolCount = 0

    def GetToolPopupPosition(self, id):
        margins =  self.GetMargins() # self.GetToolMargins()
        toolSize = self.GetToolSize()
        xPos = margins.x
        for tId in self.toolLst:
            if tId == id:
                return wx.Point(xPos, margins.y + toolSize.y)

            if tId == -1:
                xPos = xPos + self.GetToolSeparation()
            else:
                xPos = xPos + toolSize.x

        return wx.Point(0, 0)

    def PopupToolMenu(self, toolId, menu):
        self.PopupMenu(menu, self.GetToolPopupPosition(toolId))

    def DisconnectToolIds(self):
        for wid in self.toolLst:
            if wid != -1:
                self.GetParent().Disconnect(wid)


class FileDropTarget(wx.FileDropTarget):
    def __init__(self, editor):
        wx.FileDropTarget.__init__(self)
        self.editor = editor

    def OnDropFiles(self, x, y, filenames):
        wx.BeginBusyCursor()
        try:
            for filename in filenames:
                # self.editor.openOrGotoModule(filename)
                print (filename)
        finally:
            wx.EndBusyCursor()
        return True