def swap_gate(quantum_instance, step, bit0, bit1):
	quantum_instance.controlledX(step=step, ctrls=[bit0], target=bit1)
	quantum_instance.controlledX(step=step+1, ctrls=[bit1], target=bit0)
	quantum_instance.controlledX(step=step+2, ctrls=[bit0], target=bit1)

if __name__ == '__main__':
	quantum_instance.init_register(nqubits=3, value=0)
	swap_gate(quantum_instance, step=0, bit0=0, bit1=1)
	swap_gate(quantum_instance, step=4, bit0=2, bit1=0)