def sum(quantum_instance, step, bit0, bit1, bit2):
	quantum_instance.controlledX(step=step, ctrls=[bit0], target=bit2)
	quantum_instance.controlledX(step=step+1, ctrls=[bit1], target=bit2)

if __name__ == '__main__':
	quantum_instance.init_register(nqubits=4, value=0)
	sum(quantum_instance, step=0, bit0=0, bit1=1, bit2=3)
	sum(quantum_instance, step=4, bit0=3, bit1=1, bit2=0)