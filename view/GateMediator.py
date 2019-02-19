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

    def gateSelected(self, gate):
        self.__circuit_view.stimula(True, gate)

    def gateUnselected(self):
        self.__frame.SetCursor(wx.NullCursor)
        self.__circuit_view.stimula(False)

    def register_changed(self):
        self.__circuit_inspector.reset_view()
        self.__circuit_view.resetView()
        self.__bloch_canvas.reset_view()

    def run_in_console(self, quantum_computer):
        code = self.__code_notebook.get_current_code_string()
        file_name = self.__code_notebook.get_current_file_name()
        out = quantum_computer.run_code(code, file_name, for_simulation=True)
        self.__notepad.update_console(out)
        self.__history_panel.reset_view()

    def build_circuit(self, quantum_computer):
        code = self.__code_notebook.get_current_code_string()
        file_name = self.__code_notebook.get_current_file_name()
        quantum_computer.run_code(code, file_name, for_simulation=False)
        self.__circuit_view.resetView()
        self.__circuit_inspector.reset_view()
        self.__bloch_canvas.reset_view()
        self.__history_panel.reset_view()
        self.__editor.switch_to_circuit_view()

    def history_changed(self):
        self.__history_panel.reset_view()
        self.__circuit_view.resetView()
        self.__circuit_inspector.reset_view()
        self.__bloch_canvas.reset_view()

    def generate_code(self, quantum_computer, file_name):
        quantum_computer.generate_current_circuit_code(file_name)
        self.__code_notebook.newTabIfNotExists(file_name)
        self.__editor.switch_to_notepad_view()