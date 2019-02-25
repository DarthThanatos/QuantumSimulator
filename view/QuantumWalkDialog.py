import wx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from util.Utils import get_screen_middle_point, new_big_font_label, newStandardButton, new_titled_view, ImgPanel
from view.constants import QUANTUM_WALK_FIGURE_ID
from wx.lib.scrolledpanel import ScrolledPanel


class QuantumWalkMediator:

    def __init__(self, quantum_walk_panel, quantum_computer):
        self.__quantum_walk_panel = quantum_walk_panel
        self.__quantum_computer = quantum_computer
        self.__graph_panel = None
        self.__simulation_btn = None
        self.__center_slider = None
        self.__t_number_ctrl = None
        self.__vertices_number_label = None
        self.__center_ctrl = None
        self.__clear_checkbox = None

    def set_clear_checkbox(self, clear_checkbox):
        self.__clear_checkbox = clear_checkbox

    def set_graph_panel(self, graph_panel):
        self.__graph_panel = graph_panel

    def set_simulation_button(self, simulation_btn):
        self.__simulation_btn = simulation_btn

    def set_center_slider(self, center_slider):
        self.__center_slider = center_slider

    def set_t_number_ctrl(self, t_number_ctrl):
        self.__t_number_ctrl = t_number_ctrl

    def set_vertices_number_label(self, vertices_number_label):
        self.__vertices_number_label = vertices_number_label

    def set_graph_center_ctrl(self, graph_center_ctrl):
        self.__center_ctrl = graph_center_ctrl

    def change_start_ctrl(self):
        value = self.__center_ctrl.GetValue()
        if value != self.__center_slider.GetValue():
            self.__center_slider.SetValue(value)

    def change_start_slider(self):
        value = self.__center_slider.GetValue()
        if value != self.__center_ctrl.GetValue():
            self.__center_ctrl.SetValue(value)

    def steps_changed(self):
        value = self.__t_number_ctrl.GetValue()
        self.__vertices_number_label.SetLabel(TOTAL_VERTICES_NUMBER_LABEL.format(2*value + 1))
        self.__center_slider.SetRange(-value, value)
        self.__center_slider.SetValue(0)
        self.__center_ctrl.SetRange(-value, value)
        self.__center_slider.SetValue(0)

    def simulate(self):
        t = self.__t_number_ctrl.GetValue()
        center = self.__center_slider.GetValue()
        p_p = self.__quantum_computer.simulate_quantum_walk(t, center)
        if self.__clear_checkbox.IsChecked():
            self.__graph_panel.clear()
        self.__graph_panel.plot_pdf(p_p)


WIDTH = 750
HEIGHT = 800
TOTAL_VERTICES_NUMBER_LABEL = "total vertices number = 2t + 1 = {}"


class GraphPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        fig = plt.figure(QUANTUM_WALK_FIGURE_ID, figsize=(5., 5.))
        FigureCanvas(self, -1, fig)
        self.clear()

    def plot_pdf(self, P_p):
        fig = plt.figure(QUANTUM_WALK_FIGURE_ID)
        lattice_positions = range(int(-len(P_p) / 2 + 1), int(len(P_p) / 2 + 2))
        plt.plot(lattice_positions, P_p)
        plt.xlim([-len(P_p) / 2 + 2, len(P_p) / 2 + 2])
        plt.ylim([min(P_p), max(P_p) + 0.01])
        fig.canvas.draw()

    def clear(self):
        plt.figure(QUANTUM_WALK_FIGURE_ID)
        plt.clf()
        plt.gca()
        plt.ylabel(r'$Probablity$')
        plt.xlabel(r'$Particle \ position$')


class QuantumWalkScrollPanel(ScrolledPanel):
    def __init__(self, parent, quantum_computer):
        ScrolledPanel.__init__(self, parent)
        self.__quantum_computer = quantum_computer
        self.__qw_mediator = QuantumWalkMediator(self, quantum_computer)
        self.__root_sizer = self.__new_root_sizer()
        self.SetSizer(self.__root_sizer)
        self.SetBackgroundColour(wx.WHITE)
        self.SetupScrolling()

    def __new_root_sizer(self):
        root_sizer = wx.BoxSizer(wx.VERTICAL)
        root_sizer.Add(new_big_font_label(self, "\n Unlocked achievement. \n Quantum walk along a two dimensional line graph!"), 0, wx.CENTER)
        root_sizer.Add(ImgPanel(self, "../images/modules/path_graph.png", (WIDTH/2, HEIGHT/2)), 0,  wx.CENTER)
        root_sizer.Add(self.__new_graph_panel(), 0, wx.CENTER)
        root_sizer.AddSpacer(20)
        root_sizer.Add(self.__new_parameters_sizer(), 0, wx.CENTER)
        root_sizer.AddSpacer(20)
        root_sizer.Add(self.__new_graph_center_sizer(), 0, wx.CENTER)
        root_sizer.AddSpacer(10)
        root_sizer.Add(self.__new_clear_checkbox(), 0, wx.CENTER)
        root_sizer.AddSpacer(30)
        root_sizer.Add(self.__new_simulation_button(), 0, wx.CENTER)
        root_sizer.AddSpacer(20)
        root_sizer.Layout()
        return root_sizer

    def __new_clear_checkbox(self):
        clear_checkbox = wx.CheckBox(self, label="clear canvas after simulation")
        self.__qw_mediator.set_clear_checkbox(clear_checkbox)
        return clear_checkbox

    def __new_parameters_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.__new_t_number_ctrl(), wx.CENTER)
        sizer.AddSpacer(10)
        sizer.Add(self.__new_vertices_number_label(), wx.CENTER)
        return sizer

    def __new_graph_panel(self):
        graph_panel = GraphPanel(self)
        self.__qw_mediator.set_graph_panel(graph_panel)
        return graph_panel

    def __new_t_number_ctrl(self):
        t_number_ctrl = wx.SpinCtrl(self, min=2, max=1000, initial=100)
        t_number_ctrl.Bind(wx.EVT_SPINCTRL, self.__on_t_ctrl_change)
        self.__qw_mediator.set_t_number_ctrl(t_number_ctrl)
        return new_titled_view(self, "t steps:", t_number_ctrl)

    def __new_vertices_number_label(self):
        vertices_number_label = wx.StaticText(self, label=TOTAL_VERTICES_NUMBER_LABEL.format(2*100+1))
        self.__qw_mediator.set_vertices_number_label(vertices_number_label)
        return vertices_number_label

    def __new_graph_center_sizer(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.__new_center_selector(), wx.CENTER)
        sizer.AddSpacer(10)
        sizer.Add(self.__new_graph_center_ctrl(), wx.CENTER)
        sizer.Layout()
        return sizer

    def __new_graph_center_ctrl(self):
        graph_center_ctrl = wx.SpinCtrl(self, min=-100, max=100, initial=0)
        graph_center_ctrl.Bind(wx.EVT_SPINCTRL, self.__on_start_ctrl_change)
        self.__qw_mediator.set_graph_center_ctrl(graph_center_ctrl)
        return graph_center_ctrl

    def __new_center_selector(self):
        center_selector = wx.Slider(self, minValue=-100, maxValue=100, value=0, style=wx.SL_HORIZONTAL)
        center_selector.Bind(wx.EVT_SLIDER, self.__on_start_slider_change)
        self.__qw_mediator.set_center_slider(center_selector)
        return new_titled_view(self, "graph starting node ", center_selector)

    def __on_start_slider_change(self, _):
        self.__qw_mediator.change_start_slider()

    def __on_start_ctrl_change(self, _):
        self.__qw_mediator.change_start_ctrl()

    def __on_t_ctrl_change(self, _):
        self.__qw_mediator.steps_changed()

    def __new_simulation_button(self):
        btn = newStandardButton(self, (200, 50), "simulate quantum walk", self.__on_simulate)
        self.__qw_mediator.set_simulation_button(btn)
        return btn

    def __on_simulate(self, _):
        self.__qw_mediator.simulate()

class QuantumWalkDialog(wx.Dialog):

    def __init__(self, parent, quantum_computer):
        x,y = get_screen_middle_point()
        x,y = x - WIDTH/2, y - HEIGHT/2
        wx.Dialog.__init__(self, parent, size=(WIDTH, HEIGHT),  pos=(x,y))
        QuantumWalkScrollPanel(self, quantum_computer)


if __name__ == "__main__":
    app = wx.PySimpleApp()
    win = QuantumWalkDialog(None, None)
    win.ShowModal()
    app.MainLoop()