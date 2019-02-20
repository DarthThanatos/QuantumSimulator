import wx 
import os 
import re 

def get_workspace_path():
    cwd = os.getcwd()
    C_root, subdir, _, _ = re.findall(r'(C:\\)((\w+\\)+)(\w+)', cwd)[0]
    workspacePath = C_root + subdir + "workspace"
    return workspacePath

dialog = wx.FileDialog(
	None,
	defaultDir=get_workspace_path(),
	message="Choose new file name",
	wildcard="*.py",
	style=wx.FD_SAVE
)

if dialog.ShowModal() == wx.ID_OK:
	pass