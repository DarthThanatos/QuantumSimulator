import sys
from io import StringIO

from model.Circuit import Circuit
from model.QuantumInstance import QuantumInstance


class CodeProcessor:

    def run_code(self, code_string, file_name, for_simulation):
        # create file-like string to capture output
        codeOut = StringIO()
        codeErr = StringIO()
        circuit = Circuit(1)
        quantum_instance = QuantumInstance(for_simulation, circuit)
        safe_list = ['quantum_instance']
        current_locals = locals() # must be here, not in generator function, as locals are different there
        safe_dict = dict([(k, current_locals.get(k, None)) for k in safe_list])
        # capture output and errors
        sys.stdout = codeOut
        sys.stderr = codeErr
        try:
            code_object = compile(code_string, file_name, 'exec')
            exec(code_object, safe_dict)
        except Exception as e:
            print(e)  # error message is printed to stdout, which at this moment is captured by codeOut
        # restore stdout and stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        out = codeOut.getvalue()
        out += codeErr.getvalue()
        codeOut.close()
        codeErr.close()
        return out, circuit

    def generate_current_circuit_code(self, circuit, file_name):
        generated = "help(quantum_instance)"
        with open(file_name, 'w+') as f:
            f.write(generated)
