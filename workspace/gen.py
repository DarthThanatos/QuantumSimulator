import pydoc

pydoc.help(quantum_instance)
quantum_instance.init_register(nqubits=16, value=0)
quantum_instance.X(step=299, target=0)
quantum_instance.Y(step=300, target=0)
