from qutip import *
from matplotlib.pyplot import  *
from threading import Thread
import time
from math import cos, sin, radians
import numpy as np

if __name__ == '__main__':
    # H = 2 * np.pi  * sigmax()
    # psi0 = ket("0")
    times = np.linspace(0., 10., 20)
    # res = mcsolve(H, psi0, times, [destroy(2)], [sigmaz(), sigmay()], map_func=serial_map, options=qutip.Options(store_states=True))
    # fig, ax = subplots()
    # ax.plot(res.times, res.expect[0])
    # ax.plot(res.times, res.expect[1])
    # ax.set_xlabel('Time')
    # ax.set_ylabel('Expectation values')
    # ax.legend(["Sigma-Z", "Sigma-Y"])

    def normalize(vec):
        norm = np.sqrt((vec.dag() * vec)[0,0])
        normalized = vec * 1/norm
        return normalized

    def sampleOnSphere():
        vec = Qobj(np.random.randn(2, 1))
        return normalize(vec)

    def hamiltonianMedian(K, H):
        res = H * sampleOnSphere() * 1. / K
        for i in range(K-1):
            res += H * sampleOnSphere() * 1. / K
        return res

    def custom_mcsolve(H, psi0, times):
        res = [psi0]
        prev = psi0
        K = 100
        for j in range(1, times.shape[0]):
            psi_j = normalize(prev - (times[j] - times[j-1]) * hamiltonianMedian(K, H))
            prev = psi_j
            res.append(psi_j)
            print(j)
        return res

    def getEvolution(H, psi0, times):
        res = mcsolve(H, psi0, times, [destroy(2)], [], options=qutip.Options(average_states=True))
        res = res.states

        # res = custom_mcsolve(H, psi0, times)
        return res

    def evolve():
        H = 2 * np.pi * sigmay()
        psi0 = hadamard_transform() * ket("1")
        res = getEvolution(H, psi0, times)
        print(res)
        i = 0
        xs = []
        ys = []
        zs = []
        while True:
            if i == res.__len__():
                i = 0
                xs  = []
                ys = []
                zs = []
            st = res[i]
            print(st)
            try:
                xs.append(float((st.dag() * sigmax() * st).data[0,0]))
                ys.append(float((st.dag() * sigmay() * st).data[0,0]))
                zs.append(float((st.dag() * sigmaz() * st).data[0,0]))
                b.clear()
                b.add_states(res[i])
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

