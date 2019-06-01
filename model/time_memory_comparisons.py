import sys
import os, shutil
import time
from random import shuffle
from multiprocessing import Process
import psutil
from qutip import *
from memory_profiler import memory_usage
import numpy as np
import matplotlib.pyplot as plt
import traceback 
import pandas as pd 
import seaborn as sns
from matplotlib.dates import date2num
import matplotlib.ticker as ticker
import datetime
import re 

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
    for nqubits in range(4, 15):
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
    methods = [ applyOpCustomTensor, applyOpHash, applyOpMatrixMul ] # [applyOpCustomTensor, applyOpHash, applyOpHybrid, applyOpMatrixMul]
    gate_creator = GateCreator()
    gate = gate_creator.createGate("X", 0)
    for reg_alpha in [.5]: # [.1, .2, .5, .6, .7, .9]:
        for nqubits in range(13, 15):
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
    kwargs = {"options": Options(store_states=True, average_states=True, nsteps=100000000)}
    format = "{} {} {} {} {}\n"
    debug_args = (steps, nqubits, measurements_ops_number)
    file_name = method.__name__
    test_framework(method, args, format, debug_args, file_name, kwargs)


def decoherence_loop(method):
    for steps in [10, 20, 30, 40, 50, 70, 90, 100]:
        for nqubits in range(8):
            for measurements_ops_number in range(min(nqubits, 5)):
                run_in_process(decoherence, (method, steps, nqubits, measurements_ops_number))


def decoherence_scalability_main():
    decoherence_loop(mesolve)
    decoherence_loop(mcsolve)


#==============================================
# plotting 


def create_dict(file_pattern, update_dict_fun):
    res = {}
    for root, dirs, files in os.walk("results", topdown = False):
        for file_name in files:
            if not file_pattern(file_name): 
                continue
            file_name = file_name.replace(".txt", "")
            with open("results/{}.txt".format(file_name), "r") as f:
                lines = f.read().split("\n")
                for line in lines:
                    try:
                        update_dict_fun(res, file_name, line)
                    except Exception:
                        pass
    return res


def plot_df(collection, x_title, hue_title, col_title, dir_name, file_name, title, lineplot, scale, palette=None, fig_size=None):
    plt.clf()
    if fig_size is not None:
        plt.figure(figsize=fig_size)
    df = pd.DataFrame(collection, columns=[x_title, hue_title, col_title])  
    if lineplot:
        plt.yscale(scale)
        sns.lineplot(x=x_title, hue=hue_title, y=col_title, data=df, legend="full", palette=palette)
    else:
        plt.yscale(scale)
        sns.barplot(x=x_title, hue=hue_title, y=col_title, data=df)
    plt.title(title)
    plt.savefig("results/imgs/{}/{}.png".format(dir_name, file_name))  


def plot_time_memory(d, x_name, hue_name, dir_name, get_data_description, get_file_prefix, get_title, palette, scales, methods_filter=None, fig_size=None):
    for plot_key in d:
        method_dict = d[plot_key]
        if methods_filter is not None:
            method_dict_filtered_keys = methods_filter(method_dict)
        else:
            method_dict_filtered_keys = method_dict.keys() if type(method_dict) is dict else method_dict
        data, lines = get_data_description(method_dict, method_dict_filtered_keys)
        time_scale, mem_scale = scales
        file_name =  "{}_{}_{}.png".format(get_file_prefix(), "time", plot_key)
        plot_df(lines, x_name, hue_name, "time[s]", dir_name, file_name, get_title(plot_key), True, time_scale, palette, fig_size=None)
        file_name =  "{}_{}_{}.png".format(get_file_prefix(), "mem", plot_key)
        plot_df(data, x_name, hue_name, "memory[MB]", dir_name, file_name, get_title(plot_key), False, mem_scale, fig_size=fig_size)


def plot_hybrid(d):
    palette={0.1:"blue", 0.2:"orange", 0.5:"green",0.6:"brown",0.7:"cyan",0.9:"black"}

    def methods_filter(d):
        return list(filter(lambda x: x.startswith(applyOpHybrid.__name__), d.keys()))

    def get_data_description(d, filtered_keys):
        data = []
        lines = []
        for method_name in filtered_keys:
            hyb_alpha = float(re.match(r'applyOpHybrid_(\d\.\d)', method_name)[1])
            nqs, ts, mems = d[method_name]
            for n, t, m in zip(nqs, ts, mems):
                data.append((n, hyb_alpha, m))
                lines.append((n, hyb_alpha, t))
        return data, lines

    def get_file_prefix():
        return "hybrid_comparison"

    def get_title(alpha):
        return "hybrid comparison for sparsity = {}".format(alpha)

    scales = ("log", "linear")
    dir_name = "hybrid_comparison"
    plot_time_memory(d, "nqubits", "alpha", dir_name, get_data_description, get_file_prefix, get_title, palette, scales, methods_filter)


def create_alphas_dict():

    def file_pattern(file_name):
        return file_name.startswith("apply")

    def update_dict_fun(d, file_name, line):
        if file_name.startswith(applyOpHybrid.__name__):
            alpha, hybrid_alpha, nqubits, t, mem = line.split(" ")
        else:
            alpha, nqubits, t, mem = line.split(" ")
        if alpha not in d:
            d[alpha] = {}
        if file_name not in d[alpha]:
            d[alpha][file_name] = [], [], []
        d[alpha][file_name][0].append(int(nqubits))
        d[alpha][file_name][1].append(float(t))
        d[alpha][file_name][2].append(float(mem))

    return create_dict(file_pattern, update_dict_fun)


def create_hybrid_search_dict():

    def file_pattern(file_name):
        return file_name.startswith("hybrid_alpha")

    def update_dict_fun(d, file_name, line):
        alpha, nqubits, t, mem = line.split(" ")
        if alpha not in d:
            d[alpha] = [], [], []
        d[alpha][0].append(int(nqubits))
        d[alpha][1].append(float(t))
        d[alpha][2].append(float(mem))

    return create_dict(file_pattern, update_dict_fun)


def create_decoherence_dict(method_name):

    def file_pattern(file_name):
        return file_name.startswith(method_name)

    def update_dict_fun(d, file_name, line):
        steps, nqubits, c_ops_num, t, mem = line.split(" ")
        if steps != "40":
            return
        if nqubits != "6" and nqubits != "7":
            return 
        if nqubits not in d:
            d[nqubits] = [], [], []
        d[nqubits][0].append(int(c_ops_num))
        d[nqubits][1].append(float(t))
        d[nqubits][2].append(float(mem))

    return create_dict(file_pattern, update_dict_fun)


def create_walk_dict():

    def file_pattern(file_name):
        return file_name.startswith("discrete_walk")

    def update_dict_fun(d, file_name, line):
        nnodes, t, mem = line.split(" ")
        if "walk" not in d:
            d["walk"] = [], [], []
        d["walk"][0].append(int(nnodes))
        d["walk"][1].append(float(t))
        d["walk"][2].append(float(mem))

    return create_dict(file_pattern, update_dict_fun)


def plot_xsolve(d, method_name):

    palette={method_name:"orange"}

    def get_data_description(cs_ts_ms, filtered_keys):
        data = []
        lines = []
        c_ops_num, ts, mems = cs_ts_ms
        for c, t, m in zip(c_ops_num, ts, mems):
            data.append((c, method_name, m))
            lines.append((c, method_name, t))
        return data, lines

    def get_file_prefix():
        return method_name

    def get_title(nqubits):
        return "scalability of {} continuous evolution method for {} qubits and 40 time resolution".format(method_name, nqubits)

    scales = ("log", "log")
    dir_name = "decoherence"
    plot_time_memory(d, "c_ops number", "name", dir_name, get_data_description, get_file_prefix, get_title, palette, scales)


def plot_xsolve_test(method_name):
    d = create_decoherence_dict(method_name)
    plot_xsolve(d, method_name)


def plot_walk(d):
    palette={"walk":"red"}

    def get_data_description(ns_ts_ms, filtered_keys):
        data = []
        lines = []
        nqs, ts, mems = ns_ts_ms
        for n, t, m in zip(nqs, ts, mems):
            data.append((n, "walk", m))
            lines.append((n, "walk", t))
        return data, lines

    def get_file_prefix():
        return "discrete_walk"

    def get_title(_):
        return "discrete quantum walk along a path"

    scales = ("log", "linear")
    dir_name = "walk"
    plot_time_memory(d, "evolution steps", "name", dir_name, get_data_description, get_file_prefix, get_title, palette, scales, fig_size=(11., 5.))


def plot_hybrid_search(d):
    palette={"search":"blue"}

    def get_data_description(ns_ts_ms, filtered_keys):
        data = []
        lines = []
        nqs, ts, mems = ns_ts_ms
        for n, t, m in zip(nqs, ts, mems):
            data.append((n, "search", m))
            lines.append((n, "search", t))
        return data, lines

    def get_file_prefix():
        return "hybrid_search"

    def get_title(alpha):
        return "hybrid search for switching alpha = {}".format(alpha)

    scales = ("log", "linear")
    dir_name = "hybrid_search"
    plot_time_memory(d, "nqubits", "name", dir_name, get_data_description, get_file_prefix, get_title, palette, scales)


def plot_methods(d):
    palette={"applyOpHash":"blue", "applyOpMatrixMul":"orange", "applyOpCustomTensor":"green", "applyOpHybrid_0.5":"brown"}

    def methods_filter(d):
        def matches(x):
            return x.startswith("applyOpHybrid_0.5") or\
                x.startswith(applyOpHash.__name__) or\
                x.startswith(applyOpCustomTensor.__name__) or\
                x.startswith(applyOpMatrixMul.__name__)
        return list(filter(lambda x: matches(x), d.keys()))

    def get_data_description(d, filtered_keys):
        data = []
        lines = []
        for method_name in filtered_keys:
            nqs, ts, mems = d[method_name]
            for n, t, m in zip(nqs, ts, mems):
                data.append((n, method_name, m))
                lines.append((n, method_name, t))
        return data, lines

    def get_file_prefix():
        return "method_comparison"

    def get_title(alpha):
        return "methods comparison for sparsity = {}".format(alpha)

    dir_name = "methods_comparison"
    scales = ("log", "log")
    plot_time_memory(d, "nqubits", "name", dir_name, get_data_description, get_file_prefix, get_title, palette, scales, methods_filter)


def plot_method_tests():
    alphas_dict = create_alphas_dict()
    plot_hybrid(alphas_dict)
    plot_methods(alphas_dict)


def plot_hybrid_search_test():
    d = create_hybrid_search_dict()
    plot_hybrid_search(d)


def plot_walk_test():
    d = create_walk_dict()
    plot_walk(d)


def seaborn_test():
    l = [(2202423.0, 'y', 5), (2202423.0, 'z',  9), (2202422.0, 'y', 4), (2202422.0, 'z',  6), (2202421.0, 'y', 4), (2202421.0, 'z',  9)]
    df = pd.DataFrame(l, columns=["time", "kind", "data"])
    plt.figure(figsize=(10, 6))
    sns.barplot(x="time", hue="kind", y="data", data=df)
    plt.show()


#=====================================================
# main

def gather_results():
    methods_comparison_()
    methods_comparison()
    hybrid_alpha_search_main()
    discrete_walk_scalability_main()
    decoherence_scalability_main()


def prepare_imgs_folder():
    folder = 'results/imgs'
    access_rights = 0o777
    dirs = ["decoherence", "hybrid_comparison", "hybrid_search", "walk", "methods_comparison"]
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): 
                shutil.rmtree(file_path)
                print("deleted directory {}".format(file_path))
        except Exception as e:
            print(e)
    for imgs_dir in dirs:
        try:  
            full_dir_path = os.path.join(folder, imgs_dir)
            os.mkdir(full_dir_path, access_rights)
        except OSError:  
            print ("Creation of the directory %s failed" % full_dir_path)
        else:  
            print ("Successfully created the directory %s" % full_dir_path)

def plot_all():
    prepare_imgs_folder()
    plot_method_tests()
    plot_hybrid_search_test()
    plot_walk_test()
    plot_xsolve_test("mcsolve")
    plot_xsolve_test("mesolve")

if __name__ == "__main__":
    plot_all()