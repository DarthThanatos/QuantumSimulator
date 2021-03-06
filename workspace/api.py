# please try not to treat this scripting functionality as an opportunity to hack your class host, as it is highly immoral

import pydoc
from workspace.composite_gates_scripts.carry import carry
from workspace.composite_gates_scripts.qft import qft

if __name__ == '__main__':
	
	# quantum_instance is an injected object, that is used as an api fasade, 
	# through which you can communicate with quantum computer simulation via python scripts
	# if you are lost, you can use the statement below to quickly print a cheat sheet with the api
	pydoc.help(quantum_instance) 

	quantum_instance.init_register(nqubits=5, value=1)
	quantum_instance.X(step=2, target=0)
	quantum_instance.Y(step=3, target=0)
	quantum_instance.Z(step=4, target=0)
	quantum_instance.r_x(step=5, target=0, angle="pi/2")
	quantum_instance.r_y(step=6, target=0, angle=1.571)
	quantum_instance.H(step=7, target=0)
	quantum_instance.sqrt_x(step=8, target=0)
	quantum_instance.phase_kick(step=9, target=0, angle=1.571)
	quantum_instance.phase_scale(step=10, target=0, angle=1.571)
	quantum_instance.cphase(step=11, target=0, k=0)
	quantum_instance.inv_cphase(step=12, target=0, k=0)
	quantum_instance.U(step=13, target=0, matrix=[1.00+0.00j, 0.000+0.000j, 0.000+0.000j, 1.000+0.000j])
	quantum_instance.controlledX(step=2, ctrls=[2], target=1)
	quantum_instance.controlledY(step=3, ctrls=[2], target=1)
	quantum_instance.controlledZ(step=4, ctrls=[2], target=1)
	quantum_instance.controlledr_x(step=5, ctrls=[2], target=1, angle=0.524)
	quantum_instance.controlledr_y(step=6, ctrls=[2], target=1, angle=0.524)
	quantum_instance.controlledH(step=7, ctrls=[2], target=1)
	quantum_instance.controlledsqrt_x(step=8, ctrls=[2], target=1)
	quantum_instance.controlledphase_kick(step=9, ctrls=[2], target=1, angle=0.524)
	quantum_instance.controlledphase_scale(step=10, ctrls=[2], target=1, angle=0.524)
	quantum_instance.controlledcphase(step=11, ctrls=[2], target=1, k=1)
	quantum_instance.controlledinv_cphase(step=12, ctrls=[2], target=1, k=1)
	quantum_instance.controlledU(step=13, ctrls=[2], target=1, matrix=[0.00+0.00j, 1.000+0.000j, 1.000+0.000j, 0.000+0.000j])
	quantum_instance.measure(step=14, target=0)
	quantum_instance.measure(step=14, target=1)
	quantum_instance.measure(step=14, target=2)
	quantum_instance.next_step()
	quantum_instance.next_step()
	for i in range(15):
		quantum_instance.X(step=15 + i, target=i%3)
	quantum_instance.next_step()
	quantum_instance.set_hidden_qubits([0, 1, 2])
	quantum_instance.print_register_state(with_hidden=False)
	quantum_instance.next_step()
	quantum_instance.next_step()
	quantum_instance.next_step()
	
	# note that you can use other scipts within your workspace folder.  
	carry(quantum_instance, step=31, bit0=0, bit1=1, bit2=2, bit3=3)
	qft(quantum_instance, 35, 0, 4)

	#quantum_instance.X(step=2, target=0) # raises exception, as this simulation grid slot is filled
	#quantum_instance.set_to(8) # raises exception due to overflow, please do not do that :)