from workspace.composite_gates_scripts.hadamard_sandwitch import hadamard_sandwitch

def bernstein_vazirani(quantum_instance, nqubits, a):
	step = 1
	while a > 0:
		if int(a) % 2 == 1:
			ctrl = nqubits - step - 1
			quantum_instance.controlledX(step=step, ctrls=[ctrl], target=nqubits-1)
		step += 1
		a = int(a / 2)
		

if __name__ == '__main__':
	nqubits= 6
	res = 0
	for i in range(nqubits - 1):
		value = (1 << (i+1))
		quantum_instance.init_register(nqubits=nqubits, value=value)
		bernstein_vazirani(quantum_instance, nqubits, 25)
		measured = quantum_instance.get_measured() & 1
		if measured == 1:
			res |= (1 << i)
	print("a in the black box:", res)