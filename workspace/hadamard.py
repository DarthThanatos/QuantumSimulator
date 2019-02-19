import numpy as np
from numpy import array, sqrt, exp, pi, abs

quantum_instance.hello_world()
quantum_instance.init_register(nqubits=1, register_value=1)
print(quantum_instance)
help(quantum_instance)

sqrt2 = 1./(sqrt(2))
H = array([[sqrt2, sqrt2], [sqrt2, -sqrt2]])
zero = array([1., 0.])
one = array([0., 1.])

print(H @ zero)
print(H @ one)

omega = exp(complex(0,pi/2))
state = sqrt2 * (zero + omega * one)
hs = H @ state
print(hs)
print("{:.2f}".format(abs(one @ hs) ** 2))
print("{:.2f}".format(abs(zero @ hs) ** 2))