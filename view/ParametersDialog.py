from model.gates.U import UGate
from util.Utils import get_screen_middle_point, flatten_dicts, newIconButton, InspectorMatrixPanel, newStandardButton
import wx

from view.constants import INSPECTOR_MATRIX_FIGURE_ID
from wx.lib.scrolledpanel import ScrolledPanel


class ParameterMediator:

    def __init__(self, gate):
        self._gate = gate
        self.__parameters_views = []
        self.__parameters_frame = None
        self.__apply_button = None
        self.__gate_error_log = None

    def set_parameters_frame(self, parameters_frame):
        self.__parameters_frame = parameters_frame

    def __get_gate_kwargs(self):
        return flatten_dicts(map(lambda view: view.get_arg_description(), self.__parameters_views))

    def setup_gate_error_log(self, log):
        self.__gate_error_log = log
        kwargs = self.__get_gate_kwargs()
        if not self._gate.is_gate_correct(kwargs):
            log.SetLabelText(self._gate.why_gate_not_correct(kwargs))

    def setup_apply_button(self, apply_btn):
        self.__apply_button = apply_btn
        kwargs = self.__get_gate_kwargs()
        apply_btn.Enable(self._gate.is_gate_correct(kwargs))

    def add_parameter_view(self, parameter_view):
        self.__parameters_views.append(parameter_view)

    def parameter_input_changed(self, parameter_view):
        input_value = parameter_view.parameter_input.GetValue()
        param_name = parameter_view.get_parameter_name()
        correct = self._gate.is_parameter_correct(param_name, input_value)
        if not correct:
            error = self._gate.why_is_parameter_incorrect(param_name, input_value)
            parameter_view.change_error_log(
                foreground_color=wx.WHITE,
                background_color=wx.RED,
                error="{}: {}".format(param_name, error)
            )
        else:
            parameter_view.change_error_log(wx.BLACK, wx.WHITE, error="")
        self.__on_parameter_input_changed()

    def __on_parameter_input_changed(self):
        kwargs = self.__get_gate_kwargs()
        self.__apply_button.Enable(self._gate.is_gate_correct(kwargs))
        error_msg = \
            self._gate.why_gate_not_correct(kwargs) \
            if not self._gate.is_gate_correct(kwargs) \
            else ""
        self.__gate_error_log.SetLabelText(error_msg)
        self.__parameters_frame.layout()

    def on_apply(self):
        for name, value in self.__get_gate_kwargs().items():
            self._gate.set_parameter_value(name, value)


class GateInspectorMediator(ParameterMediator):
    def __init__(self, gate, gate_mediator):
        ParameterMediator.__init__(self, gate)
        self.__gate_mediator = gate_mediator
        self.__matrix_panel = None


    def set_matrix_panel(self, matrix_panel):
        self.__matrix_panel = matrix_panel

    def on_apply(self):
        super().on_apply()
        self.__matrix_panel.change_matrix_value(self._gate.qutip_object().full())
        self.__gate_mediator.circuit_grid_changed()


OK_CANCEL_STYLE = 0
APPLY_STYLE = 1


class ParameterView(wx.Panel):

    def __init__(self, parent, parameter_name, parameter_default, error_log, parameter_mediator):
        super().__init__(parent)
        self.__parameter_name = parameter_name
        self.__parameter_mediator = parameter_mediator
        self.parameter_input = None
        self.error_log = error_log
        self.__create_sizer(parameter_name, parameter_default)

    def __create_sizer(self, parameter_name, default_value):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticText(self, label=parameter_name))
        sizer.AddSpacer(10)
        sizer.Add(self.__new_parameter_input(default_value))
        sizer.AddSpacer(10)
        sizer.Layout()
        self.SetSizer(sizer)

    def __new_parameter_input(self, default):
        self.parameter_input = wx.TextCtrl(self, style=wx.TE_RICH | wx.WANTS_CHARS)
        self.parameter_input.SetValue(default)
        self.parameter_input.Bind(wx.EVT_KILL_FOCUS, self.__on_input_changed)
        return self.parameter_input

    def __on_input_changed(self, ev):
        self.__parameter_mediator.parameter_input_changed(self)
        ev.Skip()

    def change_error_log(self, foreground_color, background_color, error=""):
        self.error_log.SetLabelText(error)
        self.parameter_input.SetBackgroundColour(background_color)
        self.parameter_input.SetForegroundColour(foreground_color)

    def get_arg_description(self):
        return {self.__parameter_name: self.parameter_input.GetValue()}

    def get_parameter_name(self):
        return self.__parameter_name


class ParametersPanel(wx.Panel):

    WIDTH = 450

    def __init__(self, parent, gate_name, gate_parameters_names, gate_parameters_defaults, parameters_mediator,
                 style=OK_CANCEL_STYLE):
        wx.Panel.__init__(self, parent)
        self.__parameters_mediator = parameters_mediator
        self.__style = style
        parameters_mediator.set_parameters_frame(self)
        self.__root_sizer = None
        self.__new_panel(gate_name, gate_parameters_names, gate_parameters_defaults)

    def get_height(self, gate_parameters_names):
        # the dialog must have the height that fits len(params) widgets (i.e. all parameter views),
        # plus it must contain an error log area for each such widget, plus a log area for the gate itself,
        # plus buttons area, plus spacers, plus header
        spacers = 70
        single_view_height = 20
        header_size = 30
        return (len(gate_parameters_names) + 1) * 2 * single_view_height + header_size + spacers

    def __new_panel(self, gate_name, parameters_names, parameters_defaults):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(self.__new_header(gate_name), 0, wx.CENTER)
        sizer.AddSpacer(20)
        sizer.Add(self.__new_parameters_views(parameters_names, parameters_defaults), 0, wx.CENTER)
        sizer.Add(self.__new_gate_error_log(), 0, wx.CENTER)
        sizer.AddSpacer(10)
        sizer.Add(self.__new_ok_cancel(), 0, wx.EXPAND if self.__style == APPLY_STYLE else wx.CENTER)
        sizer.AddSpacer(20)
        sizer.Layout()
        self.SetSizer(sizer)
        self.__root_sizer = sizer

    def __new_ok_cancel(self):
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(self.__new_ok(), wx.CENTER)
        if self.__style == OK_CANCEL_STYLE:
            btn_sizer.AddSpacer(10)
            btn_sizer.Add(self.__new_cancel(), wx.CENTER)
        return btn_sizer

    def __new_ok(self):
        ok_btn = wx.Button(self, label="ok" if self.__style == OK_CANCEL_STYLE else "apply")
        ok_btn.Bind(wx.EVT_BUTTON, self.__on_ok)
        self.__parameters_mediator.setup_apply_button(ok_btn)
        if self.__style == APPLY_STYLE:
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(wx.Panel(self), proportion=3)
            sizer.Add(ok_btn, proportion=1)
            sizer.AddSpacer(10)
            return sizer
        return ok_btn

    def __new_cancel(self):
        cancel_btn = wx.Button(self, label="cancel")
        cancel_btn.Bind(wx.EVT_BUTTON, self.__on_cancel)
        return cancel_btn

    def __header_text(self, gate_name):
        return "creating a new {} gate".format(gate_name) \
                   if self.__style == OK_CANCEL_STYLE \
                   else "updating the {} gate".format(gate_name)

    def __new_header(self,  gate_name):
        header = wx.StaticText(self, label=self.__header_text(gate_name))
        header.SetForegroundColour(wx.BLUE)
        font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.NORMAL)
        header.SetFont(font)
        return header

    def __new_gate_error_log(self):
        log = self.__new_error_log()
        self.__parameters_mediator.setup_gate_error_log(log)
        return log

    def __new_error_log(self):
        error_log = wx.StaticText(self)
        error_log.SetForegroundColour(wx.RED)
        return error_log

    def __new_parameters_views(self, parameters_names, parameters_defaults):
        parameters_sizer = wx.BoxSizer(wx.VERTICAL)
        error_log_sizer, error_logs = self.__new_error_logs(parameters_names)
        for parameter_name in parameters_names:
            parameter_default = str(parameters_defaults[parameter_name])
            parameter_view = ParameterView(self, parameter_name, parameter_default, error_logs[parameter_name], self.__parameters_mediator)
            self.__parameters_mediator.add_parameter_view(parameter_view)
            parameters_sizer.Add(parameter_view)
        parameters_sizer.Add(error_log_sizer)
        return parameters_sizer

    def __new_error_logs(self, parameters_names):
        error_sizer = wx.BoxSizer(wx.VERTICAL)
        error_logs = {}
        for parameter_name in parameters_names:
            error_log = self.__new_error_log()
            error_logs[parameter_name] = error_log
            error_sizer.Add(error_log)
        return error_sizer, error_logs

    def __on_ok(self, _):
        self.__parameters_mediator.on_apply()
        self.GetParent().on_ok()

    def __on_cancel(self, _):
        self.GetParent().on_cancel()

    def layout(self):
        self.__root_sizer.Layout()


class ParametersDialog(wx.Dialog):
    def __init__(self, parent, gate_name, gate_parameters_names, gate_parameters_defaults, parameters_mediator):
        wx.Dialog.__init__(self, parent, style=wx.NO_BORDER)
        panel = ParametersPanel(self, gate_name, gate_parameters_names, gate_parameters_defaults, parameters_mediator,
                        style=OK_CANCEL_STYLE)
        self.SetSize(*get_screen_middle_point(), panel.WIDTH, panel.get_height(gate_parameters_names))

    def on_ok(self):
        self.EndModal(wx.OK)

    def on_cancel(self):
        self.EndModal(wx.CANCEL)


class GateInspectorPanel(ScrolledPanel):

    def __init__(self, splitter_parent, gate_mediator):
        ScrolledPanel.__init__(self, splitter_parent)
        self.__gate_mediator = gate_mediator
        self.__gate_mediator.set_gate_inspector_panel(self)
        self.__root_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__root_sizer)
        self.__timer = wx.Timer(self)
        self.__sash_pos = 0
        self.Bind(wx.EVT_TIMER, self.__animate_showing, self.__timer)
        self.__should_show = False
        self.__gate = None
        self.__gate_inspector_mediator = None
        self.SetBackgroundColour(wx.WHITE)
        self.SetupScrolling()

    def reset_view(self, gate):
        self.__gate = gate
        self.Freeze()
        self.DestroyChildren()
        self.__root_sizer.Clear()
        self.__root_sizer.Add(self.__new_close_button(), 0, wx.EXPAND)
        self.__root_sizer.Add(self.__new_parameters_panel(gate))
        self.__root_sizer.AddSpacer(10)
        self.__root_sizer.Add(self.__new_matrix_panel(gate), 0, wx.CENTER)
        self.__root_sizer.Add(self.__new_copy_gate_btn(), 0, wx.CENTER)
        self.__root_sizer.Layout()
        self.SetupScrolling()
        self.Thaw()

    def __new_copy_gate_btn(self):
        return newStandardButton(self, (125, 25), "copy gate", self.__on_copy)

    def __on_copy(self, _):
        self.__gate_mediator.gateSelected(self.__gate.get_name(), self.__gate)

    def __new_matrix_panel(self, gate):
        try:
            gate_matrix = gate.qutip_object().full()
        except:
            return wx.Panel(self)
        matrix_panel = InspectorMatrixPanel(self, gate.latex_symbol(), gate_matrix, INSPECTOR_MATRIX_FIGURE_ID, gate.latex_matrix_str())
        if self.__gate_inspector_mediator is not None:
            self.__gate_inspector_mediator.set_matrix_panel(matrix_panel)
        return matrix_panel

    def __new_close_button(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn = newIconButton(self, (32, 32), '../images/icons/close_icon.png', self.on_close)
        sizer.Add(wx.Panel(self), 5)
        sizer.Add(btn, 1)
        return sizer

    def on_close(self, event=None):
        self.__show_inspector(False)

    def __new_parameters_panel(self, gate):
        gate_name = gate.get_name()
        params_names = gate.get_parameters_names()
        if len(params_names) == 0:
            return wx.Panel(self)
        params_defaults = gate.parameters()
        self.__gate_inspector_mediator = GateInspectorMediator(gate, self.__gate_mediator)
        panel = ParametersPanel(self, gate_name, params_names, params_defaults, self.__gate_inspector_mediator, style=APPLY_STYLE)
        return panel

    def on_ok(self):
        pass  # is demanded by ParametersPanel class

    def on_cancel(self):
        pass  # is demanded by ParametersPanel class

    def __animate_showing(self, event):
        parent = self.GetParent()
        if not self.__should_show:
            if self.__sash_pos > 1:
                self.__sash_pos -= 40
            else:
                self.__gate_mediator.stop_inspecting_gate()
                self.__sash_pos = 1
                self.__timer.Stop()
            self.__sash_pos = max(1, self.__sash_pos)
        else:
            if self.__sash_pos < 450:
                self.__sash_pos += 40
            else:
                self.__sash_pos = 450
                self.__timer.Stop()
        parent.SetSashPosition(self.__sash_pos, redraw=True)
        event.Skip()

    def inspect(self, gate):
        self.reset_view(gate)
        self.__show_inspector(True)

    def __show_inspector(self, should_show):
        self.__should_show = should_show
        if not should_show:
            self.__gate_mediator.init_stop_inspecting_gate()
        self.__timer.Start(10)


if __name__ == "__main__":
    app = wx.PySimpleApp()
    gate = UGate(0)
    dialog = ParametersDialog(
        None,
        gate.get_name(),
        gate.get_parameters_names(),
        gate.get_parameters_defaults(),
        ParameterMediator(gate)
    )
    status = dialog.ShowModal()
