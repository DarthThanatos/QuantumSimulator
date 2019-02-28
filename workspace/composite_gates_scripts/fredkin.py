def fredkin_gate(step, ctrl, bit0, bit1):
	quantum_instance.controlledX(step=step, ctrls=[ctrl], target=bit1)
	quantum_instance.controlledX(step=step+1, ctrls=[bit0], target=bit1)
	quantum_instance.controlledX(step=step+2, ctrls=[bit1], target=bit0)
	quantum_instance.controlledX(step=step+3, ctrls=[ctrl], target=bit1)
	quantum_instance.controlledX(step=step+4, ctrls=[ctrl], target=bit0)
	quantum_instance.controlledX(step=step+5, ctrls=[bit1], target=bit0)
	quantum_instance.controlledX(step=step+6, ctrls=[bit0], target=bit1)

quantum_instance.init_register(nqubits=3, value=0)
fredkin_gate(step=0, ctrl=0, bit0=1, bit1=2)
fredkin_gate(step=9, ctrl=2, bit0=1, bit1=0)