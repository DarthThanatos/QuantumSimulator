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

def mc_solve():
    psi_out, expect_out = run()
    expect = [np.mean(np.array([expect_out[nt][op].real
                                for nt in range(ntraj)],
                               dtype=object),
                      axis=0)
              for op in range(e_num)]
    return psi_out, expect

def run():
    # set arguments for input to monte carlo
    map_kwargs = {'progress_bar': TextProgressBar(),
                  'num_cpus': 8}
    seeds = randint(1, 100000000.0 + 1, size=ntraj)
    task_args = (seeds,)
    task_kwargs = {}

    results = parallel_map(_mc_alg_evolve,
                              list(range(ntraj)),
                              task_args, task_kwargs,
                              **map_kwargs)

    expect_out = [None] * ntraj if e_num > 0 else []
    psi_out = []
    for n, result in enumerate(results):
        state_out, expect = result

        if e_num == 0:
            psi_out[n] = state_out

        if e_num > 0:
            expect_out[n] = expect

    psi_out = np.asarray(psi_out, dtype=object)
    return psi_out, expect_out


class Options:

    def __init__(self):
        self.method='adams'
        self.order=12
        self.atol=1e-08,
        self.rtol=1e-06
        self.nsteps=1000
        self.first_step = 0
        self.min_step=0
        self.max_step=0



def _mc_alg_evolve(nt, seeds):
    num_times = len(tlist)
    states_out = np.zeros((num_times), dtype=object)

    temp = sp.csr_matrix(np.reshape(psi0, (psi_0.shape[0], 1)), dtype=complex)
    temp = csr2fast(temp)
    states_out[0] = Qobj(temp, psi_0.dims, psi_0.shape, fast='mc')
    expect_out = []
    for i in range(e_num):
        expect_out.append(np.zeros(num_times, dtype=complex))
        expect_out[i][0] = \
            cy_expect_psi_csr(np.array(e_ops[i].data.data),
                              e_ops[i].data.indices,
                              e_ops[i].data.indptr,
                              psi0,
                              e_ops[i].isherm)
    prng = RandomState(seeds[nt])
    rand_vals = prng.rand(2)
    ODE = ode(cy_ode_rhs)
    ODE.set_f_params(h_.data.data, h_.data.indices, h_.data.indptr)
    ODE._integrator = CustomZvode(
        method=opt.method, order=opt.order, atol=opt.atol,
        rtol=opt.rtol, nsteps=opt.nsteps, first_step=opt.first_step,
        min_step=opt.min_step, max_step=opt.max_step)
    if not len(ODE._y):
        ODE.t = 0.0
        ODE._y = np.array([0.0], complex)
    ODE._integrator.reset(len(ODE._y),  ODE.jac is not None)
    ODE.set_initial_value(psi0, tlist[0])
    for k in range(1, num_times):
        while ODE.t < tlist[k]:
            # integrate up to tlist[k], one step at a time.
            ODE.integrate(tlist[k], step=1)
            if not ODE.successful():
                raise Exception("ZVODE failed!")
            norm2_psi = dznrm2(ODE._y) ** 2
            if norm2_psi <= rand_vals[0] and c_op is not None:
                # collapse has occured
                state = spmv_csr(c_op.data.data,
                                 c_op.data.indices,
                                 c_op.data.indptr, ODE._y)
                state = state / dznrm2(state)
                ODE._y = state
                ODE._integrator.call_args[3] = 1
                rand_vals = prng.rand(2)
        out_psi = ODE._y / dznrm2(ODE._y)
        if e_num == 0:
            out_psi_csr = dense2D_to_fastcsr_cmode(np.reshape(out_psi,
                                                   (out_psi.shape[0], 1)),
                                                   out_psi.shape[0], 1)
            states_out[k] = Qobj(out_psi_csr, psi0.dims, psi0.shape, fast='mc')
        for jj in range(e_num):
            expect_out[jj][k] = cy_expect_psi_csr(
                e_ops[jj].data.data, e_ops[jj].data.indices,
                e_ops[jj].data.indptr, out_psi,
                e_ops[jj].isherm)
    return states_out, expect_out


dznrm2 = get_blas_funcs("znrm2", dtype=np.float64)
tlist = np.linspace(0., 10., 20)
psi_0 = ket("0")
psi0 = psi_0.full().ravel()
e_ops = [sigmaz(), sigmay()]
e_num = len(e_ops)
c_op = destroy(2)
ntraj = 500
h = 2 * np.pi  * sigmax()
h_ = h
h_ -= .5j * c_op.dag() * c_op if c_op is not None else 0
h_ *= -1.j
opt = Options()

if __name__ == '__main__':
    psi, expect = mc_solve()
    print(expect)
    fig, ax = subplots()
    ax.plot(tlist, expect[0])
    ax.plot(tlist, expect[1])
    ax.set_xlabel('Time')
    ax.set_ylabel('Expectation values')
    ax.legend(["Sigma-Z", "Sigma-Y"])
    plt.show()