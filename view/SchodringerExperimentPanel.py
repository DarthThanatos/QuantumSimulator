import traceback

import matplotlib.patches
import matplotlib.lines
import wx
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from qutip import Bloch
import matplotlib.pyplot as plt
from model.constants import MASTERS_EQUATIONS, MONTE_CARLO
from util.Utils import new_big_font_label, newScaledImgBitmap, newStandardButton
from view.SchodringerMediator import SchodringerMediator
from view.constants import SCHODRINGER_EXPECTATIONS_FIGURE_ID, HAMILTONIAN_PANEL_ID, PSI_PANEL_ID
import numpy as np
from math import pi


class BlochEvolutionPanel(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow. __init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        self.figure = Figure(figsize=(3.,3.))
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


class GraphPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        fig = plt.figure(SCHODRINGER_EXPECTATIONS_FIGURE_ID, figsize=(4., 4.))
        FigureCanvas(self, -1, fig)
        times = np.linspace(0., 10., 20)
        plt.plot(times, np.cos(times))
        fig.axes[0].set_xlabel('Time')
        fig.axes[0].set_ylabel('Expectation values')
        self.__correct_axes(fig)
        plt.legend(["Sigma-Z", "Sigma-Y"])

    def __correct_axes(self, fig):
        ax = fig.axes[0]
        pos1 = ax.get_position() # get the original position
        pos2 = [pos1.x0, pos1.y0 * 2,  pos1.width, pos1.height]
        ax.set_position(pos2) # set a new position


class ImgPanel(wx.Panel):

    def __init__(self, parent, img_path, size):
        wx.Panel.__init__(self, parent, size=size)
        self.__bmp = newScaledImgBitmap(img_path, size)
        self.__size = size
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetBackgroundColour(wx.WHITE)
        self.Bind(wx.EVT_PAINT, self.__on_paint)

    def __on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        dc.DrawBitmap(self.__bmp, 0, 0)


class CenteredTextLatexPanel(wx.Panel):

    def __init__(self, parent, figure_number, figure_size):
        wx.Panel.__init__(self, parent)
        self.__fig = plt.figure(figure_number, figsize=figure_size)
        self.__fig_number = figure_number
        FigureCanvas(self, -1, self.__fig)
        plt.axis("off")
        self.__t = self._draw()

    def _draw(self):
        text = self._prepare_text()
        t = plt.text(0, 0, text, fontsize=23)
        self._center_text(t)
        return t

    def _get_text_coordinates(self, text):
        r = self.__fig.canvas.get_renderer()
        bb = text.get_window_extent(renderer=r)
        inv = self.__fig.axes[0].transData.inverted()
        x0, y0 = inv.transform((bb.x0, bb.y0))
        x1, y1 = inv.transform((bb.x1, bb.y1))
        return x0, y0, x1-x0, y1-y0

    def _draw_rect_to_text(self, text, fig):
        x0, y0, width, height = self._get_text_coordinates(text)
        rect = matplotlib.patches.Rectangle((x0, y0), width, height, linewidth=1, edgecolor='r', facecolor='none')
        fig.axes[0].add_patch(rect)

    def _draw_line(self, fig):
        l = matplotlib.lines.Line2D([0, 1], [.5, .5])
        fig.axes[0].add_line(l)

    def _center_text(self, t):
        _, _, width, height = self._get_text_coordinates(t)
        new_x = .5 - width * .5
        new_y = .5 - height * .25
        t.set_position((new_x, new_y))

    def _prepare_text(self):
        raise Exception("No prepared text to display")

    def _redraw(self):
        plt.figure(self.__fig_number)
        self.__t.remove()
        self.__t = self._draw()
        self.__fig.canvas.draw()


class MatrixPanel(CenteredTextLatexPanel):
    def __init__(self, parent, matrix, fig_numer):
        self.__matrix = matrix
        CenteredTextLatexPanel.__init__(self, parent, fig_numer, (4., .75))

    def _prepare_text(self):
        matrix = self.__matrix
        text = r'$H = \left[' \
               r' \stackrel{' + '{:.2f}'.format(matrix[0][0]) + '}{' + '{:.2f}'.format(matrix[0][1]) + r'}' \
               r'\,\,\,' \
               r' \stackrel{' + '{:.2f}'.format(matrix[1][0]) + '}{' + '{:.2f}'.format(matrix[1][1]) + r'}' \
               r'\right]$'
        return text

    def change_matrix_value(self, matrix):
        self.__matrix = matrix
        self._redraw()


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


class SchodringerExperimentPanel(wx.Panel):

    def __init__(self, splitter_parent, gate_mediator, quantum_computer):
        wx.Panel.__init__(self, splitter_parent)
        self.__should_show = False
        self.__sash_pos = 800
        self.__schodringer_mediator = self.__new_schodringer_mediator(gate_mediator, quantum_computer)
        self.__timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.__animate_showing, self.__timer)
        self.SetSizer(self.__new_root_sizer())

    def __new_schodringer_mediator(self, gate_mediator, quantum_computer):
        sm = SchodringerMediator(quantum_computer)
        sm.set_schodringer_panel(self)
        gate_mediator.set_schodringer_mediator(sm)
        return sm

    def __new_root_sizer(self):
        root_sizer = wx.BoxSizer(wx.VERTICAL)
        root_sizer.Add(self.__new_schodringer_title_view(), 0, wx.EXPAND)
        root_sizer.AddSpacer(30)
        root_sizer.Add(self.__new_experiment_sizer(), 0, wx.CENTER)
        return root_sizer

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
        self.__graph_panel = GraphPanel(self)
        return self.__graph_panel

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
        sizer.Add(self.__new_simulation_button(), 0, wx.CENTER)
        return sizer

    def __new_destroy_checkbox(self):
        destroy = wx.CheckBox(self, label="Destroy")
        self.__schodringer_mediator.set_destroy_checkbox(destroy)
        return destroy

    def __new_x_checkbox(self):
        x_checkbox = wx.CheckBox(self, label="X expectation")
        self.__schodringer_mediator.set_x_checkbox(x_checkbox)
        return x_checkbox

    def __new_y_checkbox(self):
        y_checkbox = wx.CheckBox(self, label="Y expectation")
        self.__schodringer_mediator.set_y_checkbox(y_checkbox)
        return y_checkbox

    def __new_z_checkbox(self):
        z_checkbox = wx.CheckBox(self, label="Z expectation")
        self.__schodringer_mediator.set_z_checkbox(z_checkbox)
        return z_checkbox

    def __new_steps_ctrl(self):
        steps_ctrl = wx.SpinCtrl(self, min=0, max=100, initial=20)
        self.__schodringer_mediator.set_steps_ctrl(steps_ctrl)
        return self.__new_titled_view("Simulation steps", steps_ctrl)

    def __new_simulation_button(self):
        self.__simulation_button = newStandardButton(self, (125,50), "start simulation", self.__change_simulation_mode)
        self.__schodringer_mediator.set_simulation_button(self.__simulation_button)
        return self.__simulation_button

    def __change_simulation_mode(self, _):
        self.__schodringer_mediator.change_simulation_mode()

    def __new_titled_view(self, title, view):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticText(self, label=title))
        sizer.AddSpacer(10)
        sizer.Add(view)
        return sizer

    def __new_simulation_choice(self):
        choices = [MONTE_CARLO, MASTERS_EQUATIONS]
        method_choice = wx.Choice(self, choices=choices)
        method_choice.SetSelection(0)
        self.__schodringer_mediator.set_metod_choice(method_choice)
        return self.__new_titled_view("Method of simulation", method_choice)

    def __new_coeff_input(self):
        coefficient_input = CoefficientInput(self)
        self.__schodringer_mediator.set_coefficient_input(coefficient_input)
        coefficient_input.set_schodringer_mediator(self.__schodringer_mediator)
        return self.__new_titled_view("tunnelling coefficient", coefficient_input)

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
            if self.__sash_pos > 230:
                self.__sash_pos -= 20
            else:
                self.__timer.Stop()
        parent.SetSashPosition(self.__sash_pos)

    def reset_view(self, should_show):
        self.__should_show = should_show
        self.__timer.Start(15)