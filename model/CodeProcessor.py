import sys
from io import StringIO

class CodeProcessor:

    def __init__(self, quantum_computer):
        self.__quantum_computer = quantum_computer

    def run_code(self, code_string, file_name, for_simulation):
        # create file-like string to capture output
        codeOut = StringIO()
        codeErr = StringIO()
        quantum_instance = self.__quantum_computer.get_quantum_instance(for_simulation)
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
        return out
