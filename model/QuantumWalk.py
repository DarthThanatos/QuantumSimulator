from qutip import *
import numpy as np
from math import *

psip = (basis(2, 0) + basis(2, 1) * 1j).unit()
psim = (basis(2, 0) - basis(2, 1) * 1j).unit()
ket0 = ket("0")
ket1 = ket("1")


class QuantumWalk:
    def __measurement(self, t, Psi, z):
        sites = 2 * t + 1
        prob = []
        for i in range(0, sites, z):
            M_p = basis(sites, i) * basis(sites, i).dag()
            Measure = tensor(qeye(2), M_p)
            p = abs((Psi * Measure).tr())
            prob.append(p)
        return prob

    def __coin(self, coin_angle):
        C_hat = qutip.Qobj([[cos(radians(coin_angle)), sin(radians(coin_angle))],
                            [sin(radians(coin_angle)), -cos(radians(coin_angle))]])
        return C_hat

    def __shift(self, t):
        sites = 2 * t + 1
        shift_l = qutip.Qobj(np.roll(np.eye(sites), 1, axis=0))
        shift_r = qutip.Qobj(np.roll(np.eye(sites), -1, axis=0))
        S_hat = tensor(ket0 * ket0.dag(), shift_l) + tensor(ket1 * ket1.dag(), shift_r)
        return S_hat

    def __walk(self, t, center, coin_angle):
        sites = 2 * t + 1
        C_hat = self.__coin(coin_angle)
        S_hat = self.__shift(t)
        U_hat = S_hat * (tensor(C_hat, qeye(sites)))
        return U_hat

    def __qwalk_gen(self, t, center, qubit_state, coin_angle):
        sites = 2 * t + 1
        Position_state = basis(sites, center)
        Psi = ket2dm(tensor(qubit_state, Position_state))
        U_hat = self.__walk(t, center, coin_angle)
        for i in range(t):
            Psi = U_hat * Psi * U_hat.dag()
        return Psi

    def simulate(self, t, center):
        # assumes that center is in range (-t,t)
        center += t
        Psi_t = self.__qwalk_gen(t, center, psip, 45)
        P_p = self.__measurement(t, Psi_t, 2)
        return P_p
