from numpy import array, log2, append
from qutip import Qobj, tensor


class CustomTensor:
    def __init__(self, gates, permutation=None):
        self.__gates = gates
        self.__permutation = permutation
        self.__max_gates_row_indices = list(map(lambda x: x.shape[0], self.__gates))
        self.__subindices = [0 for _ in range(len(self.__gates))]
        self.__enumerated_ops = list(enumerate(self.__gates))

    def __fill_subindices_array(self, index):
        for i in range(len(self.__subindices)-1, -1, -1):
            self.__subindices[i] = index % self.__max_gates_row_indices[i]
            index = int(index / self.__max_gates_row_indices[i])

    def createColumnFunc(self, psi):
        columnMapFun = lambda i_op: Qobj(i_op[1].full()[self.__subindices[i_op[0]]], shape=(i_op[1].shape[1], 1))
        return Qobj(tensor(list(map(columnMapFun, self.__enumerated_ops))), dims=psi.dims)

    def transform(self, psi):
        res = array([])
        for index in range(psi.shape[0]):
            self.__fill_subindices_array(index)
            opColumn = self.createColumnFunc(psi)
            elem = (opColumn.dag() * input).data[0,0]
            res = append(res, array(elem))
            del opColumn
        res = Qobj(res, dims=psi.dims)
        return res
