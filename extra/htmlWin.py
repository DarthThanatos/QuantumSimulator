import wx
import wx.html as html
import wx.html2
import wx.lib.wxpTag


about_html = '''
<html>
<body bgcolor="#4488FF">
<center>
<table cellpadding="5" bgcolor="#FFFFFF" width="100%%">
  <tr>
    <td align="center"><br>
    <img src="%s"><br>
    <font color="#006600" size="+4"><b>Constructor</b></font><br><strong>v%s</strong>%s</td>
  </tr>
</table>
%s
</body>
</html>
'''

progress_text = '''<p>
<wxp module="wx" class="StaticText">
  <param name="label" value="  ">
  <param name="id"    value="%d">
  <param name="size"  value="(352, 20)">
  <param name="style" value="wx.ALIGN_CENTER | wx.CLIP_CHILDREN | wx.ST_NO_AUTORESIZE">
</wxp>
<wxp module="wx" class="Window">
  <param name="id"    value="%d">
  <param name="size"  value="(352, 16)">
</wxp>'''

class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title)
        panel = MainPanel(self)

def printChildren(html):
    print (html.GetChildren())
    print(html.Children)

class MainPanel(wx.Panel):
    def __init__(self, frame):
        wx.Panel.__init__(self, frame)

        wx.StaticText()
        txt_style = wx.VSCROLL|wx.HSCROLL|wx.TE_READONLY|wx.BORDER_SIMPLE
        self.html = wx.html.HtmlWindow(self, -1, size=(300, 150), style=txt_style)
        # self.html = wx.html2.WebView.New(self)
        # self.html.Create(self, -1, size=(300, 150), style=txt_style)
        txt = "Here is some <b>formatted</b>"\
            "<i><u>text</u></i> "\
            "loaded from a "\
            "<font color=\"red\">string</font>."
        txt = about_html % ('memory:Simul.jpg',  '0.7.2', progress_text % (102, 103), '')
        self.html.SetPage(txt)

        wx.CallAfter(printChildren, self.html)
        print (self.html.GetChildren())
        # help(self.html)

app = wx.App()
frm = MainFrame(None, "Screen layout")
frm.Show()
app.MainLoop()