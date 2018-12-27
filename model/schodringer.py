from qutip import *
from matplotlib.pyplot import  *
from threading import Thread
import time
from math import cos, sin, radians

H = 2 * np.pi * .1 * sigmax()
psi0 = ket("0")
times = np.linspace(0., 10., 100)
res = mesolve(H, psi0, times, [], [sigmaz(), sigmay()])

fig, ax = subplots()
ax.plot(res.times, res.expect[0])
ax.plot(res.times, res.expect[1])
ax.set_xlabel('Time')
ax.set_ylabel('Expectation values')
ax.legend(["Sigma-Z", "Sigma-Y"])

def evolve():
    H = 2 * np.pi * sigmay()
    psi0 = hadamard_transform() * ket("1")
    res = mesolve(H, psi0, times, [], [])
    i = 0
    xs = []
    ys = []
    zs = []
    while True:
        if i == res.states.__len__():
            i = 0
            xs  = []
            ys = []
            zs = []
        st = res.states[i]
        try:
            xs.append(float((st.dag() * sigmax() * st).data[0,0]))
            ys.append(float((st.dag() * sigmay() * st).data[0,0]))
            zs.append(float((st.dag() * sigmaz() * st).data[0,0]))
            b.clear()
            b.add_states(res.states[i])
            b.add_points([xs, ys, zs])
            b.make_sphere()
            b.fig.canvas.draw()
        except Exception as e:
            print(e)
        i+=1
        time.sleep(.05)

def rotationGate(coin_angle):
    return qutip.Qobj([[cos(radians(coin_angle)), sin(radians(coin_angle))],  # one paramter SU(2) matrix
                        [sin(radians(coin_angle)), -cos(radians(coin_angle))]], dims=[[2],[2]])

def standaloneBloch():
    b = Bloch()
    psi = rotationGate(30) * hadamard_transform() * ket("1")
    b.add_states(psi)
    b.show()

standaloneBloch()

t = Thread(target=evolve)
t.setDaemon(True)
t.start()


b = Bloch()
b.show()

