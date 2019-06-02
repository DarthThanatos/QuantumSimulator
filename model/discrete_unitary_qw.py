from qutip import basis, Qobj, tensor, qeye, ket2dm
import numpy as np
import matplotlib.pyplot as plt
from math import *

ket0 = basis(2,0).unit()
ket1 = basis(2,1).unit()                
psip = (basis(2,0)+basis(2,1)*1j).unit() 
psip = Qobj(np.array([1/sqrt(2) , - 1/sqrt(2) * 1j])).unit()
# we need to start with the H_e space configured to sqrt(a)|e1> + sqrt(1-a)(cos(w) - isin(w))|e2>), for some a in (0,1) and w in (0, 2pi)
# e.g. a = 1/2, w = pi/2

def measurement(t,Psi,z):
  sites=2*t+1
  print("s", sites)
  prob=[]
  for i in range(0,sites,z):                  
    M_p = basis(sites,i)*basis(sites,i).dag() 
    Measure = tensor(qeye(2),M_p)             
    p = (Measure * Psi).tr()               
    prob.append(p)
  return prob

def plot_pdf(P_p):
    lattice_positions = range(int(-len(P_p)/2+1),int(len(P_p)/2+2))
    print(lattice_positions.__len__(), P_p.__len__())
    plt.plot(lattice_positions,P_p)
    plt.xlim([-len(P_p)/2+2,len(P_p)/2+2])
    plt.ylim([min(P_p),max(P_p)+0.01])
    plt.ylabel(r'$Probablity$')
    plt.xlabel(r'$Particle \ position$')
    plt.show()

def coin(coin_angle):
  C_hat = Qobj([[cos(radians(coin_angle)), sin(radians(coin_angle))],
                      [sin(radians(coin_angle)), -cos(radians(coin_angle))]])
  C_hat = Qobj([[1/sqrt(2), 1/sqrt(2)],
                [1/sqrt(2), -1/sqrt(2)]])
  return C_hat

def shift(t):
  sites = 2*t+1
  shift_l = np.roll(np.eye(sites), 1, axis=0)
  # shift_l[0, -1] = 0
  shift_l = Qobj(shift_l)
  shift_r = np.roll(np.eye(sites), -1, axis=0)
  # shift_r[-1, 0] = 0
  shift_r = Qobj(shift_r)
  print(shift_l)
  S_hat = tensor(ket0*ket0.dag(),shift_l) + tensor(ket1*ket1.dag(),shift_r) 
  return S_hat

def walk(t,coin_angle):
  sites = 2*t+1
  C_hat = coin(coin_angle)
  S_hat = shift(t)
  U_hat = S_hat*(tensor(C_hat,qeye(sites))) 
  return U_hat

def qwalk_gen(t,qubit_state,coin_angle):
  sites=2*t+1
  Position_state = basis(sites,t)                  
  # print(tensor(qubit_state,Position_state))
  Psi = ket2dm(tensor(qubit_state,Position_state)) 
  # Psi = tensor(qubit_state,Position_state)
  U_hat = walk(t,coin_angle)
  for i in range(t):                               
    Psi = U_hat * Psi * U_hat.dag() 
    # Psi = U_hat*Psi
  # return ket2dm(Psi)
  return Psi


if __name__ == "__main__":           
  Psi_t = qwalk_gen(100,psip,45)     
  P_p  = measurement(100,Psi_t,2)    
  plot_pdf(P_p)
