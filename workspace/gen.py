import pydoc
import importlib
from workspace.composite_gates_scripts.carry import carry


if __name__ == '__main__':
	pydoc.help(quantum_instance)
	quantum_instance.init_register(nqubits=6, value=0)

	carry(quantum_instance, step=0, bit0=0, bit1=1, bit2=2, bit3=3)
	quantum_instance.X(step=299, target=0)
	quantum_instance.Y(step=300, target=0)
