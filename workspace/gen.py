import pydoc
#from workspace.gen1 import hello5

def hello2(quantum_instance):
	quantum_instance.init_register(nqubits=0, value=0)

def hello1(quantum_instance, i = 0):
	if i == 53:
		hello2(quantum_instance)
		return 
	hello1(quantum_instance, i + 1)

def hello(quantum_instance):
	hello1(quantum_instance)

def hello_(quantum_instance, i = 0):
	if i == 100:
		hello(quantum_instance)
		return
	hello_(quantum_instance, i+1)

a = [1, 2, 3]
#1 / 0
#a[4]
pydoc.help(quantum_instance)
hello_(quantum_instance)
quantum_instance.X(step=5, target=0)
quantum_instance.X(step=5, target=1)
