import pydoc

if __name__ == '__main__':
	pydoc.help(quantum_instance)
	quantum_instance.init_register(nqubits=1, value=0)
	quantum_instance.H(step=3, target=0)
	quantum_instance.r_y(step=4, target=0, angle=0.449)
