import sys
import os
import time
from random import shuffle
from multiprocessing import Process
import psutil
from qutip import *
from memory_profiler import memory_usage
import numpy as np

cwd = os.getcwd()
dir_name = os.path.basename(cwd)
if dir_name == "model":
    os.chdir("..")
sys.path += [os.getcwd()]

from model.CustomTensor import CustomTensor
from model.QuantumWalk import QuantumWalk
from model.SingleGateTransformation import SingleGateTransformation
from model.gates.GateCreator import GateCreator
from model.Circuit import Circuit
from model.QuantumInstance import QuantumInstance
from model.grover_hybrid import grover_main


def timed(f, *args, **kwargs):
    start = time.time()
    f(*args, **kwargs)
    elapsed = time.time() - start
    return elapsed


def run_in_process(target, args):
    p = Process(target=target, args=args)
    p.start()
    p.join()  # this blocks until the process terminates


def test_framework(method, args, format, debug_args, file_name, kwargs={}):
    process = psutil.Process(os.getpid())
    start_mem = process.memory_info().rss / (2 ** 20) # rss is given in bytes
    t = timed(method, *args, **kwargs)
    mem_usage = max(memory_usage(proc=(method, args, kwargs), max_usage=True)) - start_mem
    current_stats = format.format(*debug_args, t, mem_usage)
    print("pid", os.getpid(), method.__name__, current_stats, end="")
    with open("results/{}.txt".format(file_name), "a+") as f:
        f.write(current_stats)
        f.flush()


#================================================================
# quantum walk

def run_walk(t):
    q = QuantumWalk()
    q.simulate(t, 0)


def discrete_walk_scalability(t):
    args = (t,)
    format = "{} {} {}\n"
    debug_args = (t,)
    file_name = "discrete_walk"
    test_framework(run_walk, args, format, debug_args, file_name)


def discrete_walk_scalability_main():
    for t in [10, 20, 30, 50, 70, 100, 120, 150, 180, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1500]:
        run_in_process(discrete_walk_scalability, (t,))


#================================================================
# hybrid alpha search

def new_quantum_instance(alpha, reg=None):
    circuit = Circuit(quantum_computer=None, nqbits=2, alpha=alpha, initial_reg_psi=reg)
    quantum_instance = QuantumInstance(should_simulate=True, circuit=circuit)
    return quantum_instance


def hybrid_alpha_search(q, nqubits, single_iter):
    grover_main(q, nqubits, single_iter)


def run_hybrid_search(nqubits, alpha):
    q = new_quantum_instance(alpha)
    args = (q, nqubits, True)
    format = "{} {} {} {}\n"
    debug_args = (alpha, nqubits)
    file_name = "hybrid_alpha"
    test_framework(hybrid_alpha_search, args, format, debug_args, file_name)


def hybrid_alpha_search_main():
    alpha = .75
    for nqubits in range(4, 16):
        run_in_process(run_hybrid_search, (nqubits, alpha))


#================================================================
# methods comparison


def applyOpHybrid(op, reg, nqubits, alpha=.75):
    quantum_instance = new_quantum_instance(alpha, reg)
    quantum_instance.init_register(nqubits, 0)
    eval(op.generate_single_gate_code(0))
    quantum_instance.next_step()
    return quantum_instance.current_simulation_psi()


def applyOpMatrixMul(op, reg, nqubits):
    target = op.target()
    transf = tensor([qeye(2)] * target + [op.qutip_object()] + [qeye(2)] * (nqubits - target - 1))
    reg = Qobj(transf.data.toarray() @ reg.data.toarray(), shape=(2**nqubits, 1), dims=[[2]*nqubits, [1]*nqubits])
    return reg


def applyOpCustomTensor(op, reg, nqubits):
    target = op.target()
    op_list = [qeye(2)] * target + [op.qutip_object()] + [qeye(2)] * (nqubits - target - 1)
    transf = CustomTensor(op_list)
    reg = transf.transform(reg)
    return reg


def applyOpHash(op, reg, nqubits):
    tranf = SingleGateTransformation(op, nqubits)
    reg = tranf.transform(reg)
    return reg


def new_reg(nqubits, alpha):
    non_zero_elems = int(alpha * (2 ** nqubits))
    arr = [0 for _ in range(2 ** nqubits)]
    for i in range(non_zero_elems):
        arr[i] = .5
    shuffle(arr)
    arr = [[x] for x in arr]
    reg = Qobj(arr, shape=(2**nqubits, 1), dims=[[2] * nqubits, [1] * nqubits])
    return reg


def run_hybrid_method(reg, gate, nqubits, alpha, hybrid_alpha):
    args = (gate, reg, nqubits, hybrid_alpha)
    format = "{} {} {} {} {}\n"
    debug_args = (alpha, hybrid_alpha, nqubits)
    file_name = "{}_{}".format(applyOpHybrid.__name__, hybrid_alpha)
    test_framework(applyOpHybrid, args, format, debug_args, file_name)


def run_method(method, reg, gate, nqubits, alpha):
    args = (gate, reg, nqubits)
    format = "{} {} {} {}\n"
    debug_args = (alpha, nqubits)
    file_name = method.__name__
    test_framework(method, args, format, debug_args, file_name)


def methods_comparison():
    methods = [applyOpCustomTensor, applyOpHash, applyOpHybrid, applyOpMatrixMul]
    gate_creator = GateCreator()
    gate = gate_creator.createGate("X", 0)
    for reg_alpha in [.1, .2, .5, .6, .7, .9]:
        for nqubits in range(1, 16):
            reg = new_reg(nqubits, reg_alpha)
            for method in methods:
                if method.__name__ == applyOpHybrid.__name__:
                    for hybrid_alpha in [.1, .2, .5, .6, .7, .9]:
                        run_in_process(run_hybrid_method, (reg, gate, nqubits, reg_alpha, hybrid_alpha))
                else:
                    run_in_process(run_method, (method, reg, gate, nqubits, reg_alpha))


def methods_comparison_():
    gate_creator = GateCreator()
    gate = gate_creator.createGate("Z", 0)
    nqubits = 5
    alpha = .3
    reg = new_reg(nqubits, alpha)
    reg4 = applyOpMatrixMul(gate, reg, nqubits)
    reg1 = applyOpHash(gate, reg, nqubits)
    reg2 = applyOpCustomTensor(gate, reg, nqubits)
    reg3 = applyOpHybrid(gate, reg, nqubits)
    assert(reg1 == reg2 == reg3 == reg4)


#================================================================
# decoherence


def decoherence(method, steps, nqubits, measurements_ops_number):
    times = np.linspace(0., 10., steps)
    psi0 = ket("0" * nqubits)
    H = hadamard_transform(nqubits)
    c_ops = [Qobj(destroy(2 ** nqubits, x), dims=[[2]*nqubits, [2]*nqubits]) for x in range(measurements_ops_number)]
    args = (H, psi0, times, c_ops)
    kwargs = {"options": Options(store_states=True, average_states=True)}
    format = "{} {} {} {} {}\n"
    debug_args = (steps, nqubits, measurements_ops_number)
    file_name = method.__name__
    test_framework(method, args, format, debug_args, file_name, kwargs)


def decoherence_loop(method):
    for steps in [10, 20, 30, 40, 50, 70, 90, 100]:
        for nqubits in range(1, 16):
            for measurements_ops_number in range(min(nqubits, 5)):
                run_in_process(decoherence, (method, steps, nqubits, measurements_ops_number))


def decoherence_scalability_main():
    decoherence_loop(mesolve)
    decoherence_loop(mcsolve)


if __name__ == "__main__":
    methods_comparison_()
    methods_comparison()
    hybrid_alpha_search_main()
    discrete_walk_scalability_main()
    decoherence_scalability_main()
