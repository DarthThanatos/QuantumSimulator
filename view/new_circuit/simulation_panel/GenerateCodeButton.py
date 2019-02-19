import wx

from util.Utils import get_workspace_path


class GenerateCodeButton(wx.Button):

    def __init__(self, parent, gate_mediator, quantum_computer):
        wx.Button.__init__(self, parent, label="Generate code", size=(125,25))
        self.__gate_mediator = gate_mediator
        self.__quantum_computer = quantum_computer
        self.Bind(wx.EVT_BUTTON, self.__on_click)

    def __on_click(self, event):
        dialog = wx.FileDialog(
            self,
            defaultDir=get_workspace_path(),
            message="Choose new file name",
            wildcard="*.py",
            style=wx.FD_SAVE
        )
        if dialog.ShowModal() == wx.ID_OK:
            file_name = dialog.GetPath()
            self.__gate_mediator.generate_code(self.__quantum_computer, file_name)
