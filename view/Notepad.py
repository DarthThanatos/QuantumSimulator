import wx
import wx.stc as stc

import keyword

class Notepad(wx.Panel):
    def __init__(self, parent, editor):
        wx.Panel.__init__(self, parent, wx.NewId(), style=wx.CLIP_CHILDREN | wx.SP_LIVE_UPDATE)
        self.textArea = stc.StyledTextCtrl(self, size = parent.GetClientSize(), style=wx.TE_MULTILINE)
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
        # Python styles
        # Default
        self.textArea.StyleSetSpec(stc.STC_P_DEFAULT, "fore:#000000,face:%(helv)s,size:%(size)d" % faces)
        # Comments
        self.textArea.StyleSetSpec(stc.STC_P_COMMENTLINE, "fore:#007F00,face:%(other)s,size:%(size)d" % faces)
        # Number
        self.textArea.StyleSetSpec(stc.STC_P_NUMBER, "fore:#007F7F,size:%(size)d" % faces)
        # String
        self.textArea.StyleSetSpec(stc.STC_P_STRING, "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces)
        # Single quoted string
        self.textArea.StyleSetSpec(stc.STC_P_CHARACTER, "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces)
        # Keyword
        self.textArea.StyleSetSpec(stc.STC_P_WORD, "fore:#00007F,bold,size:%(size)d" % faces)
        # Triple quotes
        self.textArea.StyleSetSpec(stc.STC_P_TRIPLE, "fore:#7F0000,size:%(size)d" % faces)
        # Triple double quotes
        self.textArea.StyleSetSpec(stc.STC_P_TRIPLEDOUBLE, "fore:#7F0000,size:%(size)d" % faces)
        # Class name definition
        self.textArea.StyleSetSpec(stc.STC_P_CLASSNAME, "fore:#0000FF,bold,underline,size:%(size)d" % faces)
        # Function or method name definition
        self.textArea.StyleSetSpec(stc.STC_P_DEFNAME, "fore:#007F7F,bold,size:%(size)d" % faces)
        # Operators
        self.textArea.StyleSetSpec(stc.STC_P_OPERATOR, "bold,size:%(size)d" % faces)
        # Identifiers
        self.textArea.StyleSetSpec(stc.STC_P_IDENTIFIER, "fore:#000000,face:%(helv)s,size:%(size)d" % faces)
        # Comment-blocks
        self.textArea.StyleSetSpec(stc.STC_P_COMMENTBLOCK, "fore:#7F7F7F,size:%(size)d" % faces)
        # End of line where string is not closed
        self.textArea.StyleSetSpec(stc.STC_P_STRINGEOL, "fore:#000000,face:%(mono)s,back:#E0C0E0,eol,size:%(size)d" % faces)

        self.textArea.SetCaretForeground("BLUE")
        self.editor = editor

    def handleStyleNeeded(self):
        print("style needed and i do not know ")