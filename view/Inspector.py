import colorsys
from math import pi

from util.Utils import *
from wx.lib.scrolledpanel import ScrolledPanel

from qutip import Bloch
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import matplotlib.pyplot as plt


class BlochCanvas(wx.ScrolledWindow):
    def __init__(self, parent, gate_mediator, quantum_computer):
        wx.ScrolledWindow. __init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        self.__gate_mediator = gate_mediator
        gate_mediator.set_bloch_canvas(self)
        self.__quantum_computer = quantum_computer
        self.figure = Figure()
        FigureCanvas(self, -1, self.figure)
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


class RestoreExperimentButton(wx.Button):

    def __init__(self, parent, label, experiment_index, gate_mediator, quantum_computer):
        wx.Button.__init__(self, parent, label = label, size=(-1, 50))
        self.__gate_mediator = gate_mediator
        self.__experiment_index = experiment_index
        self.__quantum_computer = quantum_computer
        self.Bind(wx.EVT_BUTTON, self.__on_click)

    def __on_click(self, event):
        self.__quantum_computer.restore_experiment_at(self.__experiment_index)
        self.__gate_mediator.experiment_changed()


class HistoryPanel(ScrolledPanel):

    def __init__(self, parent, gate_mediator, quantum_computer):
        super().__init__(parent)
        self.__quantum_computer = quantum_computer
        self.__gate_mediator = gate_mediator
        gate_mediator.set_history_panel(self)
        self.__root_sizer = wx.BoxSizer(wx.VERTICAL)
        self.__create_new_history_view()
        self.SetSizer(self.__root_sizer)

    def __create_new_history_view(self):
        self.Freeze()
        self.__root_sizer.AddSpacer(20)
        self.__root_sizer.Add(new_big_font_label(self, "History of experiments"), 0, wx.CENTER)
        self.__root_sizer.AddSpacer(20)
        for experiment in self.__quantum_computer.all_experiments():
            label = "restore experiment {} created at {}".format(experiment.index(), experiment.date())
            self.__root_sizer.Add(RestoreExperimentButton(self, label, experiment.index(), self.__gate_mediator, self.__quantum_computer), 0, wx.CENTER)
        self.__root_sizer.Layout()
        self.SetupScrolling()
        self.Thaw()

    def reset_view(self):
        self.DestroyChildren()
        self.__root_sizer.Clear()
        self.__create_new_history_view()


class CircuitInspector(wx.SplitterWindow):

    ARGAND_FIGURE_ID = 0

    def __init__(self, parent, gate_mediator, quantum_computer):
        wx.SplitterWindow.__init__(self, parent, style=wx.SP_LIVE_UPDATE | wx.SP_3DSASH, size=(450, 1000))
        self.__quantum_computer = quantum_computer
        self.__gate_mediator = gate_mediator
        gate_mediator.set_circuit_inspector(self)
        self.__bloch_canvas = BlochCanvas(self, gate_mediator, quantum_computer)
        self.__probs_area = None
        self.SplitHorizontally(self.__new_probs_history_splitter(), self.__bloch_canvas)
        self.__sash_pos = 800
        self.SetSashPosition(self.__sash_pos)
        self.__should_show = False
        self.Bind(wx.EVT_SIZE, self.onresize)
        self.__timer = wx.Timer(self.__bloch_canvas)
        self.__bloch_canvas.Bind(wx.EVT_TIMER, self.__show_bloch, self.__timer)
        self.__bind()

    def __new_probs_history_splitter(self):
        probs_history_splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE | wx.SP_3DSASH)
        probs_panel = self.__new_probs_panel(probs_history_splitter)
        history_panel = HistoryPanel(probs_history_splitter, self.__gate_mediator, self.__quantum_computer)
        probs_history_splitter.SplitHorizontally(probs_panel, history_panel, 375)
        return probs_history_splitter

    def __new_probs_panel(self, parent):
        panel = ScrolledPanel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(20)
        sizer.Add(new_big_font_label(panel, "State of the register"), 0, wx.CENTER)
        sizer.AddSpacer(20)
        self.__probs_area = wx.TextCtrl(panel, style=wx.TE_READONLY | wx.TE_CENTRE | wx.TE_MULTILINE | wx.NO_BORDER)
        self.__probs_area.SetValue(self.__quantum_computer.current_simulation_psi_str())
        sizer.Add(self.__probs_area, 0, wx.EXPAND)
        sizer.Add(self.__qubit_state_argand(panel), wx.CENTER, wx.EXPAND)
        sizer.Layout()
        panel.SetSizer(sizer)
        panel.SetupScrolling()
        return panel

    def __qubit_state_argand(self, panel):
        fig = plt.figure(self.ARGAND_FIGURE_ID, figsize=(3., 3.))
        self.__visualize_complex(0+0j)
        return FigureCanvas(panel, -1, fig)

    def __visualize_complex(self, x):
        plt.figure(self.ARGAND_FIGURE_ID)
        self.__palette()
        plt.polar([0, np.angle(x)], [0, 1], marker=',', c=[0,0,0])
        plt.polar(np.angle(x), 1, marker=10, c=[0,0,0])

    def __palette(self):
        xval = np.arange(0, 2 * pi, 0.01)
        N = len(xval)
        HSV_tuples = [(x*1.0/N, 0.5, 0.5) for x in range(N)]
        RGB_tuples = list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))
        for i, x in enumerate(xval):
            plt.polar([0, x], [0, 1], marker=',', c=RGB_tuples[i])  # first are angles, second are rs

    def __bind(self):
        self.Bind(wx.EVT_SPLITTER_DCLICK, self.__dev_null)
        self.Bind(wx.EVT_SPLITTER_DOUBLECLICKED, self.__dev_null)
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.__dev_null)
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.__dev_null)
        self.Bind(wx.EVT_SPLITTER_UNSPLIT, self.__dev_null)

    def __dev_null(self, event):
        event.Veto()

    def reset_view(self):
        nqubits = self.__quantum_computer.circuit_qubits_number()
        self.__should_show = nqubits == 1
        self.__timer.Start(20)
        self.__probs_area.SetValue(self.__quantum_computer.current_simulation_psi_str())

    def __show_bloch(self, _):
        if not self.__should_show:
            if self.__sash_pos < 800:
                self.__sash_pos += 40
            else:
                self.__timer.Stop()
        else:
            if self.__sash_pos > 375:
                self.__sash_pos -= 40
            else:
                self.__timer.Stop()
        self.SetSashPosition(self.__sash_pos)

    def onresize(self, ev):
        self.__bloch_canvas.initSize()
        ev.Skip()

    def setInspector(self, inspector):
        self.inspector = inspector

    def destroy(self):
        self.inspector = None

