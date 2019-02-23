import matplotlib.patches
import matplotlib.lines
import wx
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from qutip import Bloch
import matplotlib.pyplot as plt

from model.constants import MASTERS_EQUATIONS, MONTE_CARLO
from util.Utils import new_big_font_label, newScaledImgBitmap
from view.constants import SCHODRINGER_EXPECTATIONS_FIGURE_ID
import numpy as np


class BlochEvolutionPanel(wx.ScrolledWindow):
    def __init__(self, parent, gate_mediator, quantum_computer):
        wx.ScrolledWindow. __init__(self, parent, -1, style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
        self.__gate_mediator = gate_mediator
        self.__quantum_computer = quantum_computer
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

    def __init__(self, parent, gate_mediator, quantum_computer):
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


class MatrixCanvas(wx.Panel):
    def __init__(self, parent, matrix):
        wx.Panel.__init__(self, parent)
        fig = plt.figure(5, figsize=(6., .5))
        FigureCanvas(self, -1, fig)
        plt.axis("off")
        text = r'$|\psi>=|0>\,\,\,\,\,\, H = \left[\stackrel{3}{4} \,\,\, \stackrel{3}{4}\right]$'
        t = plt.text(0, 0, text, fontsize=23)
        _, _, width, height = self.__get_text_coordinates(t, fig)
        new_x = .5 - width * .5
        new_y = .5 - height * .25
        t.set_position((new_x, new_y))

    def __get_text_coordinates(self, text, fig):
        r = fig.canvas.get_renderer()
        bb = text.get_window_extent(renderer=r)
        inv = fig.axes[0].transData.inverted()
        x0, y0 = inv.transform((bb.x0, bb.y0))
        x1, y1 = inv.transform((bb.x1, bb.y1))
        return x0, y0, x1-x0, y1-y0

    def __draw_rect_to_text(self, text, fig):
        x0, y0, width, height = self.__get_text_coordinates(text, fig)
        rect = matplotlib.patches.Rectangle((x0, y0), width, height, linewidth=1, edgecolor='r', facecolor='none')
        fig.axes[0].add_patch(rect)

    def __draw_line(self, fig):
        l = matplotlib.lines.Line2D([0, 1], [.5, .5])
        fig.axes[0].add_line(l)

class PsiCanvas(wx.Panel):
    def __init__(self, parent, psi):
        wx.Panel.__init__(self, parent)
        fig = plt.figure(6, figsize=(2., .5))
        FigureCanvas(self, -1, fig)
        plt.axis("off")
        plt.text(0.5, 0, r'$|\psi>=|0>$ ', fontsize=23)


class SchodringerExperimentPanel(wx.Panel):

    def __init__(self, splitter_parent, gate_mediator, quantum_computer):
        wx.Panel.__init__(self, splitter_parent)
        self.__should_show = False
        self.__sash_pos = 800
        self.__quantum_computer = quantum_computer
        self.__gate_mediator = gate_mediator
        self.__timer = wx.Timer(self)
        self.SetSizer(self.__new_root_sizer())

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
        sizer.Add(GraphPanel(self, self.__gate_mediator, self.__quantum_computer))
        sizer.AddSpacer(20)
        sizer.Add(BlochEvolutionPanel(self, self.__gate_mediator, self.__quantum_computer))
        return sizer

    def __new_parameters_panel(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        choices = [MASTERS_EQUATIONS, MONTE_CARLO]
        sizer.Add(self.__new_simulation_choice(), choices=choices)
        sizer.Add(wx.CheckBox(self, label="X expectation"))
        sizer.Add(wx.CheckBox(self, label="Y expectation"))
        sizer.Add(wx.CheckBox(self, label="Z expectation"))
        sizer.AddSpacer(10)
        sizer.Add(self.__new_coeff_input())
        sizer.Add(wx.CheckBox(self, label="Destroy"))
        return sizer

    def __new_titled_view(self, title, view):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticText(self, label=title))
        sizer.AddSpacer(10)
        sizer.Add(view)
        return sizer

    def __new_simulation_choice(self):
        return self.__new_titled_view("Method of simulation", wx.Choice(self))

    def __new_coeff_input(self):
        return self.__new_titled_view("tunnelling coefficient", wx.TextCtrl(self, value="pi/2"))

    def __new_psi_view(self):
        return self.__new_titled_view("your psi", wx.StaticText(self, "|0>"))

    def __new_hamiltonian_view(self):
        return self.__new_titled_view("your hamiltonian", wx.StaticText(self, "hamiltonian values"))

    def __new_schodringer_title_view(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(new_big_font_label(self, "Schodringer Hamiltonian simulation"), 0, wx.CENTER)
        sizer.Add(ImgPanel(self, "../images/circuit/schodringer.png", (200, 100)), 0, wx.CENTER)
        horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        horizontal_sizer.Add(MatrixCanvas(self, []))
        sizer.Add(horizontal_sizer, 0, wx.CENTER)
        return sizer

    def animate_showing(self):
        parent = self.GetParent()
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
        parent.SetSashPosition(self.__sash_pos)
