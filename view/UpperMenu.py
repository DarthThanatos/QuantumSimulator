import wx
import wx.lib.buttons

[wxID_BOAFRAME, wxID_BOAFRAMEPALETTE, wxID_BOAFRAMETOOLBAR,
] = [wx.NewId() for _init_ctrls in range(3)]

[wxID_BOAFRAMETOOLBARTOOLS0, wxID_BOAFRAMETOOLBARTOOLS1,
] = [wx.NewId() for _init_coll_toolBar_Tools in range(2)]

class UpperMenu(wx.MDIChildFrame):

    palettePages =[]

    def __init__(self, parent):
        wx.MDIChildFrame.__init__(self,
              id=wxID_BOAFRAME, name='', parent=parent, pos=wx.Point(116, 275),
              size=wx.Size(645, 74), style=   wx.SIMPLE_BORDER,
              title="SimQuant - Python Quantum scripts IDE & Quantum Gates Builder")

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
        self.SetDimensions(screenX, screenY,
            screenWidth - windowManagerSide * 2 + 11,
            paletteHeight)

    def initUpperMenu(self, inspector, editor):
        self.inspector = inspector
        self.editor = editor
        palettePage = NewPalettePage(self.palette, "New",
              '../Images/Palette/', self)
        paletteLists = {'New': ["X", "Y", "Z", "T", "H"]}

        for modelName in paletteLists['New']:
            palettePage.addButton2(modelName,
                ButtonConstrClass(),
                wx.lib.buttons.GenBitmapButton)

        self.palettePages.append(palettePage)


    def addTool(self, filename, text, help, func, toggle = False):
        mID = wx.NewId()
        self.toolBar.AddTool(toolId = mID, bitmap = wx.Image(filename+'.png').ConvertToBitmap(),
          shortHelp = text, label="")
        self.Bind(wx.EVT_TOOL, func, id=mID)
        return mID

    def OnInspectorToolClick(self, event):
        self.inspector.restore()

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
        self.editor.addNewPage(name, controller)

    # noinspection PyMethodOverriding
    def Iconize(self, iconize):
        wx.Frame.Iconize(self, iconize)

    def OnBoaframeIconize(self, event):
        self.SetFocus()
        event.Skip()

class PanelPalettePage(wx.Panel):
    buttonSep = 11
    buttonBorder = 7
    def __init__(self, parent, name, bitmapPath, palette):
        # default size provided for better sizing on GTK where notebook page
        # size isn't available at button creation time
        wx.Panel.__init__(self, parent, -1, size=(44, 44))

        self.palette = palette
        self.name = name
        self.bitmapPath = bitmapPath
        self.buttons = {}
        parent.AddPage(self, name)
        self.posX = int(round(self.buttonSep/2.0))
        self.posY = int(round((self.GetSize().y -(75+self.buttonBorder) + 4)/2.0))
        self.menu =wx.Menu()


    def addButton(self, widgetName, wxClass, constrClass, clickEvt, hintFunc,
                  hintLeaveFunc, btnType):
        mID = wx.NewId()
        self.menu.Append(mID, widgetName, '', False)
        self.palette.Bind(wx.EVT_MENU, clickEvt, id=mID)


        bmp = self.getButtonBmp(widgetName, wxClass)
        width = bmp.GetWidth() + self.buttonBorder
        height = bmp.GetHeight() + self.buttonBorder

        _, _, screenWidth, _ = wx.GetClientDisplayRect()
        btnXOffs = (screenWidth - 5 * 75)/ 2
        newButton = btnType(self, mID, None, wx.Point(self.posX + btnXOffs, self.posY),
                           wx.Size(width, height))

        newButton.SetBezelWidth(1)
        newButton.SetUseFocusIndicator(0)
        newButton.SetToolTipString(widgetName)
        try:
            newButton.SetBitmapLabel(bmp, False)
        except TypeError:
            newButton.SetBitmapLabel(bmp)

        self.Bind(wx.EVT_BUTTON, clickEvt, id=mID)

        self.buttons[widgetName] = newButton
        self.posX = self.posX + bmp.GetWidth() + 11

        return mID

    def getButtonBmp(self, name, wxClass):
        return wx.Image('../Images/Palette/Component.png').ConvertToBitmap()

class NewPalettePage(PanelPalettePage):
    def __init__(self, parent, name, bitmapPath, palette):
        PanelPalettePage.__init__(self, parent, name, bitmapPath,  palette)


    def addButton(self, widgetName, wxClass, constrClass, clickEvt, hintFunc,
                  hintLeaveFunc, btnType):
        mID = PanelPalettePage.addButton(self, widgetName, wxClass, constrClass,
              clickEvt, hintFunc, hintLeaveFunc, btnType)
        return mID

    def addButton2(self, name, Controller, btnType):
        mID = PanelPalettePage.addButton(self, name, Controller, None,
              self.OnClickTrap, None, None, btnType)

        return mID

    def getButtonBmp(self, name, wxClass):
        try:
            return wx.Image('%s%s.png' %(self.bitmapPath, name)).ConvertToBitmap()
        except:
            return wx.Image('../Images/Palette/Component.png').ConvertToBitmap()

    def OnClickTrap(self, event):
        pass

class ButtonConstrClass:
    pass

class PalettePage(PanelPalettePage):
    def __init__(self, parent, name, bitmapPath, palette):
        PanelPalettePage.__init__(self, parent, name, bitmapPath, palette)

    def addToggleBitmaps(self, classes, hintFunc, hintLeaveFunc):
        for wxClass in classes:
            self.addButton("empty", wxClass, ButtonConstrClass(), self.OnClickTrap, hintFunc,
                  hintLeaveFunc, wx.lib.buttons.GenBitmapToggleButton)

    def OnClickTrap(self, event):
        pass

