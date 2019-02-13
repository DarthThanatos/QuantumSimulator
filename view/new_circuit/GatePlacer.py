import wx
import wx.lib.newevent
from view.new_circuit.constants import *

from util.Utils import get_screen_middle_point, flatten_dicts

ParameterChangedEvent, EVT_PARAM_CHANGED = wx.lib.newevent.NewEvent()


class ParameterView(wx.Panel):

    def __init__(self, parent, gate, parameter_name, error_log):
        super().__init__(parent)
        self.__gate = gate
        self.__parameter_name = parameter_name
        self.__parameter_input = None
        self.__error_log = error_log
        self.__create_sizer()

    def __create_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticText(self, label=self.__parameter_name))
        sizer.AddSpacer(10)
        sizer.Add(self.__new_parameter_input())
        sizer.AddSpacer(10)
        sizer.Layout()
        self.SetSizer(sizer)

    def __new_parameter_input(self):
        self.__parameter_input = wx.TextCtrl(self, style=wx.TE_RICH | wx.WANTS_CHARS)
        value = str(self.__gate.get_parameter_default(self.__parameter_name))
        self.__parameter_input.SetValue(value)
        self.__parameter_input.Bind(wx.EVT_KILL_FOCUS, self.__on_input_changed)
        return self.__parameter_input

    def __on_input_changed(self, ev):
        input = self.__parameter_input.GetValue()
        correct = self.__gate.is_parameter_correct(self.__parameter_name, input)
        if not correct:
            error = self.__gate.why_is_parameter_incorrect(self.__parameter_name, input)
            self.__change_error_log(
                foreground_color=wx.WHITE,
                background_color=wx.RED,
                error="{}: {}".format(self.__parameter_name, error)
            )
        else:
            self.__change_error_log(wx.BLACK, wx.WHITE, error="")
        param_changed_ev = ParameterChangedEvent()
        wx.PostEvent(self.GetParent(), param_changed_ev)
        ev.Skip()  # so that text ctrl handles its own focus correctly

    def __change_error_log(self, foreground_color, background_color, error=""):
        self.__error_log.SetLabelText(error)
        self.__parameter_input.SetBackgroundColour(background_color)
        self.__parameter_input.SetForegroundColour(foreground_color)

    def get_arg_description(self):
        return {self.__parameter_name: self.__parameter_input.GetValue()}


class ParameterDialog(wx.Dialog):

    WIDTH = 450

    def __init__(self, parent, quantum_computer, gate, i, j):
        wx.Dialog.__init__(self, parent, size=(self.WIDTH, self.getHeight(gate)), style=wx.NO_BORDER, pos=get_screen_middle_point())
        self.__quantum_computer = quantum_computer
        self.__gate = gate
        self.__ij = (i, j)
        self.__parameters_views = []
        self.__gate_error_log = None
        self.__ok_btn = None
        self.__root_sizer = None
        self.__new_panel()

    def getHeight(self, gate):
        # the dialog must have the height that fits len(params) widgets (i.e. all parameter views),
        # plus it must contain an error log area for each such widget, plus a log area for the gate itself,
        # plus buttons area, plus spacers
        spacers = 50
        single_view_height = 20
        return (len(gate.get_parameters_names()) + 1) * 2 * single_view_height + spacers

    def __new_panel(self):
        panel = wx.Panel(self)
        panel.Bind(EVT_PARAM_CHANGED, self.__on_parameter_input_changed)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(self.__new_parameters_views(panel), 0, wx.CENTER)
        sizer.Add(self.__new_gate_error_log(panel), 0, wx.CENTER)
        sizer.AddSpacer(10)
        sizer.Add(self.__new_ok_cancel(panel), 0, wx.CENTER)
        sizer.AddSpacer(20)
        sizer.Layout()
        panel.SetSizer(sizer)
        self.__root_sizer = sizer

    def __get_gate_kwargs(self):
        return flatten_dicts(map(lambda view: view.get_arg_description(), self.__parameters_views))

    def __on_parameter_input_changed(self, _):
        kwargs = self.__get_gate_kwargs()
        self.__ok_btn.Enable(self.__gate.is_gate_correct(kwargs))
        error_msg = \
            self.__gate.why_gate_not_correct(kwargs) \
            if not self.__gate.is_gate_correct(kwargs) \
            else ""
        self.__gate_error_log.SetLabelText(error_msg)
        self.__root_sizer.Layout()

    def __new_gate_error_log(self, panel):
        self.__gate_error_log = self.__new_error_log(panel)
        kwargs = self.__get_gate_kwargs()
        if not self.__gate.is_gate_correct(kwargs):
            self.__gate_error_log.SetLabelText(self.__gate.why_gate_not_correct(kwargs))
        return self.__gate_error_log

    def __new_error_log(self, panel):
        error_log = wx.StaticText(panel)
        error_log.SetForegroundColour(wx.RED)
        return error_log

    def __new_parameters_views(self, panel):
        parameters_sizer = wx.BoxSizer(wx.VERTICAL)
        error_log_sizer, error_logs = self.__new_error_logs(panel)
        for parameter_name in self.__gate.get_parameters_names():
            parameter_view = ParameterView(panel, self.__gate, parameter_name, error_logs[parameter_name])
            self.__parameters_views.append(parameter_view)
            parameters_sizer.Add(parameter_view)
        parameters_sizer.Add(error_log_sizer)
        return parameters_sizer

    def __new_error_logs(self, panel):
        error_sizer = wx.BoxSizer(wx.VERTICAL)
        error_logs = {}
        for parameter_name in self.__gate.get_parameters_names():
            error_log = self.__new_error_log(panel)
            error_logs[parameter_name] = error_log
            error_sizer.Add(error_log)
        return error_sizer, error_logs

    def __new_ok_cancel(self, panel):
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(self.__new_ok(panel))
        btn_sizer.AddSpacer(10)
        btn_sizer.Add(self.__new_cancel(panel))
        return btn_sizer

    def __new_ok(self, panel):
        ok_btn = wx.Button(panel, label="ok")
        ok_btn.Bind(wx.EVT_BUTTON, self.__on_ok)
        kwargs = self.__get_gate_kwargs()
        ok_btn.Enable(self.__gate.is_gate_correct(kwargs))
        self.__ok_btn = ok_btn
        return ok_btn

    def __new_cancel(self, panel):
        cancel_btn = wx.Button(panel, label="cancel")
        cancel_btn.Bind(wx.EVT_BUTTON, self.__on_cancel)
        return cancel_btn

    def __on_ok(self, ev):
        for name, value in self.__get_gate_kwargs().items():
            self.__gate.set_parameter_value(name, value)
        self.EndModal(200)

    def __on_cancel(self, ev):
        self.__quantum_computer.removeGate(*self.__ij)
        self.EndModal(100)


class GatePlacer:

    def __init__(self, circuit, gate_mediator, quantum_computer):
        self.__circuit = circuit
        self.__gate_mediator = gate_mediator
        self.__quantum_computer = quantum_computer
        self.__parameters_dialog = None

    def placeGate(self, m_x, m_y):
        if self.__circuit.getW() > m_x > 2 * GATE_SIZE:
            if self.__circuit.getH(qbitAreaOnly=True) > m_y > 0:
                i,j = int(m_y / GATE_SIZE), int(m_x / (GATE_SIZE + GATE_H_SPACE))
                if self.__quantum_computer.can_add_gate_at(i, j):
                    self.__query_gate_parameters(self.__circuit.gateName, i, j)
        self.__gate_mediator.gateUnselected()
        self.__circuit.resetView()

    def __query_gate_parameters(self, gate_name, i, j):
        gate = self.__quantum_computer.add_gate(i, j, gate_name)
        if len(gate.get_parameters_names()) == 0:
            return
        dialog = ParameterDialog(self.__circuit, self.__quantum_computer, gate, i, j)
        dialog.ShowModal()
        dialog.Destroy()
