import numpy as np
from workspace.composite_gates_scripts.hadamard_sandwitch import hadamard_sandwitch

def init(quantum_instance, nqubits):
	hadamard_sandwitch(quantum_instance, 0, 0, nqubits-1)

def oracle_f0(quantum_instance, step):
	xs_sandwitch(quantum_instance, step, 0, 1)
	quantum_instance.controlledX(step=step+1, ctrls=[0,1], target=2)
	xs_sandwitch(quantum_instance, step + 2, 0, 1)

def oracle_f1(quantum_instance, step):
	quantum_instance.X(step, 0)
	quantum_instance.controlledX(step=step+1, ctrls=[0,1], target=2)
	quantum_instance.X(step+2, 0)

def oracle_f2(quantum_instance, step):
	quantum_instance.X(step, 1)
	quantum_instance.controlledX(step=step+1, ctrls=[0,1], target=2)
	quantum_instance.X(step+2, 1)

def oracle_f3(quantum_instance, step):
	quantum_instance.controlledX(step=step, ctrls=[0,1], target=2)

def xs_sandwitch(quantum_instance, step, from_bit, to_bit):
	for i in range(from_bit, to_bit + 1):
		quantum_instance.X(step=step, target=i)

def inverse(quantum_instance, step, nqubits):
	hadamard_sandwitch(quantum_instance, step, 0, nqubits-2)
	xs_sandwitch(quantum_instance, step+1, 0, nqubits-2)
	quantum_instance.H(step+2, 1)
	quantum_instance.controlledX(step+4, ctrls=[0], target=1)
	quantum_instance.H(step+6, 1)
	xs_sandwitch(quantum_instance, step+7, 0, nqubits-2)
	hadamard_sandwitch(quantum_instance, step+8, 0, nqubits-2)
	return step+9

if __name__ == '__main__':
	quantum_instance.init_register(nqubits=3, value=1)
	init(quantum_instance, 3)
	oracle_f3(quantum_instance, 1)
	inverse(quantum_instance, 4, 3)
	print(quantum_instance.get_measured() >> 1)