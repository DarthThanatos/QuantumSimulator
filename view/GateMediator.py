import wx


class GateMediator:

    def __init__(self):
        self.__editor = None
        self.__circuit_inspector = None
        self.__circuit_view = None
        self.__frame = None
        self.__bloch_canvas = None
        self.__code_notebook = None
        self.__notepad = None
        self.__history_panel = None
        self.__tree = None
        self.__circuit_frame = None
        self.__notebook_frame = None
        self.__schodringer_mediator = None

    def set_notebook_frame(self, notebook_frame):
        self.__notebook_frame = notebook_frame

    def set_circuit_frame(self, circuit_frame):
        self.__circuit_frame = circuit_frame

    def set_tree(self, tree):
        self.__tree = tree

    def set_editor(self, editor):
        self.__editor = editor

    def set_history_panel(self, history_panel):
        self.__history_panel = history_panel

    def set_notepad(self, notepad):
        self.__notepad = notepad

    def set_code_notebook(self, code_notebook):
        self.__code_notebook = code_notebook

    def set_bloch_canvas(self, bloch_canvas):
        self.__bloch_canvas = bloch_canvas

    def set_circuit_inspector(self, circuit_inspector):
        self.__circuit_inspector = circuit_inspector

    def set_frame(self, frame):
        self.__frame = frame

    def set_circuit_view(self, circuit_view):
        self.__circuit_view = circuit_view

    def set_schodringer_mediator(self, schodringer_mediator):
        self.__schodringer_mediator = schodringer_mediator
        self.__schodringer_mediator.set_gate_mediator(self)

    def gateSelected(self, gate):
        # called when a view representing a gate has been clicked
        self.__circuit_view.stimula(True, gate)

    def gateUnselected(self):
        # called when signalization of a gate selection is no longer valid
        self.__frame.SetCursor(wx.NullCursor)
        self.__circuit_view.stimula(False)

    def register_changed(self):
        # called when qubit is added or removed, a step (or steps) in simulation is(are) performed,
        # or when qubits initial values are swapped
        self.__circuit_inspector.reset_view()
        self.__circuit_view.resetView()
        self.__bloch_canvas.reset_view()
        self.__schodringer_mediator.register_changed()

    def circuit_grid_changed(self):
        # called when a gate is freshly added, completely removed, or an existing gate changed its position
        self.__schodringer_mediator.circuit_grid_changed()

    def run_in_console(self, quantum_computer):
        # called when "run in console" button was clicked
        code = self.__code_notebook.get_current_code_string()
        file_name = self.__code_notebook.get_current_file_name()
        out = quantum_computer.run_code(code, file_name, for_simulation=True)
        self.__notepad.update_console(out)
        self.__history_panel.reset_view()

    def build_circuit_from_code(self, quantum_computer):
        code = self.__code_notebook.get_current_code_string()
        file_name = self.__code_notebook.get_current_file_name()
        quantum_computer.run_code(code, file_name, for_simulation=False)
        self.__circuit_view.resetView()
        self.__circuit_inspector.reset_view()
        self.__bloch_canvas.reset_view()
        self.__history_panel.reset_view()
        self.__editor.switch_to_circuit_view()
        self.__schodringer_mediator.experiment_changed()

    def experiment_changed(self):
        # called when one of the experiment history buttons were clicked
        self.__circuit_view.resetView()
        self.__circuit_inspector.reset_view()
        self.__bloch_canvas.reset_view()
        self.__schodringer_mediator.experiment_changed()

    def generate_code(self, quantum_computer, file_name):
        # called when "generate code" is clicked
        quantum_computer.generate_current_circuit_code(file_name)
        self.__editor.switch_to_notepad_view()
        self.__code_notebook.new_tab_if_not_exists(file_name, retain_content=False)

    def schodringer_mode_changed(self, started):
        # called to lock circuitstd
        self.__circuit_frame.Enable(not started)
        self.__notebook_frame.Enable(not started)

    def window_closing(self):
        # called before a window is legally executed,
        # it lets perform cleanup (thread-related or other) before application exits
        self.__tree.stop_observer()
