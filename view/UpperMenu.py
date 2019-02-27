import wx
import wx.lib.buttons
from model.constants import *
from view.QuantumWalkDialog import QuantumWalkDialog

[wxID_BOAFRAME, wxID_BOAFRAMEPALETTE, wxID_BOAFRAMETOOLBAR,
] = [wx.NewId() for _init_ctrls in range(3)]

[wxID_BOAFRAMETOOLBARTOOLS0, wxID_BOAFRAMETOOLBARTOOLS1,
] = [wx.NewId() for _init_coll_toolBar_Tools in range(2)]

class UpperMenu(wx.MDIChildFrame):

    palettePages =[]

    def __init__(self, parent, gateMediator, quantum_computer):
        wx.MDIChildFrame.__init__(self,
              id=wxID_BOAFRAME, name='', parent=parent, pos=wx.Point(116, 275),
              size=wx.Size(645, 74), style=   wx.SIMPLE_BORDER,
              title="SimQuant - Python Quantum scripts IDE & Quantum Gates Builder")
        self.gateMediator = gateMediator
        self.__quantum_computer = quantum_computer

        self.toolBar = wx.ToolBar(id=wxID_BOAFRAMETOOLBAR, name='toolBar',
              parent=self, pos=wx.Point(0, 0), size=wx.Size(637, 24),
              style=wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT)
        self.palette = wx.Notebook(id=wxID_BOAFRAMEPALETTE, name='palette',
              parent=self, pos=wx.Point(0, 24), size=wx.Size(637, 23), style=0)
        self.toolBar.AddTool(bitmap= wx.Image('../Images/Shared/Inspector.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap(),
              toolId=wxID_BOAFRAMETOOLBARTOOLS0, label="", shortHelp='Run quantum walk!')
        self.toolBar.AddSeparator()
        self.addTool('../Images/Shared/Help', 'Simulator or selected component help', 'Show help')
        self.addTool('../Images/Shared/wxWinHelp', 'wxPython help', 'Show help')
        self.addTool('../Images/Shared/PythonHelp', 'Python help', 'Show help')

        self.SetToolBar(self.toolBar)
        self.toolBar.Realize()
        self.setDefaultSize()
        self.SetIcon(wx.Icon('../Images/Icons/Boa.ico'))

        self.Bind(wx.EVT_ICONIZE, self.OnBoaframeIconize)
        self.Bind(wx.EVT_TOOL, self.OnInspectorToolClick,
              id=wxID_BOAFRAMETOOLBARTOOLS0)

    def setDefaultSize(self):
        screenX, screenY, screenWidth, screenHeight = wx.GetClientDisplayRect()
        windowManagerSide = 5
        paletteHeight = 120
        self.SetSize(screenX, screenY,
            screenWidth - windowManagerSide * 2 + 11,
            paletteHeight)

    def initUpperMenu(self):
        palettePage = PanelPalettePage(self.palette, "Gates",
              '../Images/Palette/', self, self.gateMediator)
        paletteLists = {'Gates': [X, Y, Z, ROTATION_X, ROTATION_Y, ROTATION_Z, H, SQRT_X, PHASE_KICK, PHASE_SCALE, C_PHASE_KICK, INV_C_PHASE_KICK, U, MEASURE]}

        for modelName in paletteLists['Gates']:
            palettePage.addGateButton(modelName, wx.lib.buttons.GenBitmapButton)

        self.palettePages.append(palettePage)

    def addTool(self, filename, text, help, func=None, toggle = False):
        mID = wx.NewId()
        self.toolBar.AddTool(toolId = mID, bitmap = wx.Image(filename+'.png').ConvertToBitmap(),
          shortHelp = text, label="")
        if func:
            self.Bind(wx.EVT_TOOL, func, id=mID)
        return mID

    def OnInspectorToolClick(self, event):
        quantum_walk_dialog = QuantumWalkDialog(self, self.__quantum_computer)
        quantum_walk_dialog.ShowModal()
        quantum_walk_dialog.Destroy()

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
        newButton = btnType(self, mID, None, wx.Point(self.posX + btnXOffs, self.posY + 15),
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
        mID = PanelPalettePage.addButton(self, name, gate_btn_fun, btnType)

        return mID

    def getButtonBmp(self, name):
        try:
            return wx.Image('%s%s.png' %(self.bitmapPath, name)).ConvertToBitmap()
        except:
            return wx.Image('../Images/Palette/Component.png').ConvertToBitmap()
