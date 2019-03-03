def inverse_qft(quantum_instance, step, from_bit, to_bit):
	assert from_bit < to_bit
	for k, i in enumerate(range(to_bit, from_bit - 1, -1)):
		quantum_instance.H(step, target=i)
		step += 1
		for j in range(i-1,  from_bit-1, -1):
			quantum_instance.controlledinv_cphase(step=step, ctrls=[j], target=i, k=-k)
			step += 1

if __name__ == '__main__':
	quantum_instance.init_register(nqubits=5, value=0)
	inverse_qft(quantum_instance, 0, 0, 4)
		