import traceback

import wx
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from qutip import Bloch
import matplotlib.pyplot as plt
from model.constants import MASTERS_EQUATIONS, MONTE_CARLO
from util.Utils import new_big_font_label, newStandardButton, new_titled_view, ImgPanel, MatrixPanel, \
    CenteredTextLatexPanel, newIconButton, makeSelfIconButton
from view.SchodringerMediator import SchodringerMediator
from view.constants import SCHODRINGER_EXPECTATIONS_FIGURE_ID, HAMILTONIAN_PANEL_ID, PSI_PANEL_ID
import numpy as np
from math import pi
from wx.lib.scrolledpanel import ScrolledPanel


class BlochEvolutionPanel(wx.ScrolledWindow):

    def __init__(self, parent):
        wx.ScrolledWindow. __init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        self.figure = Figure(figsize=(2.,2.))
        FigureCanvas(self, -1, self.figure)
        b = Bloch(self.figure)
        b.make_sphere()
        self.__bloch = b

    def update_bloch(self, xs, ys, zs, state):
        b = self.__bloch
        b.clear()
        b.add_states(state)
        b.add_points([xs, ys, zs])
        b.make_sphere()
        b.fig.canvas.draw()

    def clean_bloch(self):
        b = self.__bloch
        b.clear()
        b.make_sphere()
        b.fig.canvas.draw()


class GraphPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        fig = plt.figure(SCHODRINGER_EXPECTATIONS_FIGURE_ID, figsize=(4.1, 2.5))
        FigureCanvas(self, -1, fig)
        plt.gca()
        fig.axes[0].set_xlabel('Time')
        fig.axes[0].set_ylabel('Expectation values')
        self.__correct_axes(fig)

    def __correct_axes(self, fig):
        ax = fig.axes[0]
        pos1 = ax.get_position() # get the original position
        pos2 = [pos1.x0, pos1.y0 * 2,  pos1.width, pos1.height]
        ax.set_position(pos2) # set a new position

    def plot(self, expect, steps, i, show_x=False, show_y=False, show_z=False):
        fig = plt.figure(SCHODRINGER_EXPECTATIONS_FIGURE_ID)
        plt.clf()
        times = np.linspace(0., 10., steps)
        for j in range(len(expect)):
            plt.plot(times, expect[j])
        self.__plot_legend(show_x, show_y, show_z, times[i])
        self.__correct_axes(fig)
        fig.canvas.draw()

    def __plot_legend(self, show_x, show_y, show_z, time):
        legend = []
        if show_x: legend.append("Sigma-X")
        if show_y: legend.append("Sigma-Y")
        if show_z: legend.append("Sigma-Z")
        plt.legend(legend)
        if len(legend) !=  0:
            plt.axvline(x=time, color='black')

    def clean(self):
        fig = plt.figure(SCHODRINGER_EXPECTATIONS_FIGURE_ID)
        plt.clf()
        plt.gca()
        self.__correct_axes(fig)
        fig.canvas.draw()


class PsiCanvas(CenteredTextLatexPanel):
    def __init__(self, parent, psi):
        self.__psi = psi
        CenteredTextLatexPanel.__init__(self, parent, PSI_PANEL_ID, (2., .75))

    def _prepare_text(self):
        return r'$|\psi_0>=|{}>$'.format(self.__psi)

    def change_psi_value(self, psi):
        self.__psi = psi
        self._redraw()


class CoefficientInput(wx.TextCtrl):

    def __init__(self, parent):
        value = "pi/2"
        wx.TextCtrl.__init__(self, parent, value=value, style=wx.TE_RICH | wx.WANTS_CHARS)
        self.__schodringer_mediator = None
        self.__last_correct_coeficient = float(eval(value))
        self.Bind(wx.EVT_KILL_FOCUS, self.__on_coeff_input_focus_lost)

    def set_schodringer_mediator(self, schodringer_mediator):
        self.__schodringer_mediator = schodringer_mediator

    def __on_coeff_input_focus_lost(self, event):
        current_value = self.GetValue()
        try:
            coefficient = float(eval(current_value))
            self.SetBackgroundColour(wx.WHITE)
            self.SetForegroundColour(wx.BLACK)
            if coefficient != self.__last_correct_coeficient:
                self.__last_correct_coeficient = coefficient
                if self.__schodringer_mediator:
                    self.__schodringer_mediator.coefficient_changed()
        except Exception:
            self.SetBackgroundColour(wx.RED)
            self.SetForegroundColour(wx.WHITE)
            traceback.print_exc()
        event.Skip()

    def get_coefficient(self):
        return self.__last_correct_coeficient


class ProgressSizer(wx.BoxSizer):

    def __init__(self, panel, mediator):
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        self.text = wx.StaticText(panel, label="Wait, loading")
        self.text.Show(False)
        self.progress_bar = self.__new_progress_bar(panel, mediator)
        self.Add(self.text)
        self.AddSpacer(10)
        self.Add(self.progress_bar)

    def __new_progress_bar(self, panel, mediator):
        progress_bar = wx.Gauge(panel)
        mediator.set_progress_bar(progress_bar)
        progress_bar.Show(False)
        return progress_bar

    def show_children(self, should_show):
        self.text.Show(should_show)
        self.progress_bar.Show(should_show)
        self.Layout()


class UpDownButton(wx.Button):

    def __init__(self, parent, schodringer_mediator):
        wx.Button.__init__(self, parent, size=(32,32))
        makeSelfIconButton(self, (32, 32), "../images/circuit/up.png")
        self.__up = False
        self.__schodringer_mediator = schodringer_mediator
        self.Bind(wx.EVT_BUTTON, self.__on_click)

    def __on_click(self, _):
        self.__up = not self.__up
        self.__update_bitmap()
        self.__schodringer_mediator.adjust_panel_position()

    def set_direction(self, is_up):
        self.__up = is_up
        self.__update_bitmap()

    def __update_bitmap(self):
        bmp_path = "../images/circuit/{}.png".format("up" if not self.__up else "down")
        makeSelfIconButton(self, (32,32), bmp_path)

    def is_up(self):
        return self.__up

class SchodringerExperimentPanel(ScrolledPanel):

    def __init__(self, splitter_parent, gate_mediator, quantum_computer):
        ScrolledPanel.__init__(self, splitter_parent)
        self.__should_show = False
        self.__sash_pos = 800
        self.max_sash_pos = 230
        self.__going_up = True
        self.__progress_sizer = None
        self.__schodringer_mediator = self.__new_schodringer_mediator(gate_mediator, quantum_computer)
        self.__timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.__animate_showing, self.__timer)
        self.__root_sizer = self.__new_root_sizer()
        self.SetSizer(self.__root_sizer)
        self.SetupScrolling()

    def __new_schodringer_mediator(self, gate_mediator, quantum_computer):
        sm = SchodringerMediator(quantum_computer)
        sm.set_schodringer_panel(self)
        gate_mediator.set_schodringer_mediator(sm)
        return sm

    def __new_root_sizer(self):
        root_sizer = wx.BoxSizer(wx.VERTICAL)
        root_sizer.Add(self.__new_up_arrow(), 0, wx.EXPAND)
        root_sizer.Add(self.__new_schodringer_title_view(), 0, wx.EXPAND)
        root_sizer.AddSpacer(30)
        root_sizer.Add(self.__new_experiment_sizer(), 0, wx.CENTER)
        return root_sizer

    def __new_up_arrow(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn = UpDownButton(self, self.__schodringer_mediator)
        self.__schodringer_mediator.set_up_button(btn)
        sizer.Add(wx.Panel(self), 10)
        sizer.Add(btn, 1)
        return sizer

    def __new_experiment_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.__new_parameters_panel(), 0, wx.CENTER)
        sizer.AddSpacer(20)
        sizer.Add(self.__new_graph_panel())
        sizer.AddSpacer(20)
        sizer.Add(self.__new_bloch_evolution_panel())
        return sizer

    def __new_bloch_evolution_panel(self):
        bloch_evolution_panel = BlochEvolutionPanel(self)
        self.__schodringer_mediator.set_bloch_evolution(bloch_evolution_panel)
        return bloch_evolution_panel

    def __new_graph_panel(self):
        graph_panel = GraphPanel(self)
        self.__schodringer_mediator.set_graph_panel(graph_panel)
        return graph_panel

    def __new_parameters_panel(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.__new_simulation_choice())
        sizer.Add(self.__new_x_checkbox())
        sizer.Add(self.__new_y_checkbox())
        sizer.Add(self.__new_z_checkbox())
        sizer.AddSpacer(10)
        sizer.Add(self.__new_steps_ctrl())
        sizer.Add(self.__new_coeff_input())
        sizer.Add(self.__new_destroy_checkbox())
        sizer.AddSpacer(10)
        sizer.Add(self.__new_progress_sizer(), 0, wx.CENTER)
        sizer.AddSpacer(10)
        sizer.Add(self.__new_simulation_button(), 0, wx.CENTER)
        return sizer

    def __new_progress_sizer(self):
        self.__progress_sizer = ProgressSizer(self, self.__schodringer_mediator)
        return self.__progress_sizer

    def __new_destroy_checkbox(self):
        destroy = wx.CheckBox(self, label="Destroy")
        destroy.SetValue(True)
        self.__schodringer_mediator.set_destroy_checkbox(destroy)
        return destroy

    def __new_x_checkbox(self):
        x_checkbox = wx.CheckBox(self, label="X expectation")
        x_checkbox.SetValue(True)
        self.__schodringer_mediator.set_x_checkbox(x_checkbox)
        return x_checkbox

    def __new_y_checkbox(self):
        y_checkbox = wx.CheckBox(self, label="Y expectation")
        y_checkbox.SetValue(True)
        self.__schodringer_mediator.set_y_checkbox(y_checkbox)
        return y_checkbox

    def __new_z_checkbox(self):
        z_checkbox = wx.CheckBox(self, label="Z expectation")
        z_checkbox.SetValue(True)
        self.__schodringer_mediator.set_z_checkbox(z_checkbox)
        return z_checkbox

    def __new_steps_ctrl(self):
        steps_ctrl = wx.SpinCtrl(self, min=0, max=100, initial=20)
        self.__schodringer_mediator.set_steps_ctrl(steps_ctrl)
        return new_titled_view(self, "Simulation steps", steps_ctrl)

    def __new_simulation_button(self):
        self.__simulation_button = newStandardButton(self, (125,50), "start simulation", self.__change_simulation_mode)
        self.__schodringer_mediator.set_simulation_button(self.__simulation_button)
        return self.__simulation_button

    def __change_simulation_mode(self, _):
        self.__schodringer_mediator.change_simulation_mode()

    def __new_simulation_choice(self):
        choices = [MONTE_CARLO, MASTERS_EQUATIONS]
        method_choice = wx.Choice(self, choices=choices)
        method_choice.SetSelection(0)
        self.__schodringer_mediator.set_metod_choice(method_choice)
        return new_titled_view(self, "Method of simulation", method_choice)

    def __new_coeff_input(self):
        coefficient_input = CoefficientInput(self)
        self.__schodringer_mediator.set_coefficient_input(coefficient_input)
        coefficient_input.set_schodringer_mediator(self.__schodringer_mediator)
        return new_titled_view(self, "tunnelling coefficient", coefficient_input)

    def __new_matrix_canvas(self):
        matrix_panel = MatrixPanel(self, [[0, 0], [0, 0]], HAMILTONIAN_PANEL_ID)
        self.__schodringer_mediator.set_matrix_panel(matrix_panel)
        return matrix_panel

    def __new_schodringer_title_view(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(new_big_font_label(self, "Schodringer Hamiltonian simulation"), 0, wx.CENTER)
        sizer.Add(ImgPanel(self, "../images/circuit/schodringer.png", (200, 100)), 0, wx.CENTER)
        horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        horizontal_sizer.Add(self.__new_psi_panel())
        horizontal_sizer.AddSpacer(10)
        horizontal_sizer.Add(self.__new_matrix_canvas())
        sizer.Add(horizontal_sizer, 0, wx.CENTER)
        return sizer

    def __new_psi_panel(self):
        psi_panel = PsiCanvas(self, 0)
        self.__schodringer_mediator.set_psi_panel(psi_panel)
        return psi_panel

    def __animate_showing(self, event):
        parent = self.GetParent()
        if not self.__should_show:
            if self.__sash_pos < 800:
                self.__sash_pos += 20
            else:
                self.__timer.Stop()
        else:
            if self.__going_up:
                if self.__sash_pos > self.max_sash_pos:
                    self.__sash_pos -= 20
                else:
                    self.__sash_pos = self.max_sash_pos
                    self.__timer.Stop()
            else:
                if self.__sash_pos < self.max_sash_pos:
                    self.__sash_pos += 20
                else:
                    self.__sash_pos = self.max_sash_pos
                    self.__timer.Stop()
        parent.SetSashPosition(self.__sash_pos)
        event.Skip()

    def show_progress(self, should_show):
        self.__progress_sizer.show_children(should_show)
        self.__root_sizer.Layout()
        self.SetupScrolling()

    def reset_view(self, should_show, going_up=True):
        self.__going_up = going_up
        self.__should_show = should_show
        self.__timer.Start(15)
