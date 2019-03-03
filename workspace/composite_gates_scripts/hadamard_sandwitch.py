def hadamard_sandwitch(quantum_instance, step, from_bit, to_bit):
	assert from_bit < to_bit
	for i in range(from_bit, to_bit + 1):
		quantum_instance.H(step=step, target=i)

if __name__ == '__main__':
	quantum_instance.init_register(nqubits=3, value=0)
	hadamard_sandwitch(quantum_instance, step=0, from_bit=0, to_bit=2)