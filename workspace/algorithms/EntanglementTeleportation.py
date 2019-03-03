import pydoc

def init_entangled_psi(quantum_instance):
	# input psi, we are going to that is going to be entangled
	quantum_instance.H(step=0, target=0)
	quantum_instance.controlledX(step=1, ctrls=[0], target=1)
	quantum_instance.next_step()
	quantum_instance.next_step()
	print("initial psi register")
	quantum_instance.print_current_psi()

def to_bell_basis(quantum_instance):
	quantum_instance.H(step=3, target=2)
	quantum_instance.controlledX(step=4, ctrls=[2], target=3)

def bell_measurement(quantum_instance):
	quantum_instance.controlledX(step=6, ctrls=[1], target=2)
	quantum_instance.H(step=7, target=1)
	quantum_instance.measure(step=9, target=1)
	quantum_instance.measure(step=9, target=2)	

def phone(quantum_instance):
	quantum_instance.controlledX(step=11, ctrls=[2], target=3)
	quantum_instance.controlledZ(step=12, ctrls=[1], target=3)

def entanglement_teleportation(quantum_instance):
	to_bell_basis(quantum_instance)
	bell_measurement(quantum_instance)
	phone(quantum_instance)
	quantum_instance.fast_forward()

if __name__=='__main__':
	#pydoc.help(quantum_instance)
	quantum_instance.init_register(nqubits=4, value=0)
	init_entangled_psi(quantum_instance)
	entanglement_teleportation(quantum_instance)
	print("final psi register")
	quantum_instance.print_current_psi()