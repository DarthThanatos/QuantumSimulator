import pydoc

def init_psi(quantum_instance):
	# input psi that is going to be teleported
	quantum_instance.r_x(step=1, target=0, angle=0.524) 
	quantum_instance.r_y(step=1, target=1, angle=0.524) 
	quantum_instance.next_step()
	print("initial psi register")
	quantum_instance.print_register_state()

def to_bell_basis(quantum_instance):
	quantum_instance.H(step=2, target=2)
	quantum_instance.controlledX(step=3, ctrls=[2], target=3)

def phone(quantum_instance):
	quantum_instance.controlledX(step=4, ctrls=[1], target=2)
	quantum_instance.controlledZ(step=5, ctrls=[0], target=2)

def bell_measurement(quantum_instance):
	quantum_instance.controlledX(step=6, ctrls=[2], target=3)
	quantum_instance.H(step=7, target=2)

def dense_coding(quantum_instance):
	to_bell_basis(quantum_instance)
	phone(quantum_instance)
	bell_measurement(quantum_instance)
	quantum_instance.fast_forward()

if __name__=='__main__':
	#pydoc.help(quantum_instance)
	quantum_instance.init_register(nqubits=4, value=0)
	init_psi(quantum_instance)
	dense_coding(quantum_instance)
	print("final psi register")
	quantum_instance.print_register_state()