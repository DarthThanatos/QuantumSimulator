from workspace.composite_gates_scripts.qft import qft

def carry(quantum_instance, step, bit0, bit1, bit2, bit3):
	if not quantum_instance.are_steps_free_at_qubit(step, step+2, bit0):
		return
	quantum_instance.controlledX(step=step, ctrls=[bit1, bit2], target=bit3)
	quantum_instance.controlledX(step=step+1, ctrls=[bit1], target=bit2)
	quantum_instance.controlledX(step=step+2, ctrls=[bit0, bit2], target=bit3)

if __name__=='__main__':
	quantum_instance.init_register(nqubits=4, value=0)
	carry(quantum_instance, step=0, bit0=0, bit1=1, bit2=2, bit3=3)
	carry(quantum_instance, step=0, bit0=3, bit1=2, bit2=1, bit3=0)