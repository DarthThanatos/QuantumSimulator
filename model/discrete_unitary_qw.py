from qutip import *
import numpy as np
import matplotlib.pyplot as plt
from math import *

ket0 = basis(2,0).unit()
ket1 = basis(2,1).unit()                
psip = (basis(2,0)+basis(2,1)*1j).unit() 
psim = (basis(2,0)-basis(2,1)*1j).unit() 

def measurement(t,Psi,z):
  sites=2*t+1
  print("s", sites)
  prob=[]
  for i in range(0,sites,z):                  
    M_p = basis(sites,i)*basis(sites,i).dag() 
    Measure = tensor(qeye(2),M_p)             
    p = abs((Psi*Measure).tr())               
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
  C_hat = qutip.Qobj([[cos(radians(coin_angle)), sin(radians(coin_angle))],
                      [sin(radians(coin_angle)), -cos(radians(coin_angle))]])
  return C_hat

def shift(t):
  sites = 2*t+1
  shift_l = qutip.Qobj(np.roll(np.eye(sites), 1, axis=0))  
  shift_r = qutip.Qobj(np.roll(np.eye(sites), -1, axis=0)) 
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
  Psi = ket2dm(tensor(qubit_state,Position_state)) 
  U_hat = walk(t,coin_angle)
  for i in range(t):                               
    Psi = U_hat*Psi*U_hat.dag()
  return Psi


if __name__ == "__main__":           
  Psi_t = qwalk_gen(100,psip,45)     
  P_p  = measurement(100,Psi_t,2)    
  plot_pdf(P_p)
