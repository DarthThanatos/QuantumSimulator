import datetime
import traceback

import wx.stc as stc

import keyword
import wx, os

from util.Utils import newStandardButton, get_workspace_path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from wx.aui import AuiNotebook


class CodeNotebook(AuiNotebook):

    def __init__(self, parent, rootPath, gate_mediator, quantum_computer):
        AuiNotebook.__init__(self, parent, style=wx.CLIP_CHILDREN | wx.aui.AUI_NB_CLOSE_ON_ALL_TABS)
        self.openCards = {}
        self.rootPath = rootPath
        self.__gate_mediator = gate_mediator
        gate_mediator.set_code_notebook(self)
        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSED, self.__on_page_close)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.__on_destroy)
        self.__quantum_computer = quantum_computer

    def __on_destroy(self, event):
        for file, text_area in self.openCards.items():
            try:
                path = self.rootPath + '\\' + file
                with open(path, "w") as f:
                    f.write(text_area.GetValue().replace('\r\n', '\n'))
            except Exception as e:
                traceback.print_exc()

    def __on_page_close(self, event):
        file = self.GetPageText(event.GetSelection())
        self.__close(file, event.GetSelection())

    def __close(self, file, position, save=True):
        text_area = self.openCards[file]
        self.openCards.__delitem__(file)
        if save:
            path = self.rootPath + '\\' + file
            with open(path, "w") as f:
                f.write(text_area.GetValue().replace('\r\n', '\n'))
        self.RemovePage(position)
        self.RemoveChild(text_area)
        text_area.DestroyLater()

    def modify_content_if_tab_exists(self, full_file_name):
        file_to_modify = full_file_name.split(self.rootPath)[1][1:]
        if self.openCards.__contains__(file_to_modify):
            with open(full_file_name, "r") as f:
                ta = self.openCards[file_to_modify]
                contents = f.read()
                ta.SetValue(contents)

    def deleteTabIfExists(self, full_file_path_to_close):
        file_to_close = full_file_path_to_close.split(self.rootPath)[1][1:]
        if self.openCards.__contains__(file_to_close):
            self.__close(file_to_close, self.findPageByName(file_to_close), save=False)

    def newTabIfNotExists(self, fileToOpen, retain_content=True):
        with open(fileToOpen, "r") as f:
            cardName = fileToOpen.split(self.rootPath)
            cardName = cardName[1][1:] # [1:] -> cutting off the first slash
            if self.openCards.__contains__(cardName):
                if not retain_content:
                    ta = self.openCards[cardName]
                    ta.SetValue(f.read())
            else:
                ta = self.newTextArea(cardName)
                ta.SetValue(f.read())
                self.openCards[cardName] = ta
                self.AddPage(ta, cardName)
            self.SetSelection(self.findPageByName(cardName))

    def findPageByName(self, cardName):
        for i in range (self.GetPageCount()):
            if self.GetPageText(i) == cardName:
                return i
        return None

    def __on_text_area_focus_killed(self, event):
        if not self:
            return
        file_name = self.__find_name_by_text_area(event.GetEventObject())
        text_area = event.GetEventObject()
        if file_name is None:
            return
        path = self.rootPath + '\\' + file_name
        value = text_area.GetValue().replace('\r\n', '\n')
        with open(path, "w") as f:
            f.write(value)
        event.Skip()

    def __find_name_by_text_area(self, ta):
        for file_name, text_area in self.openCards.items():
            if text_area is ta:
                return file_name

    def newTextArea(self, title):
        self.textArea = stc.StyledTextCtrl(parent=self, style=wx.TE_MULTILINE)
        self.textArea.Bind(wx.EVT_KILL_FOCUS, self.__on_text_area_focus_killed)
        with open("../workspace/{}".format(title), "r") as f:
            self.textArea.SetValue(f.read())
        self.textArea.SetLexer(stc.STC_LEX_PYTHON)
        self.textArea.SetStyleBits(5)
        self.textArea.SetMarginWidth(0, 20)
        self.textArea.SetMarginType(0, wx.stc.STC_MARGIN_NUMBER)
        faces = {
            'times': 'Times New Roman',
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

    def get_current_code_string(self):
        return self.GetCurrentPage().GetValue()

    def get_current_file_name(self):
        return self.GetPageText(self.GetSelection())


class TreeEventHandler(FileSystemEventHandler):

    def __init__(self, tree, notebook):
        self.__tree = tree
        self.__notebook = notebook

    def on_moved(self, event):
        # print("moved", event.src_path)
        wx.CallAfter(self.__notebook.deleteTabIfExists, event.src_path)
        wx.CallAfter(self.__tree.reset)

    def on_created(self, event):
        # print("created", event.src_path)
        wx.CallAfter(self.__tree.reset)

    def on_modified(self, event):
        wx.CallAfter(self.__notebook.modify_content_if_tab_exists, event.src_path)

    def on_deleted(self, event):
        # print("deleted", event.src_path)
        wx.CallAfter(self.__tree.reset)
        wx.CallAfter(self.__notebook.deleteTabIfExists, event.src_path)


class MyTree(wx.TreeCtrl):
    def __init__(self, parent, rootPath, notebook, gateMediator):
        super(MyTree, self).__init__(parent)
        self.__collapsing = True
        self.__gate_mediator = gateMediator
        gateMediator.set_tree(self)
        self.rootPath = rootPath
        self.notebook = notebook

        il = wx.ImageList(16, 16)
        self.folderidx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (16, 16)))
        self.fileidx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16, 16)))
        self.AssignImageList(il)
        self.__event_handler = TreeEventHandler(self, self.notebook)
        self.__observer = Observer()
        self.__observer.schedule(self.__event_handler, rootPath, recursive=True)
        self.__observer.start()

        self.reset()
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.onFileSelected)

    def stop_observer(self):
        self.__observer.stop()
        self.__observer.join()

    def reset(self):
        self.Freeze()
        rootPath = self.rootPath
        self.DeleteAllItems()
        ids = {rootPath: self.AddRoot(rootPath, self.folderidx)}
        for (dirpath, dirnames, filenames) in os.walk(rootPath):
            for dirname in sorted(dirnames):
                fullpath = os.path.join(dirpath, dirname)
                ids[fullpath] = self.AppendItem(ids[dirpath], dirname, self.folderidx)

            for filename in sorted(filenames):
                self.AppendItem(ids[dirpath], filename, self.fileidx)
        self.SetItemHasChildren(ids[rootPath])
        self.ExpandAll()
        self.Thaw()

    def onFileSelected(self, event):
        parent = self.GetItemParent(event.GetItem())
        parts = [self.GetItemText(event.GetItem())]
        while parent.GetID() is not None:
            parts.insert(0, self.GetItemText(parent))
            parent = self.GetItemParent(parent)
        fileToOpen = "\\".join(parts)
        self.notebook.newTabIfNotExists(fileToOpen, retain_content=False)


class Notepad(wx.SplitterWindow):
    def __init__(self, parent, gate_mediator, quantum_computer):
        wx.SplitterWindow.__init__(self, parent, wx.NewId(), style=wx.CLIP_CHILDREN | wx.SP_LIVE_UPDATE)
        self.__gate_mediator = gate_mediator
        self.__gate_mediator.set_notepad(self)
        self.__quantum_computer = quantum_computer
        self.__console = None
        self.__notebook = None

        self.__timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.__generate, self.__timer)
        self.__new_file_name = ""

        self.workspacePath = get_workspace_path()
        self.SetMinimumPaneSize(1)
        self.SplitVertically(self.__new_inspector_notebook_splitter(), self.newFileTree())
        self.SetSashPosition(1500)

    def __new_inspector_notebook_splitter(self):
        inspector_notebook_splitter = wx.SplitterWindow(self, style=wx.CLIP_CHILDREN | wx.SP_LIVE_UPDATE)
        inspector_notebook_splitter.SplitVertically(self.__new_console_panel(inspector_notebook_splitter), self.__new_notebook_panel(inspector_notebook_splitter))
        inspector_notebook_splitter.SetSashPosition(450)
        inspector_notebook_splitter.SetMinimumPaneSize(1)
        return inspector_notebook_splitter

    def __new_notebook_panel(self, splitter):
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel = wx.Panel(splitter, size=(1500,1000))
        sizer.Add(self.__new_notebook_button_panel(panel), 0, wx.CENTER)
        sizer.Add(self.__new_notebook(panel), wx.EXPAND, wx.EXPAND)
        sizer.Layout()
        panel.SetSizer(sizer)
        return panel

    def __new_notebook_button_panel(self, panel):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(newStandardButton(panel, size=(125, 35), label="Run in console", on_click=self.__run_in_console), wx.CENTER)
        sizer.AddSpacer(10)
        sizer.Add(newStandardButton(panel, size=(125, 35), label="Build circuit", on_click=self.__build_circuit), wx.CENTER)
        sizer.AddSpacer(10)
        sizer.Add(newStandardButton(panel, size=(125, 35), label="New file", on_click=self.__on_new_file), wx.CENTER)
        return sizer

    def __on_new_file(self, event):
        dialog = wx.FileDialog(
            self,
            defaultDir=get_workspace_path(),
            message="Choose new file name",
            wildcard="*.py",
            style=wx.FD_SAVE
        )
        if dialog.ShowModal() == wx.ID_OK:
            self.__new_file_name = dialog.GetPath()
            self.__timer.StartOnce(100)

    def __generate(self, event):
        with open(self.__new_file_name, 'w+'):
            self.__notebook.newTabIfNotExists(self.__new_file_name, retain_content=False)

    def __run_in_console(self, event):
        self.__gate_mediator.run_in_console(self.__quantum_computer)

    def __build_circuit(self, event):
        self.__gate_mediator.build_circuit(self.__quantum_computer)

    def __new_notebook(self, splitter):
        self.__notebook = CodeNotebook(splitter, self.workspacePath, self.__gate_mediator, self.__quantum_computer)
        self.__notebook.newTabIfNotExists("{}/hadamard.py".format(self.workspacePath), retain_content=False)
        return self.__notebook

    def __new_console_panel(self, splitter):
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel = wx.Panel(splitter)
        panel.SetSizer(sizer)
        sizer.Add(self.__new_console_label(panel))
        sizer.Add(self.__new_console(panel))
        sizer.Layout()
        return panel

    def __new_console_label(self, panel):
        label = wx.StaticText(panel, label="Console", size=(1750, -1), style=wx.ALIGN_CENTRE)
        font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.NORMAL)
        label.SetFont(font)
        return label

    def __new_console(self, splitter):
        self.__console = wx.TextCtrl(splitter, size = (1750, 1000), style=wx.TE_READONLY | wx.TE_MULTILINE | wx.NO_BORDER)
        return self.__console

    def newFileTree(self):
        panel = wx.Panel(self)
        fileTreeSizer = wx.FlexGridSizer(cols=1, hgap=5, vgap=5)
        fileTreeSizer.Add(wx.StaticText(panel, -1, "WORKSPACE"))
        fileTreeSizer.Add(self.newDirTree(panel), 0, wx.EXPAND)
        fileTreeSizer.AddGrowableCol(0)
        fileTreeSizer.AddGrowableRow(1)
        panel.SetSizer(fileTreeSizer)
        return panel


    def newDirTree(self, parent):
        dirTree = MyTree(parent, self.workspacePath, self.__notebook, self.__gate_mediator)
        dirTree.ExpandAll()
        return dirTree

    def update_console(self, output):
        self.__console.SetValue(output)