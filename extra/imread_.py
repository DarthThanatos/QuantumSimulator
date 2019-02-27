import matplotlib.pyplot as plt
import numpy as np

a = plt.imread("../images/argand.png")
print(a)
plt.imshow(a)
x = 1 + 1j
plt.plot([0, 200 * x.real], [0, 200 * x.imag])
ax = plt.gca()
plt.show()