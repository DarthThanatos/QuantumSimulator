import wx
import wx.lib.buttons

[wxID_BOAFRAME, wxID_BOAFRAMEPALETTE, wxID_BOAFRAMETOOLBAR,
] = [wx.NewId() for _init_ctrls in range(3)]

[wxID_BOAFRAMETOOLBARTOOLS0, wxID_BOAFRAMETOOLBARTOOLS1,
] = [wx.NewId() for _init_coll_toolBar_Tools in range(2)]

class UpperMenu(wx.MDIChildFrame):

    palettePages =[]

    def __init__(self, parent, gateMediator):
        wx.MDIChildFrame.__init__(self,
              id=wxID_BOAFRAME, name='', parent=parent, pos=wx.Point(116, 275),
              size=wx.Size(645, 74), style=   wx.SIMPLE_BORDER,
              title="SimQuant - Python Quantum scripts IDE & Quantum Gates Builder")
        self.gateMediator = gateMediator

        self.toolBar = wx.ToolBar(id=wxID_BOAFRAMETOOLBAR, name='toolBar',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(637, 24),
              style=wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT)
        self.palette = wx.Notebook(id=wxID_BOAFRAMEPALETTE, name='palette',
              parent=self, pos=wx.Point(0, 24), size=wx.Size(637, 23), style=0)
        self.toolBar.AddTool(bitmap= wx.Image('../Images/Shared/Inspector.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
              toolId=wxID_BOAFRAMETOOLBARTOOLS0, label="",
              shortHelp='Brings the Inspector to the front')
        self.toolBar.AddTool(bitmap= wx.Image('../Images/Shared/Editor.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
              toolId=wxID_BOAFRAMETOOLBARTOOLS1, label="",
              shortHelp='Brings the Editor to the front')
        self.toolBar.AddSeparator()
        self.addTool('../Images/Shared/Help', 'Simulator or selected component help',
              'Show help', self.OnHelpToolClick)
        self.addTool('../Images/Shared/wxWinHelp', 'wxPython help',
              'Show help', self.OnWxWinHelpToolClick)
        self.addTool('../Images/Shared/PythonHelp', 'Python help',
              'Show help', self.OnPythonHelpToolClick)

        self.SetToolBar(self.toolBar)
        self.toolBar.Realize()
        self.setDefaultSize()
        self.SetIcon(wx.Icon('../Images/Icons/Boa.ico'))

        self.Bind(wx.EVT_ICONIZE, self.OnBoaframeIconize)
        self.Bind(wx.EVT_TOOL, self.OnInspectorToolClick,
              id=wxID_BOAFRAMETOOLBARTOOLS0)
        self.Bind(wx.EVT_TOOL, self.OnEditorToolClick,
              id=wxID_BOAFRAMETOOLBARTOOLS1)

    def setDefaultSize(self):
        screenX, screenY, screenWidth, screenHeight = wx.GetClientDisplayRect()
        windowManagerSide = 5
        paletteHeight = 120
        self.SetSize(screenX, screenY,
            screenWidth - windowManagerSide * 2 + 11,
            paletteHeight)

    def initUpperMenu(self):
        palettePage = PanelPalettePage(self.palette, "New",
              '../Images/Palette/', self, self.gateMediator)
        paletteLists = {'New': ["X", "Y", "Z", "T", "H"]}

        for modelName in paletteLists['New']:
            palettePage.addGateButton(modelName, wx.lib.buttons.GenBitmapButton)

        self.palettePages.append(palettePage)

    def addTool(self, filename, text, help, func, toggle = False):
        mID = wx.NewId()
        self.toolBar.AddTool(toolId = mID, bitmap = wx.Image(filename+'.png').ConvertToBitmap(),
          shortHelp = text, label="")
        self.Bind(wx.EVT_TOOL, func, id=mID)
        return mID

    def OnInspectorToolClick(self, event):
        pass

    def OnEditorToolClick(self, event):
        pass

    def OnHelpToolClick(self, event):
        pass

    def OnWxWinHelpToolClick(self, event):
        pass

    def OnPythonHelpToolClick(self, event):
        pass

    def OnCustomHelpToolClick(self, event):
        pass

    def OnFileExit(self, event):
        self.Close()

    def OnDialogPaletteClick(self, event):
        pass

    def OnZopePaletteClick(self, event):
        pass

    def OnComposeClick(self, event):
        pass

    def OnInheritClick(self, event):
        pass

    def OnCloseClick(self, event):
        self.Close()


    def OnCreateNew(self, name, controller):
        pass

    # noinspection PyMethodOverriding
    def Iconize(self, iconize):
        wx.Frame.Iconize(self, iconize)

    def OnBoaframeIconize(self, event):
        self.SetFocus()
        event.Skip()

class PanelPalettePage(wx.Panel):
    buttonSep = 11
    buttonBorder = 7
    def __init__(self, parent, name, bitmapPath, palette, gateMediator):
        # default size provided for better sizing on GTK where notebook page
        # size isn't available at button creation time
        wx.Panel.__init__(self, parent, -1, size=(44, 44))
        self.gateMediator = gateMediator
        self.palette = palette
        self.name = name
        self.bitmapPath = bitmapPath
        self.buttons = {}
        parent.AddPage(self, name)
        self.posX = int(round(self.buttonSep/2.0))
        self.posY = int(round((self.GetSize().y -(75+self.buttonBorder) + 4)/2.0))
        self.menu = wx.Menu()


    def addButton(self, btnName, clickEvt, btnType):
        mID = wx.NewId()
        self.menu.Append(mID, btnName, '', False)
        self.palette.Bind(wx.EVT_MENU, clickEvt, id=mID)


        bmp = self.getButtonBmp(btnName)
        width = bmp.GetWidth() + self.buttonBorder
        height = bmp.GetHeight() + self.buttonBorder

        _, _, screenWidth, _ = wx.GetClientDisplayRect()
        btnXOffs = (screenWidth - 5 * 75)/ 2
        newButton = btnType(self, mID, None, wx.Point(self.posX + btnXOffs, self.posY),
                           wx.Size(width, height))

        newButton.SetBezelWidth(1)
        newButton.SetUseFocusIndicator(0)
        newButton.SetToolTip(btnName)
        try:
            newButton.SetBitmapLabel(bmp, False)
        except TypeError:
            newButton.SetBitmapLabel(bmp)

        self.Bind(wx.EVT_BUTTON, clickEvt, id=mID)

        self.buttons[btnName] = newButton
        self.posX = self.posX + bmp.GetWidth() + 11

        return mID

    def addGateButton(self, name, btnType):
        def gate_btn_fun(event):
            self.gateMediator.gateSelected(name)
            self.GetParent().GetParent().GetParent().SetCursor(wx.Cursor(wx.Image('../Images/Palette/{}.png'.format(name))))
        mID = PanelPalettePage.addButton(self, name, gate_btn_fun, btnType)

        return mID

    def getButtonBmp(self, name):
        try:
            return wx.Image('%s%s.png' %(self.bitmapPath, name)).ConvertToBitmap()
        except:
            return wx.Image('../Images/Palette/Component.png').ConvertToBitmap()
