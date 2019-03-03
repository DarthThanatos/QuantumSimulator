from workspace.composite_gates_scripts.hadamard_sandwitch import hadamard_sandwitch
from math import log2

def bernstein_vazirani(quantum_instance, nqubits, a):
	hadamard_sandwitch(quantum_instance, step=0, from_bit=0, to_bit=nqubits-1) 
	step = 1
	while a > 0:
		if int(a) % 2 == 1:
			ctrl = nqubits - step - 1
			quantum_instance.controlledX(step=step, ctrls=[ctrl], target=nqubits-1)
		step += 1
		a = int(a / 2)
	hadamard_sandwitch(quantum_instance, step=step, from_bit=0, to_bit=nqubits-1) 
		

if __name__ == '__main__':
	nqubits= 6
	quantum_instance.init_register(nqubits=nqubits, value = 1)
	bernstein_vazirani(quantum_instance, nqubits, 25)
	print("a in the black box:", (quantum_instance.get_measured()  >> 1))
	