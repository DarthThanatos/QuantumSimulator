import re
import wx.stc as stc

import keyword
import wx, os


class CodeNotebook(wx.Notebook):

    def __init__(self, parent, rootPath):
        wx.Notebook.__init__(self, parent, style=wx.CLIP_CHILDREN)
        self.openCards = {}
        self.rootPath = rootPath

    def newTabIfNotExists(self, fileToOpen):
        with open(fileToOpen, "r") as f:
            cardName = fileToOpen.split(self.rootPath)
            cardName = cardName[1][1:] # [1:] -> cutting off the first slash
            if self.openCards.__contains__(cardName):
                self.openCards[cardName].SetValue(f.read())
            else:
                ta = self.newTextArea(cardName)
                ta.SetValue(f.read())
                self.openCards[cardName] = ta
                self.AddPage(ta, cardName)
            self.SetSelection(self.SetSelection(self.findPageByName(cardName)))

    def findPageByName(self, cardName):
        for i in range (self.GetPageCount()):
            if self.GetPageText(i) == cardName:
                return i
        return None

    def newTextArea(self, title):
        self.textArea = stc.StyledTextCtrl(parent=self, style=wx.TE_MULTILINE)
        with open("../workspace/{}".format(title), "r") as f:
            self.textArea.SetValue(f.read())
        self.textArea.SetLexer(stc.STC_LEX_PYTHON)
        self.textArea.SetStyleBits(5)
        self.textArea.SetMarginWidth(0, 10)
        self.textArea.SetMarginType(0, wx.stc.STC_MARGIN_NUMBER)
        faces = {'times': 'Times New Roman',
                 'mono': 'Courier New',
                 'helv': 'Arial',
                 'other': 'Comic Sans MS',
                 'size': 10,
                 'size2': 8,
                 }
        self.textArea.SetKeyWords(0, " ".join(keyword.kwlist))
        self.textArea.StyleSetSpec(stc.STC_P_DEFAULT, "fore:#000000,face:%(helv)s,size:%(size)d" % faces)
        self.textArea.StyleSetSpec(stc.STC_P_COMMENTLINE, "fore:#007F00,face:%(other)s,size:%(size)d" % faces)
        self.textArea.StyleSetSpec(stc.STC_P_NUMBER, "fore:#007F7F,size:%(size)d" % faces)
        self.textArea.StyleSetSpec(stc.STC_P_STRING, "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces)
        self.textArea.StyleSetSpec(stc.STC_P_CHARACTER, "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces)
        self.textArea.StyleSetSpec(stc.STC_P_WORD, "fore:#00007F,bold,size:%(size)d" % faces)
        self.textArea.StyleSetSpec(stc.STC_P_TRIPLE, "fore:#7F0000,size:%(size)d" % faces)
        self.textArea.StyleSetSpec(stc.STC_P_TRIPLEDOUBLE, "fore:#7F0000,size:%(size)d" % faces)
        self.textArea.StyleSetSpec(stc.STC_P_CLASSNAME, "fore:#0000FF,bold,underline,size:%(size)d" % faces)
        self.textArea.StyleSetSpec(stc.STC_P_DEFNAME, "fore:#007F7F,bold,size:%(size)d" % faces)
        self.textArea.StyleSetSpec(stc.STC_P_OPERATOR, "bold,size:%(size)d" % faces)
        self.textArea.StyleSetSpec(stc.STC_P_IDENTIFIER, "fore:#000000,face:%(helv)s,size:%(size)d" % faces)
        self.textArea.StyleSetSpec(stc.STC_P_COMMENTBLOCK, "fore:#7F7F7F,size:%(size)d" % faces)
        self.textArea.StyleSetSpec(stc.STC_P_STRINGEOL, "fore:#000000,face:%(mono)s,back:#E0C0E0,eol,size:%(size)d" % faces)
        self.textArea.SetCaretForeground("BLUE")
        return self.textArea


class MyTree(wx.TreeCtrl):
    def __init__(self, parent, rootPath, notebook):
        super(MyTree, self).__init__(parent)
        self.__collapsing = True
        self.rootPath = rootPath
        self.notebook = notebook

        il = wx.ImageList(16, 16)
        self.folderidx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (16, 16)))
        self.fileidx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16, 16)))
        self.AssignImageList(il)

        ids = {rootPath: self.AddRoot(rootPath, self.folderidx)}
        self.SetItemHasChildren(ids[rootPath])

        for (dirpath, dirnames, filenames) in os.walk(rootPath):
            for dirname in sorted(dirnames):
                fullpath = os.path.join(dirpath, dirname)
                ids[fullpath] = self.AppendItem(ids[dirpath], dirname, self.folderidx)

            for filename in sorted(filenames):
                self.AppendItem(ids[dirpath], filename, self.fileidx)

        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.onFileSelected)

    def onFileSelected(self, event):
        parent = self.GetItemParent(event.GetItem())
        parts = [self.GetItemText(event.GetItem())]
        while parent.GetID() is not None:
            parts.insert(0, self.GetItemText(parent))
            parent = self.GetItemParent(parent)
        fileToOpen = "\\".join(parts)
        self.notebook.newTabIfNotExists(fileToOpen)

class Notepad(wx.SplitterWindow):
    def __init__(self, parent, editor):
        wx.SplitterWindow.__init__(self, parent, wx.NewId(), style=wx.CLIP_CHILDREN | wx.SP_LIVE_UPDATE)
        self.editor = editor
        self.workspacePath = self.getWorkspacePath()
        self.SetMinimumPaneSize(1)
        self.SplitVertically(self.newNotebook(), self.newFileTree())
        self.SetSashPosition(1000)

    def newNotebook(self):
        self.notebook = CodeNotebook(self, self.workspacePath)
        self.notebook.newTabIfNotExists("{}/hadamard.py".format(self.workspacePath))
        return self.notebook

    def newFileTree(self):
        panel = wx.Panel(self)
        fileTreeSizer = wx.FlexGridSizer(cols=1, hgap=5, vgap=5)
        fileTreeSizer.Add(wx.StaticText(panel, -1, "WORKSPACE"))
        fileTreeSizer.Add(self.newDirTree(panel), 0, wx.EXPAND)
        fileTreeSizer.AddGrowableCol(0)
        fileTreeSizer.AddGrowableRow(1)
        panel.SetSizer(fileTreeSizer)
        return panel

    def getWorkspacePath(self):
        cwd =  os.getcwd()
        C_root, subdir, _, _ = re.findall(r'(C:\\)((\w+\\)+)(\w+)', cwd)[0]
        workspacePath = C_root + subdir + "workspace"        
        return workspacePath

    def newDirTree(self, parent):
        dirTree = MyTree(parent, self.workspacePath, self.notebook)
        dirTree.ExpandAll()
        return dirTree