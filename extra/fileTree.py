import os

import re
import  wx

#----------------------------------------------------------------------

class TestPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        txt1 = wx.StaticText(self, -1, "style=0")
        dir1 = wx.GenericDirCtrl(self, -1, size=(200,225), style=0)

        txt2 = wx.StaticText(self, -1, "wx.DIRCTRL_DIR_ONLY")
        dir2 = wx.GenericDirCtrl(self, -1, size=(200,225), style=wx.DIRCTRL_DIR_ONLY|wx.DIRCTRL_MULTIPLE)

        txt3 = wx.StaticText(self, -1, "wx.DIRCTRL_SHOW_FILTERS")
        dir3 = wx.GenericDirCtrl(self, -1, size=(200,225), style=wx.DIRCTRL_SHOW_FILTERS,
                                filter="All files (*.*)|*.*|Python files (*.py)|*.py")

        sz = wx.FlexGridSizer(cols=3, hgap=5, vgap=5)
        sz.Add((35, 35))  # some space above
        sz.Add((35, 35))
        sz.Add((35, 35))

        sz.Add(txt1)
        sz.Add(txt2)
        sz.Add(txt3)

        sz.Add(dir1, 0, wx.EXPAND)
        sz.Add(dir2, 0, wx.EXPAND)
        sz.Add(dir3, 0, wx.EXPAND)

        sz.Add((35,35))  # some space below

        sz.AddGrowableRow(2)
        sz.AddGrowableCol(0)
        sz.AddGrowableCol(1)
        sz.AddGrowableCol(2)

        self.SetSizer(sz)
        self.SetAutoLayout(True)

    def get_item_by_label(self, tree, search_text, root_item):
        item, cookie = tree.GetFirstChild(root_item)
        while item.IsOk():
            text = tree.GetItemText(item)
            if text.lower() == search_text.lower():
                return item
            if tree.ItemHasChildren(item):
                match = self.get_item_by_label(tree, search_text, item)
                if match.IsOk():
                    return match
            item, cookie = tree.GetNextChild(root_item, cookie)

        return wx.TreeItemId()

    def newgdc(self, parent):
        dirTree = wx.GenericDirCtrl(parent, -1, style=wx.DIRCTRL_SHOW_FILTERS | wx.DIRCTRL_SELECT_FIRST,
                          filter="All files (*.*)|*.*|Python files (*.py)|*.py")

        cwd =  os.getcwd()
        C_root, subdir, _, _ = re.findall(r'(C:\\)((\w+\\)+)(\w+)', cwd)[0]
        workspacePath = C_root + subdir + "workspace"
        # dirTree.ExpandPath(workspacePath)

        dirTree.SetDefaultPath(workspacePath)
        dirTree.SetPath(workspacePath)

        tree = dirTree.GetTreeCtrl()
        res = self.get_item_by_label(tree, "workspace", tree.GetRootItem())
        print(res.IsOk())

        dirTree.GetChildren()[1].SetSize(-1, 30)
        # print(dirTree.GetChildren()[0])
        return dirTree

class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None)
        self.SetTitle('My Title')
        self.SetClientSize((500, 500))
        self.Center()
        self.view = TestPanel(self)

def main():
    app = wx.App(False)
    frame = Frame()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()