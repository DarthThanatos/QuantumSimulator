def hadamard_sandwitch(step, from_bit, to_bit):
	assert from_bit < to_bit
	for i in range(from_bit, to_bit + 1):
		quantum_instance.H(step=step, target=i)

quantum_instance.init_register(nqubits=3, value=0)
hadamard_sandwitch(step=0, from_bit=0, to_bit=2)