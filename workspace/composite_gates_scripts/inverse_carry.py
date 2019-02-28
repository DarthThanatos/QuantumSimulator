def inverse_carry(step, bit0, bit1, bit2, bit3):
	quantum_instance.controlledX(step=step, ctrls=[bit0, bit2], target=bit3)
	quantum_instance.controlledX(step=step+1, ctrls=[bit1], target=bit2)
	quantum_instance.controlledX(step=step+2, ctrls=[bit1, bit2], target=bit3)

quantum_instance.init_register(nqubits=4, value=0)
inverse_carry(step=0, bit0=0, bit1=1, bit2=2, bit3=3)
inverse_carry(step=4, bit0=3, bit1=2, bit2=1, bit3=0)