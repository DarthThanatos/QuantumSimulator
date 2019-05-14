import sys

from util.Utils import get_screen_w_h

sys.setrecursionlimit(5000)
import wx

from model.QuantumComputer import QuantumComputer
from view.GateMediator import GateMediator
from view.LoadingScreen import LoadingScreen
from view.UpperMenu import UpperMenu
from view.Editor import Editor
import re
import os
import multiprocessing


class SimulatorApp(wx.App):

    def OnKeyUP(self, event):
        keyCode = event.GetKeyCode()
        if keyCode == wx.WXK_ESCAPE:
            self.gateMediator.gateUnselected()
        event.Skip()

    def OnRMClicked(self, ev):
        self.gateMediator.gateUnselected()

    def OnInit(self):
        wx.ToolTip.Enable(True)
        frame = wx.MDIParentFrame(None, title="QuCharm", size=get_screen_w_h())
        frame.Maximize(True)
        quantum_computer = QuantumComputer(nqbits=3)
        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyUP)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRMClicked)
        self.frame = frame


        menubar = wx.MenuBar()
        menubar.Append(self.newMenu(), "File")
        frame.SetMenuBar(menubar)
        frame.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        loadingScreen = LoadingScreen(None, self.OnLoaded)
        loadingScreen.Show()
        loadingScreen.Update()

        self.gateMediator = GateMediator()

        editor = Editor(frame, self.gateMediator, quantum_computer)
        editor.Show()

        self.main = UpperMenu(frame, self.gateMediator, quantum_computer)
        self.main.initUpperMenu()
        self.main.Show()

        self.gateMediator.set_frame(frame)
        return True

    def OnLoaded(self):
        self.frame.Show()

    def newMenu(self):
        menu = wx.Menu()
        menu.Append(5000, "New Window")
        menu.Append(5001, "Exit")
        return menu

    def OnCloseWindow(self, event):
        self.gateMediator.window_closing()
        self.frame.Destroy()

def main():
    multiprocessing.freeze_support()

    # When working in intellij, we already are in the "view" directory.
    # If one wishes to run this code from a console, the root dir is "Simulator", thus all relative images paths break.
    # The code below adjusts the working directory, so there is no need to change images paths throughout the project
    # in case we want to execute the code from a different booting tool(whether from ide or console).

    cwd = os.getcwd()
    path_parts = re.findall(r'(C:\\)((\w+\\)+)(\w+)', cwd)[0]
    if path_parts[3] != "view":
        os.chdir("view")

    app = SimulatorApp()
    app.MainLoop()


if __name__ == '__main__':
    main()