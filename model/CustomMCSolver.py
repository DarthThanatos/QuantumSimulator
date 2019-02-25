from matplotlib.pyplot import subplots
from numpy.random.mtrand import RandomState
from numpy.random import randint
from qutip.cy.spconvert import dense2D_to_fastcsr_cmode
from qutip.cy.spmatfuncs import cy_ode_rhs, cy_expect_psi_csr, spmv_csr
import numpy as np
import scipy.sparse as sp
from qutip import *
from qutip.fastsparse import csr2fast
from qutip.ui import TextProgressBar
from scipy.integrate import ode
from scipy.integrate._ode import zvode
from scipy.linalg import get_blas_funcs
import matplotlib.pyplot as plt


class CustomZvode(zvode):
    def step(self, *args):
        itask = self.call_args[2]
        self.rwork[0] = args[4]
        self.call_args[2] = 5
        r = self.run(*args)
        self.call_args[2] = itask
        return r


class OdeOptions:

    def __init__(self):
        self.method='adams'
        self.order=12
        self.atol=1e-08,
        self.rtol=1e-06
        self.nsteps=1000
        self.first_step = 0
        self.min_step=0
        self.max_step=0


class ExperimentConfig:

    def __init__(self, h, psi0, times, c_op, e_ops):
        self.psi0 = psi0
        self.psi0_vector = psi0.full().ravel()
        self.times = times
        self.num_times = len(times)
        self.c_op = c_op
        self.e_ops = e_ops
        self.e_num = len(e_ops)
        self.h_ = self.__effective_h(h, c_op)
        self.trajectories_number = 500
        self.ode_options = OdeOptions()
        self.seeds = randint(1, 100000000 + 1, size=self.trajectories_number)

    def __effective_h(self, h, c_op):
        h_ = h
        h_ -= .5j * c_op.dag() * c_op if c_op is not None else 0
        h_ *= -1.j
        return h_


def mc_solve(h, psi0, times, c_op, e_ops, progress_bar, map_func=parallel_map):
    config = ExperimentConfig(h, psi0, times, c_op, e_ops)
    psi_out, expect_out = run(config, map_func, progress_bar)
    expect = [np.mean(np.array([expect_out[nt][op].real
                                for nt in range(config.trajectories_number)],
                               dtype=object),
                      axis=0)
              for op in range(config.e_num)]
    return psi_out, expect


def run(config, map_func, progress_bar):
    # set arguments for input to monte carlo
    map_kwargs = { 'progress_bar': progress_bar,
                  'num_cpus': 8}
    task_args = (config,)
    task_kwargs = {}
    results = map_func(_mc_alg_evolve,
                              list(range(config.trajectories_number)),
                              task_args, task_kwargs,
                              **map_kwargs)
    expect_out = [None] * config.trajectories_number if config.e_num > 0 else []
    psi_out = [None] * config.trajectories_number
    for n, result in enumerate(results):
        state_out, expect = result
        psi_out[n] = state_out
        if config.e_num > 0:
            expect_out[n] = expect
    psi_out = np.asarray(psi_out, dtype=object)
    return psi_out, expect_out


def _mc_alg_evolve(nt, config):
    states_out = np.zeros(config.num_times, dtype=object)
    temp = sp.csr_matrix(np.reshape(config.psi0_vector, (config.psi0.shape[0], 1)), dtype=complex)
    temp = csr2fast(temp)
    states_out[0] = Qobj(temp, config.psi0.dims, config.psi0.shape, fast='mc')
    expect_out = []
    for i in range(config.e_num):
        expect_out.append(np.zeros(config.num_times, dtype=complex))
        expect_out[i][0] = \
            cy_expect_psi_csr(np.array(config.e_ops[i].data.data),
                              config.e_ops[i].data.indices,
                              config.e_ops[i].data.indptr,
                              config.psi0_vector,
                              config.e_ops[i].isherm)
    prng = RandomState(config.seeds[nt])
    rand_vals = prng.rand(2)
    ODE = ode(cy_ode_rhs)
    ODE.set_f_params(config.h_.data.data, config.h_.data.indices, config.h_.data.indptr)
    opt = config.ode_options
    ODE._integrator = CustomZvode(
        method=opt.method, order=opt.order, atol=opt.atol,
        rtol=opt.rtol, nsteps=opt.nsteps, first_step=opt.first_step,
        min_step=opt.min_step, max_step=opt.max_step)
    if not len(ODE._y):
        ODE.t = 0.0
        ODE._y = np.array([0.0], complex)
    ODE._integrator.reset(len(ODE._y),  ODE.jac is not None)
    ODE.set_initial_value(config.psi0_vector, config.times[0])
    for k in range(1, config.num_times):
        while ODE.t < config.times[k]:
            # integrate up to tlist[k], one step at a time.
            ODE.integrate(config.times[k], step=1)
            if not ODE.successful():
                raise Exception("ZVODE failed!")
            norm2_psi = dznrm2(ODE._y) ** 2
            if norm2_psi <= rand_vals[0] and config.c_op is not None:
                # collapse has occured
                state = spmv_csr(config.c_op.data.data,
                                 config.c_op.data.indices,
                                 config.c_op.data.indptr, ODE._y)
                state = state / dznrm2(state)
                ODE._y = state
                ODE._integrator.call_args[3] = 1
                rand_vals = prng.rand(2)
        out_psi = ODE._y / dznrm2(ODE._y)
        out_psi_csr = dense2D_to_fastcsr_cmode(np.reshape(out_psi,
                                               (out_psi.shape[0], 1)),
                                               out_psi.shape[0], 1)
        states_out[k] = Qobj(out_psi_csr, config.psi0.dims, config.psi0.shape, fast='mc')
        e_ops = config.e_ops
        for jj in range(config.e_num):
            expect_out[jj][k] = cy_expect_psi_csr(
                e_ops[jj].data.data, e_ops[jj].data.indices,
                e_ops[jj].data.indptr, out_psi,
                e_ops[jj].isherm)
    return states_out, expect_out


dznrm2 = get_blas_funcs("znrm2", dtype=np.float64)

if __name__ == '__main__':
    psi, expect = mc_solve(
        h=2 * np.pi * sigmax(),
        psi0=ket("0"),
        times=np.linspace(0., 10., 20),
        c_op=destroy(2),
        e_ops=[sigmaz(), sigmay()]
    )
    fig, ax = subplots()
    ax.plot(np.linspace(0., 10., 20), expect[0])
    ax.plot(np.linspace(0., 10., 20), expect[1])
    ax.set_xlabel('Time')
    ax.set_ylabel('Expectation values')
    ax.legend(["Sigma-Z", "Sigma-Y"])
    plt.show()


