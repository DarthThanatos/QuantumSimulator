import wx
import wx.grid


class ButtonRenderer(wx.grid.GridCellRenderer):

    def __init__(self, state_details_fun):
        wx.grid.GridCellRenderer.__init__(self)
        self.down = False
        self.click_handled = False
        self.__state_details_fun = state_details_fun

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        if self.down:
            state = wx.CONTROL_PRESSED | wx.CONTROL_SELECTED
        else:
            state = 0
        x,y = rect.GetTopLeft()
        tw, th = dc.GetTextExtent("argand")
        w, h = rect.GetWidth(), rect.GetHeight()
        wx.RendererNative.Get().DrawPushButton(grid, dc, rect, state)
        dc.DrawText("argand", x + w/2 - tw/2, y + h/2 - th/2)
        if self.down and not self.click_handled:
            self.click_handled = True
            self.HandleClick()

    def HandleClick(self):
        self.__state_details_fun()

    def GetBestSize(self, grid, attr, dc, row, col):
        text = grid.GetCellValue(row, col)
        dc.SetFont(attr.GetFont())
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)

    def Clone(self):
        return ButtonRenderer(self.__state_details_fun)


class StateDetailsFun:

    def __init__(self, amplitude, probabilities_mediator):
        self.__amplitude = amplitude
        self.__probabilities_mediator = probabilities_mediator

    def __call__(self):
        self.__probabilities_mediator.visualise_amplitude(self.__amplitude)


class ProbabilitiesTable(wx.grid.Grid):
    def __init__(self, parent, register_representation, probabilities_mediator):
        wx.grid.Grid.__init__(self, parent)
        self.__probabilities_mediator = probabilities_mediator
        self.CreateGrid(len(register_representation), 5)
        self.__renderer =  ButtonRenderer(StateDetailsFun(0, self.__probabilities_mediator))
        for i, row_representation in enumerate(register_representation):
            self.__update_row(row_representation, i)
        self.__setup_titles()
        self.SetRowLabelSize(0)
        self.SetGridLineColour(wx.WHITE)
        self.GetGridWindow().Bind(wx.EVT_LEFT_DOWN, self.__on_left_down)
        self.GetGridWindow().Bind(wx.EVT_LEFT_UP, self.__on_left_up)

    def __update_row(self, row_representation, i):
        for j in range(5):
            self.SetReadOnly(i, j, True)
            if j == 4:
                self.SetCellRenderer(i, 4, ButtonRenderer(StateDetailsFun(complex(row_representation[3]), self.__probabilities_mediator)))
            else:
                self.SetCellAlignment(i, j, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
                self.SetCellValue(i, j, row_representation[j])

    def __setup_titles(self):
        titles = ["value", "qubits", "probability", "amplitude", ""]
        for i in range(5):
            self.SetColLabelValue(i, titles[i])

    def __on_left_down(self, evt):
        col, row = self.__hit_test_cell(evt.GetPosition().x, evt.GetPosition().y)
        if isinstance(self.GetCellRenderer(row, col), ButtonRenderer):
            self.GetCellRenderer(row, col).down = True
        self.Refresh()
        evt.Skip()

    def __on_left_up(self, evt):
        col, row = self.__hit_test_cell(evt.GetPosition().x, evt.GetPosition().y)
        if isinstance(self.GetCellRenderer(row, col), ButtonRenderer):
            self.GetCellRenderer(row, col).down = False
            self.GetCellRenderer(row, col).click_handled = False
        self.Refresh()
        evt.Skip()

    def __hit_test_cell(self, x, y):
        x, y = self.CalcUnscrolledPosition(x, y)
        return self.XToCol(x), self.YToRow(y)


if __name__ == '__main__':

    app = wx.App(0)
    frame = ProbabilitiesTable(None, [], None)
    app.MainLoop()