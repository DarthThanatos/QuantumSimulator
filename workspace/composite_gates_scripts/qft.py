def qft(quantum_instance, step, from_bit_inclusive, to_bit_inclusive):
	assert from_bit_inclusive < to_bit_inclusive
	for k, i in enumerate(range(from_bit_inclusive, to_bit_inclusive + 1)):
		for j in range(from_bit_inclusive, i):
			quantum_instance.controlledcphase(step=step, ctrls=[j], target=i, k=-k)
			step += 1
		quantum_instance.H(step, target=i)
		step += 1

if __name__=='__main__':
	quantum_instance.init_register(nqubits=5, value=0)
	qft(quantum_instance, 0, 0, 4)
		