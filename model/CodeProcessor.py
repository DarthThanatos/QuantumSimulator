import sys
from io import StringIO

import re

from model.Circuit import Circuit
from model.QuantumInstance import QuantumInstance
from model.constants import QUANTUM_INSTANCE
import traceback


class CodeProcessor:

    def __init__(self, quantum_computer):
        self.__quantum_computer = quantum_computer
        self.__initial_globals = globals()

    def __create_local_scope_code(self, original_code):
        lines = original_code.split("\n")
        res = "def __temp_scope():\n"
        for line in lines:
            res += '\t' + line + "\n"
        return res + "__temp_scope()\n" \
                     "del globals()[\'__temp_scope\']"

    def __remove_workspace_imports_re(self, code):
        one = re.findall(r'import ((\w+\.?)+)', code)
        two = re.findall(r'from ((\w+\.?)+) import \w', code)
        for imp, _ in one + two:
            try:
                if imp.startswith("workspace"):
                    del sys.modules[imp]
            except Exception:
                pass

    def __remove_workspace_imports(self, old_sys_modules):
        values = [k for k in set(sys.modules) - set(old_sys_modules)]
        for imp in values:
            try:
                if imp.startswith("workspace"):
                    del sys.modules[imp]
            except Exception:
                pass

    def run_code(self, code_string, file_name, for_simulation):
        # create file-like string to capture output
        codeOut = StringIO()
        codeErr = StringIO()
        circuit = Circuit(self.__quantum_computer, nqbits=1)
        quantum_instance = QuantumInstance(for_simulation, circuit)
        safe_list = ['quantum_instance']
        current_locals = locals() # must be here, not in generator function, as locals are different there
        safe_dict = dict([(k, current_locals.get(k, None)) for k in safe_list])
        safe_dict['__name__'] = '__main__'
        code_string = self.__create_local_scope_code(code_string)
        # capture output and errors
        sys.stdout = codeOut
        sys.stderr = codeErr
        old_sys_modules = dict(sys.modules)
        try:
            code_object = compile(code_string, file_name, 'exec')
            exec(code_object, safe_dict)
            self.__remove_workspace_imports(old_sys_modules)
        except Exception as e:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            self.__remove_workspace_imports(old_sys_modules)
            traceback.print_exc()  # error message is printed to stdout, which at this moment is captured by codeOut
            raise
        # restore stdout and stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        out = codeOut.getvalue()
        out += codeErr.getvalue()
        codeOut.close()
        codeErr.close()
        return out, circuit

    def generate_current_circuit_code(self, circuit, file_name):
        generated = "import pydoc\n\npydoc.help(quantum_instance)\n"
        generated += self.__generate_init_code(circuit)
        generated += self.__generate_non_measure_code(circuit)
        generated += self.__generate_multi_gates_code(circuit)
        generated += self.__generate_measure_gates_code(circuit)
        with open(file_name, 'w+') as f:
            f.write(generated)

    def __generate_init_code(self, circuit):
        code = "{}.init_register(nqubits={}, value={})\n".format(QUANTUM_INSTANCE, circuit.circuit_qubits_number(), circuit.initial_int_value())
        return code

    def __generate_single_gates_code(self, circuit, single_gates):
        code = ""
        for j in single_gates:
            for _, gate in single_gates[j].items():
                code += gate.generate_single_gate_code(j)
        return code

    def __generate_non_measure_code(self, circuit):
        single_gates = circuit.simulation_single_gates_dict()
        return self.__generate_single_gates_code(circuit, single_gates)

    def __generate_multi_gates_code(self, circuit):
        code = ""
        multi_gates = circuit.simulation_multi_gates_dict()
        for j in multi_gates:
            for ctrls, gate in multi_gates[j].items():
                code += gate.generate_controlled_gate_code(j, list(ctrls))
        return code

    def __generate_measure_gates_code(self, circuit):
        measure_gates = circuit.simulation_measure_gates_dict()
        return self.__generate_single_gates_code(circuit, measure_gates)