import numpy as np
from workspace.composite_gates_scripts.hadamard_sandwitch import hadamard_sandwitch
from math import log2

def init(quantum_instance, nqubits):
	hadamard_sandwitch(quantum_instance, 0, 0, nqubits-1)
	quantum_instance.next_step()

def with_negated_zeroes(quantum_instance, step, nqubits, N):
	for i in range(0, int(nqubits - log2(N))-1):
		quantum_instance.X(step, i)
	i =  nqubits - 1 - int(log2(N))
	while N > 0:
		if int(N) % 2 == 0:
			quantum_instance.X(step=step, target=i)
			i -= 1
		N = int(N / 2)
	
def oracle_fN(quantum_instance, step, nqubits, N):
	with_negated_zeroes(quantum_instance, step, nqubits, N)
	quantum_instance.controlledX(step=step+1, ctrls=list(range(0, nqubits-1)), target=nqubits-1)
	with_negated_zeroes(quantum_instance, step+2, nqubits, N)
	return step + 3

def xs_sandwitch(quantum_instance, step, from_bit, to_bit):
	for i in range(from_bit, to_bit + 1):
		quantum_instance.X(step=step, target=i)

def inverse(quantum_instance, step, nqubits):
	hadamard_sandwitch(quantum_instance, step, 0, nqubits-2)
	xs_sandwitch(quantum_instance, step+1, 0, nqubits-2)
	quantum_instance.H(step+2, nqubits-2)
	quantum_instance.controlledX(step+4, ctrls=list(range(0, nqubits-2)), target=nqubits-2)
	quantum_instance.H(step+6, nqubits-2)
	xs_sandwitch(quantum_instance, step+7, 0, nqubits-2)
	hadamard_sandwitch(quantum_instance, step+8, 0, nqubits-2)
	return step+9

def peek_register_value(quantum_instance, log, step, nqubits):
	#quantum_instance.H(step, nqubits-1)
	print("After", log)
	quantum_instance.print_current_psi_without_qubits([nqubits-1])
	#quantum_instance.H(step + 1, nqubits-1)
	#move_n_steps(quantum_instance, 2)
	return step #+2

def move_n_steps(quantum_instance, n):
	for i in range(n):
		quantum_instance.next_step()

if __name__ == '__main__':
	nqubits = 5
	iterations = 3
	quantum_instance.init_register(nqubits=nqubits, value=1)
	init(quantum_instance, nqubits)
	step = 1
	for i in range(iterations):
		step = oracle_fN(quantum_instance, step, nqubits, 5)
		move_n_steps(quantum_instance, 3)
		step = peek_register_value(quantum_instance, "Oracle", step, nqubits)
		step = inverse(quantum_instance, step, nqubits)
		move_n_steps(quantum_instance, 7)
		step = peek_register_value(quantum_instance, "Inverse", step, nqubits)
	print(quantum_instance.get_measured() >> 1)
