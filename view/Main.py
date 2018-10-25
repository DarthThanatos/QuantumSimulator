import wx

from view.LoadingScreen import LoadingScreen
from view.Inspector import Inspector
from view.UpperMenu import UpperMenu
from view.Editor import Editor
import re

from win32api import GetSystemMetrics
import os

# when working in intellij, we already are in the "view" directory.
# If one wishes to run this code from a console, the root dir is "Simulator", thus all relative images paths break.
# the code below adjusts the working directory, so there is no need to change images paths throughout the project
# in case we want to execute the code from a different booting tool(whether from ide or console).

cwd = os.getcwd()
path_parts = re.findall(r'(C:\\)((\w+\\)+)(\w+)', cwd)[0]
if path_parts[3] != "view":
    os.chdir("view")

class SimulatorApp(wx.App):

    def __init__(self):
        wx.App.__init__(self)

    def OnInit(self):
        wx.ToolTip.Enable(True)

        frame = wx.MDIParentFrame(None, title="Hello Simulator", size=(GetSystemMetrics(0),GetSystemMetrics(1)))
        frame.Maximize(True)
        self.frame = frame


        menubar = wx.MenuBar()
        menubar.Append(self.newMenu(), "File")
        frame.SetMenuBar(menubar)
        frame.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        loadingScreen = LoadingScreen(None, self.OnLoaded)
        loadingScreen.Show()
        loadingScreen.Update()

        inspector = Inspector(frame)
        inspector.Show()

        self.main = UpperMenu(frame)
        self.main.initUpperMenu(inspector, frame)
        self.main.Show()

        editor = Editor(frame, wx.NewId(), inspector)
        editor.Show()
        return True

    def OnLoaded(self):
        self.frame.Show()

    def newMenu(self):
        menu = wx.Menu()
        menu.Append(5000, "New Window")
        menu.Append(5001, "Exit")
        return menu

    def OnCloseWindow(self, event):
        self.frame.Destroy()

def main():
    app = SimulatorApp()
    app.MainLoop()

if __name__ == '__main__':
    main()