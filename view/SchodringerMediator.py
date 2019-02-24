import time
from threading import Thread

import wx
from qutip import sigmax, sigmay, sigmaz

SHOULD_CONTINUE = 0

def evolve(bloch_evolution_sphere, states, sentinel):

        def update_bloch(xs_, ys_, zs_, state):
            bloch_evolution_sphere.clear()
            bloch_evolution_sphere.add_states(state)
            bloch_evolution_sphere.add_points([xs_, ys_, zs_])
            bloch_evolution_sphere.make_sphere()
            bloch_evolution_sphere.fig.canvas.draw()

        i = 0
        xs = []
        ys = []
        zs = []

        while sentinel[SHOULD_CONTINUE]:
            if i == len(states):
                i = 0
                # xs = []
                # ys = []
                # zs = []
            # st = states[i]
            try:
                pass
                # xs.append(float((st.dag() * sigmax() * st).data[0,0]))
                # ys.append(float((st.dag() * sigmay() * st).data[0,0]))
                # zs.append(float((st.dag() * sigmaz() * st).data[0,0]))
                # wx.CallAfter(update_bloch, xs, ys, zs, states[i])
            except Exception as e:
                print(e)
            i+=1
            time.sleep(.05)
        print("out")

class SchodringerMediator:

    def __init__(self, quantum_computer):
        self.__quantum_computer = quantum_computer
        self.__steps_ctrl = None
        self.__schodringer_panel = None
        self.__x_checkbox = None
        self.__y_checkbox = None
        self.__z_checkbox = None
        self.__destroy_checkbox = None
        self.__simulation_button = None
        self.__method_choice = None
        self.__coefficient_input = None
        self.__matrix_panel = None
        self.__bloch_evolution = None
        self.__graph_panel = None
        self.__psi_panel = None
        self.__simulation_on = False
        self.__schodringer_experiment = None
        self.__evolution_thread = None
        self.__sentinel = {SHOULD_CONTINUE: True}

    def set_steps_ctrl(self, steps_ctrl):
        self.__steps_ctrl = steps_ctrl

    def set_destroy_checkbox(self, destroy):
        self.__destroy_checkbox = destroy

    def set_psi_panel(self, psi_panel):
        self.__psi_panel = psi_panel

    def set_schodringer_panel(self, schodringer_panel):
        self.__schodringer_panel = schodringer_panel

    def set_x_checkbox(self, checkbox):
        self.__x_checkbox = checkbox

    def set_y_checkbox(self, checkbox):
        self.__y_checkbox = checkbox

    def set_z_checkbox(self, checkbox):
        self.__z_checkbox = checkbox

    def set_simulation_button(self, btn):
        self.__simulation_button = btn

    def set_metod_choice(self, method_choice):
        self.__method_choice = method_choice

    def set_coefficient_input(self, coefficient_input):
        self.__coefficient_input = coefficient_input

    def set_matrix_panel(self, matrix_panel):
        self.__matrix_panel = matrix_panel

    def set_bloch_evolution(self, bloch_evolution):
        self.__bloch_evolution = bloch_evolution

    def set_graph_panel(self, graph_panel):
        self.__graph_panel = graph_panel

    def coefficient_changed(self):
        self.__visualize_hamiltonian()

    def change_simulation_mode(self):
        self.__simulation_on = not self.__simulation_on
        if self.__simulation_on:
            self.__start_simul()
        else:
            self.__end_simul()

    def __start_simul(self):
        self.__bulk_enable(enabled=False)
        self.__simulation_button.SetLabel("Stop Simulation")
        self.__sentinel[SHOULD_CONTINUE] = True
        states, expectations = self.__get_solution()
        self.__evolution_thread = Thread(target=evolve,  args=(self.__bloch_evolution, [], self.__sentinel))
        self.__evolution_thread.start()

    def __get_solution(self):
        method = self.__method_choice.GetString(self.__method_choice.GetSelection())
        tunneling_coef = self.__coefficient_input.get_coefficient()
        steps = self.__steps_ctrl.GetValue()
        for_x = self.__x_checkbox.IsChecked()
        for_y = self.__y_checkbox.IsChecked()
        for_z = self.__z_checkbox.IsChecked()
        destroy = self.__destroy_checkbox.IsChecked()
        return self.__schodringer_experiment.solve(method, tunneling_coef, steps, for_x, for_y, for_z, destroy)

    def __end_simul(self):
        self.__bulk_enable(enabled=True)
        self.__simulation_button.SetLabel("Start Simulation")
        self.__sentinel[SHOULD_CONTINUE] = False
        self.__evolution_thread.join()

    def __bulk_enable(self, enabled):
        self.__x_checkbox.Enable(enabled)
        self.__y_checkbox.Enable(enabled)
        self.__z_checkbox.Enable(enabled)
        self.__steps_ctrl.Enable(enabled)
        self.__method_choice.Enable(enabled)
        self.__destroy_checkbox.Enable(enabled)
        self.__coefficient_input.Enable(enabled)

    def experiment_changed(self):
        self.__reset_state()

    def register_changed(self):
        self.__reset_state()

    def __visualize_hamiltonian(self):
        coefficient = self.__coefficient_input.get_coefficient()
        h = self.__schodringer_experiment.get_hamiltonian(coefficient)
        self.__matrix_panel.change_matrix_value(h.full())

    def __reset_state(self):
        should_show = self.__quantum_computer.circuit_qubits_number() == 1
        self.__schodringer_panel.reset_view(should_show)
        if should_show:
            self.__schodringer_experiment = \
                self.__quantum_computer.get_current_schodringer_experiment()
            self.__visualize_hamiltonian()
            self.__psi_panel.change_psi_value(self.__schodringer_experiment.get_psi0())