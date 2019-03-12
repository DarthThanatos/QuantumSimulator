import colorsys
from math import pi

from util.Utils import *
from wx.lib.scrolledpanel import ScrolledPanel

from qutip import Bloch
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import matplotlib.pyplot as plt
import wx.grid

from view.ParametersDialog import GateInspectorPanel
from view.ProbabilitiesTable import ProbabilitiesTable


class BlochCanvas(wx.ScrolledWindow):
    def __init__(self, parent, gate_mediator, quantum_computer):
        wx.ScrolledWindow. __init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        self.__gate_mediator = gate_mediator
        gate_mediator.set_bloch_canvas(self)
        self.__quantum_computer = quantum_computer
        self.figure = Figure(figsize=(2.,2.))
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(FigureCanvas(self, -1, self.figure), wx.CENTER)
        sizer.Layout()
        self.SetSizer(sizer)
        b = Bloch(self.figure)
        b.make_sphere()
        self.__bloch = b

    def reset_view(self):
        nqubits = self.__quantum_computer.circuit_qubits_number()
        psi = self.__quantum_computer.current_simulation_psi()
        if nqubits != 1:
            return
        self.__bloch.clear()
        self.__bloch.add_states(psi)
        self.__bloch.make_sphere()
        self.__bloch.fig.canvas.draw()

    def initSize(self):
        w,h = self.GetClientSize()
        if w == 0 or h == 0: return
        ppiw, ppih = wx.GetDisplayPPI()
        self.figure.set_size_inches( (w / ppiw, w / ppiw))


class ExperimentMediator:

    def __init__(self, history_panel, gate_mediator, quantum_computer):
        self.__history_panel = history_panel
        self.__gate_mediator = gate_mediator
        self.__quantum_computer = quantum_computer

    def on_restore(self, restore_button):
        experiment_index = restore_button.experiment_index()
        self.__quantum_computer.restore_experiment_at(experiment_index)
        self.__gate_mediator.experiment_changed()

    def on_delete(self, delete_button):
        experiment_index = delete_button.experiment_index()
        try:
            self.__quantum_computer.remove_experiment(experiment_index)
            self.__gate_mediator.experiment_deleted()
        except Exception as e:
            wx.MessageBox(str(e), 'Error', wx.OK | wx.ICON_ERROR)

    def on_rename(self, rename_button):
        dlg = wx.TextEntryDialog(self.__history_panel, 'New experiment name', 'New name for experiment with id {}'.format(rename_button.experiment_index()))
        dlg.SetValue("")
        dlg.SetMaxLength(10)
        if dlg.ShowModal() == wx.ID_OK:
            self.__quantum_computer.rename_experiment(rename_button.experiment_index(), dlg.GetValue())
        dlg.Destroy()
        self.__gate_mediator.history_changed()

    def all_experiments(self):
        return self.__quantum_computer.all_experiments()

    def max_experiment_button_width(self):
        all_experiments = self.__quantum_computer.all_experiments()
        max_width = 0
        for experiment in all_experiments:
            dc = wx.ScreenDC()
            label = self.get_restore_experiment_label(experiment.name(), experiment.date())
            w,_ = dc.GetTextExtent(label)
            max_width = max(max_width, w)
        return max_width

    def get_restore_experiment_label(self, experiment_name, experiment_date):
        return "{} created at {}".format(experiment_name, experiment_date.strftime("%Y-%m-%d %H:%M"))


class HistoryButton(wx.Button):

    def __init__(self, parent, size, experiment_index, experiment_mediator):
        wx.Button.__init__(self, parent, size=size)
        self._experiment_mediator = experiment_mediator
        self.__experiment_index = experiment_index
        self._init_view()
        self.Bind(wx.EVT_BUTTON, self.__on_click)

    def experiment_index(self):
        return self.__experiment_index

    def _init_view(self):
        raise Exception("init view not implemented")

    def __on_click(self, event):
        self._history_operation()

    def _history_operation(self):
        raise Exception("history operation not implemented")


class RestoreExperimentButton(HistoryButton):

    def __init__(self, parent, label, experiment_index, experiment_mediator):
        self.__label = label
        max_size = experiment_mediator.max_experiment_button_width()
        HistoryButton.__init__(self, parent, (max_size, 50), experiment_index, experiment_mediator)

    def _init_view(self):
        self.SetLabelText(self.__label)

    def _history_operation(self):
        self._experiment_mediator.on_restore(self)


class DeleteExperimentButton(HistoryButton):
    def __init__(self, parent, experiment_index, experiment_mediator):
        HistoryButton.__init__(self, parent, (50, 50), experiment_index, experiment_mediator)

    def _init_view(self):
        makeSelfIconButton(self, (50, 50), "../images/circuit/delete.png")

    def _history_operation(self):
        self._experiment_mediator.on_delete(self)


class RenameExperimentButton(HistoryButton):
    def __init__(self, parent, experiment_index, experiment_mediator):
        HistoryButton.__init__(self, parent, (50,50), experiment_index, experiment_mediator)

    def _init_view(self):
        makeSelfIconButton(self, (50, 50), "../images/circuit/rename.png")

    def _history_operation(self):
        self._experiment_mediator.on_rename(self)


class HistoryPanel(ScrolledPanel):

    def __init__(self, parent, gate_mediator, quantum_computer):
        super().__init__(parent)
        self.__experiment_mediator = ExperimentMediator(self, gate_mediator, quantum_computer)
        gate_mediator.set_history_panel(self)
        self.__root_sizer = wx.BoxSizer(wx.VERTICAL)
        self.__create_new_history_view()
        self.SetSizer(self.__root_sizer)

    def __create_new_history_view(self):
        self.Freeze()
        self.__root_sizer.AddSpacer(20)
        self.__root_sizer.Add(new_big_font_label(self, "History of experiments"), 0, wx.CENTER)
        self.__root_sizer.AddSpacer(20)
        for experiment in self.__experiment_mediator.all_experiments():
            label = self.__experiment_mediator.get_restore_experiment_label(experiment.name(), experiment.date())
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(RestoreExperimentButton(self, label, experiment.index(), self.__experiment_mediator))
            sizer.AddSpacer(10)
            sizer.Add(RenameExperimentButton(self, experiment.index(), self.__experiment_mediator))
            sizer.AddSpacer(10)
            sizer.Add(DeleteExperimentButton(self, experiment.index(), self.__experiment_mediator))
            self.__root_sizer.Add(sizer, 0, wx.CENTER)
        self.__root_sizer.Layout()
        self.SetupScrolling()
        self.Thaw()

    def reset_view(self):
        self.DestroyChildren()
        self.__root_sizer.Clear()
        self.__create_new_history_view()


class HideRegisterQubitsDialog(wx.Dialog):

    def __init__(self, parent, already_hidden=None):
        wx.Dialog.__init__(self, parent, size=(550, 250), title="Qubits in register selection", style=wx.NO_BORDER)
        root_sizer = self.__new_root_sizer()
        root_sizer.Layout()
        self.SetSizer(root_sizer)

        x,y = get_screen_middle_point()
        WIDTH, HEIGHT = self.GetSize()
        x,y = x - WIDTH/2, y - HEIGHT/2
        self.SetPosition((x, y))

    def __new_root_sizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(new_big_font_label(self, "Select qubits to hide in the register"), 0, wx.CENTER)
        sizer.AddSpacer(40)
        sizer.Add(self.__new_hide_checkboxes_panel(), 0, wx.CENTER)
        sizer.AddSpacer(30)
        sizer.Add(self.__new_buttons_panel(), 0, wx.CENTER)
        return sizer

    def __new_hide_checkboxes_panel(self):
        panel = ScrolledPanel(self, size=(500, 85), style=wx.SUNKEN_BORDER)
        sizer = wx.BoxSizer(wx.VERTICAL)
        for i in range(13):
            checkbox = wx.CheckBox(panel, label="Hide qubit {}".format(i))
            sizer.Add(checkbox, 0, wx.CENTER)
        panel.SetSizer(sizer)
        sizer.Layout()
        panel.SetupScrolling()
        return panel

    def __new_buttons_panel(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(newStandardButton(self, (75, 25), "ok", self.__on_ok))
        sizer.AddSpacer(20)
        sizer.Add(newStandardButton(self, (75, 25), "cancel", self.__on_cancel))
        return sizer

    def __on_ok(self, _):
        self.EndModal(wx.OK)

    def __on_cancel(self, _):
        self.EndModal(wx.CANCEL)


class ProbsPanelMediator:

    def __init__(self, probs_panel):
        self.__probs_panel = probs_panel
        self.__argand_panel = None
        self.__probabilities_table = None

    def set_argand_panel(self, argand_panel):
        self.__argand_panel = argand_panel

    def set_probabilities_table(self, probabilities_table):
        self.__probabilities_table = probabilities_table

    def show_partially(self):
        self.__probabilities_table.Hide()
        # self.__argand_panel.Hide()
        self.__probs_panel.layout()
        self.__probs_panel.Show()

    def show_fully(self):
        self.__probabilities_table.Show()
        # self.__argand_panel.Show()
        self.__probs_panel.layout()
        self.__probs_panel.Show()

    def visualise_amplitude(self, amplitude):
        self.__probs_panel.visualize_complex(amplitude)

    def probs_table_resized(self):
        self.__probs_panel.layout()
        self.__probs_panel.SetupScrolling()

    def on_hide_register_qubits(self, quantum_computer):
        dialog = HideRegisterQubitsDialog(self.__probs_panel)
        status = dialog.ShowModal()
        if status == wx.OK:
            print("ok")
        else:
            print("cancel")
        dialog.Destroy()


class ProbsPanel(ScrolledPanel):

    def __init__(self, parent, gate_mediator, quantum_computer):
        ScrolledPanel.__init__(self, parent)
        self.__quantum_computer = quantum_computer
        self.__gate_mediator = gate_mediator
        self.__gate_mediator.set_probs_panel(self)
        self.__probabilities_mediator = ProbsPanelMediator(self)
        self.__root_sizer = wx.BoxSizer(wx.VERTICAL)
        self.__argand_vector_base = None
        self.__argand_vector_arrow = None
        self.__argand_background_drawn = False
        self.__init_root_sizer()
        self.SetSizer(self.__root_sizer)
        self.SetBackgroundColour(wx.WHITE)
        self.SetupScrolling()

    def reset_view(self):
        self.Freeze()
        self.DestroyChildren()
        self.__root_sizer.Clear()
        self.__init_root_sizer()
        self.Refresh()
        self.Thaw()
        self.SetupScrolling()

    def __init_root_sizer(self):
        self.__root_sizer.AddSpacer(20)
        self.__root_sizer.Add(new_big_font_label(self, "State of the register"), 0, wx.CENTER)
        self.__root_sizer.AddSpacer(20)
        self.__root_sizer.Add(self.__new_probabilities_table(), 0, wx.CENTER)
        self.__root_sizer.AddSpacer(20)
        self.__root_sizer.Add(self.__new_hide_register_qubits_button(),0, wx.CENTER)
        # self.__root_sizer.Add(self.__qubit_state_argand(), wx.CENTER, wx.EXPAND)
        self.__root_sizer.Layout()

    def __new_hide_register_qubits_button(self):
        btn = newStandardButton(self, (75,25), "hide qubits", self.__on_hide_register_qubits)
        return btn

    def __on_hide_register_qubits(self, _):
        self.__probabilities_mediator.on_hide_register_qubits(self.__quantum_computer)

    def __new_probabilities_table(self):
        representation = self.__gate_mediator.current_psi_representation(self.__quantum_computer)
        probabilities_table = ProbabilitiesTable(self,  representation, self.__probabilities_mediator)
        self.__probabilities_mediator.set_probabilities_table(probabilities_table)
        return probabilities_table

    def __qubit_state_argand(self, ):
        fig = plt.figure(ARGAND_FIGURE_ID, figsize=(2., 2.5))
        argand_panel = self.__new_argand_sizer(fig)
        self.__palette()
        self.__probabilities_mediator.set_argand_panel(argand_panel)
        return argand_panel

    def __new_argand_sizer(self, fig):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(FigureCanvas(self, -1, fig), 3)
        sizer.Add(wx.Panel(self), 1)
        # sizer.Add(wx.Panel(self), wx.CENTER)
        return sizer

    def visualize_complex(self, x):
        fig = plt.figure(ARGAND_FIGURE_ID)
        self.__remove_previous_argand_pointer()
        self.__argand_vector_base = plt.polar([0, np.angle(x)], [0, 1], marker=',', c=[0,0,0])[0]
        self.__argand_vector_arrow = plt.polar(np.angle(x), 1, marker=10, c=[0,0,0])[0]
        fig.canvas.draw()

    def __palette(self,):
        if not self.__argand_background_drawn:
            xval = np.arange(0, 2 * pi, 0.017)
            N = len(xval)
            HSV_tuples = [(x*1.0/N, 0.5, 0.5) for x in range(N)]
            RGB_tuples = list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))
            for i, x in enumerate(xval):
                plt.polar([0, x], [0, 1], marker=',', c=RGB_tuples[i])  # first are angles, second are rs
            plt.gca().set_yticks([])
            self.__argand_background_drawn = True
        self.__remove_previous_argand_pointer()

    def __remove_previous_argand_pointer(self):
        if self.__argand_vector_base:
            self.__argand_vector_base.remove()
            self.__argand_vector_arrow.remove()
            self.__argand_vector_arrow = None
            self.__argand_vector_base = None

    def layout(self):
        self.__root_sizer.Layout()

    def show_partially(self):
        self.__probabilities_mediator.show_partially()

    def show_fully(self):
        self.__probabilities_mediator.show_fully()

INSPECTOR_MAIN_SASH = 250

class CircuitInspector(wx.SplitterWindow):

    def __init__(self, parent, gate_mediator, quantum_computer):
        wx.SplitterWindow.__init__(self, parent, style=wx.SP_LIVE_UPDATE | wx.SP_3DSASH, size=(350, 1000))
        self.__quantum_computer = quantum_computer
        self.__gate_mediator = gate_mediator
        gate_mediator.set_circuit_inspector(self)
        self.__probs_panel = None
        self.__bloch_canvas = None
        self.SplitHorizontally(self.__new_probs_history_splitter(), self.__new_bloch_sizer())
        self.__sash_pos = 800
        self.SetSashPosition(self.__sash_pos)
        self.__should_show_bloch = False
        #self.Bind(wx.EVT_SIZE, self.onresize)
        self.__timer = wx.Timer(self.__bloch_canvas)
        self.__bloch_canvas.Bind(wx.EVT_TIMER, self.__show_bloch, self.__timer)
        self.__bind(self)

    def __new_bloch_sizer(self):
        panel = wx.Panel(self)
        self.__bloch_canvas = BlochCanvas(panel, self.__gate_mediator, self.__quantum_computer)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.Panel(panel), wx.CENTER)
        sizer.Add(self.__bloch_canvas, wx.CENTER)
        sizer.Add(wx.Panel(panel), wx.CENTER)
        panel.SetSizer(sizer)
        sizer.Layout()
        return panel

    def __new_probs_history_splitter(self):
        probs_history_splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE | wx.SP_3DSASH)
        gate_insp_history_splitter = self.__new_gate_inspector_history_splitter(probs_history_splitter)
        probs_panel = ProbsPanel(probs_history_splitter, self.__gate_mediator, self.__quantum_computer)
        self.__probs_panel = probs_panel
        probs_history_splitter.SplitHorizontally(probs_panel, gate_insp_history_splitter, INSPECTOR_MAIN_SASH)
        return probs_history_splitter

    def __new_gate_inspector_history_splitter(self, probs_history_splitter):
        gate_inspt_hist_splitter = wx.SplitterWindow(probs_history_splitter, style=wx.SP_LIVE_UPDATE | wx.SP_3DSASH)
        history_panel = HistoryPanel(gate_inspt_hist_splitter, self.__gate_mediator, self.__quantum_computer)
        gate_inspector_panel = GateInspectorPanel(gate_inspt_hist_splitter, self.__gate_mediator)
        gate_inspt_hist_splitter.SplitVertically(gate_inspector_panel, history_panel, 1)
        return gate_inspt_hist_splitter


    def __new_gateinsp_probs_splitter(self, probs_history_splitter):
        gateinsp_probs_splitter = wx.SplitterWindow(probs_history_splitter, style=wx.SP_LIVE_UPDATE | wx.SP_3DSASH)
        probs_panel = ProbsPanel(gateinsp_probs_splitter, self.__gate_mediator, self.__quantum_computer)
        gate_inspector_panel = GateInspectorPanel(gateinsp_probs_splitter, self.__gate_mediator)
        gateinsp_probs_splitter.SplitVertically(gate_inspector_panel, probs_panel, 1)
        self.__bind(gateinsp_probs_splitter)
        self.__probs_panel = probs_panel
        return gateinsp_probs_splitter

    def __bind(self, splitter):
        splitter.Bind(wx.EVT_SPLITTER_DCLICK, self.__dev_null)
        splitter.Bind(wx.EVT_SPLITTER_DOUBLECLICKED, self.__dev_null)
        splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.__dev_null)
        splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.__dev_null)
        splitter.Bind(wx.EVT_SPLITTER_UNSPLIT, self.__dev_null)

    def __dev_null(self, event):
        event.Veto()

    def reset_view(self):
        nqubits = self.__quantum_computer.circuit_qubits_number()
        self.__should_show_bloch = nqubits == 1
        self.__timer.Start(20)
        self.__probs_panel.reset_view()

    def __show_bloch(self, event):
        if not self.__should_show_bloch:
            if self.__sash_pos < 800:
                self.__sash_pos += 40
            else:
                self.__timer.Stop()
        else:
            if self.__sash_pos > INSPECTOR_MAIN_SASH:
                self.__sash_pos -= 40
            else:
                self.__timer.Stop()
        self.SetSashPosition(self.__sash_pos)
        event.Skip()

    def onresize(self, ev):
        self.__bloch_canvas.initSize()
        ev.Skip()

