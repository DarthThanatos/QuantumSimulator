from qutip import Qobj, tensor, qeye, ket, controlled_gate, sigmax, hadamard_transform
import datetime
from numpy import sqrt, array, append, matrix, log2


def fillIndxs(indxs, q_index, max_op_row_index):
    for i in range(len(indxs) - 1, -1, -1):
        indxs[i] = q_index % max_op_row_index[i]
        q_index = int(q_index / max_op_row_index[i])


def distributePermutationIndxs(ops, permutation):
    # returns {opindex -> list[permutations]}
    res = {}
    i = 0
    for op_index, op in enumerate(ops):
        res.update({op_index: permutation[i: i + len(op.dims[0])]})
        i += len(op.dims[0])
    return res


def permuteTensor(op, opPermutation):
    # swaps axes of a composite quantum object in a direction that satisfies opPermutation.
    # e.g. having an op with an opPermutation = [5, 3, 1, 8]
    # (i.e. that is a multi-ring operator acting somehow on qubits 5,3,1 and 8),
    # then axis swap ordering is [2, 1, 0, 3]. Returns a permuted tensor
    index = 0
    perm = []
    prevMin = -1
    for _ in range(len(opPermutation)):
        currentMin = 100
        for i in range(len(opPermutation)):
            if currentMin > opPermutation[i] and opPermutation[i] > prevMin:
                currentMin = opPermutation[i]
                index = i
        prevMin = currentMin
        perm.append(index)
    return op.permute(perm)


def permutedOps(ops, permutation):
    opPermDict = distributePermutationIndxs(ops, permutation)
    permutedTensors = list(map(lambda i_op: permuteTensor(i_op[1], opPermDict[i_op[0]]), enumerate(ops)))
    return permutedTensors, opPermDict


def flattenIndexes(indxs, max_op_row_index):
    # returns [flattened_indxs] so that indexes of compound quantum objects are mapped
    # to a collection of indexes of equivalent collection of tensored subobjects,
    # e.g.  indxs = [0, 2, 1, 3] and max_op_row_index = [2,4,2,4], then
    # flattenIndexes = res => [0,(1,0), 1, (1,1)] => [0, 1, 0, 1, 1, 1]
    res = []
    for i, indx in enumerate(indxs):
        if max_op_row_index[i] == 2:
            res.append(indx)
        else:
            partial_res = []
            for _ in range(int(log2(max_op_row_index[i]))):
                partial_res = [indx % 2] + partial_res
                indx = int(indx / 2)
            res += partial_res
    return res


def createColumn(ops, indxs, enumerated_ops, permutation=None):
    opColumn = Qobj(1.)
    for i, op in enumerated_ops:
        curColumn = Qobj(op.full()[indxs[i]], shape=(op.shape[1], 1))
        opColumn = tensor(opColumn, curColumn)
    return Qobj(opColumn, dims=input.dims)


def permutedRowIndex(opPermDict, i_op, flattened_indxs):
    i, op = i_op
    opPerm = opPermDict[i]
    index = 0
    dim = 1
    for n in range(len(opPerm) - 1, -1, -1):
        index += flattened_indxs[opPerm[n]] * dim
        dim *= 2  # op.dims[0][n]
    print(index, flattened_indxs, opPerm)
    return index


def permutedRowsIndexes(ops, indxs, max_op_row_index, permutation, opPermDict):
    flattened_indxs = flattenIndexes(indxs, max_op_row_index)
    return list(map(lambda i_op: permutedRowIndex(opPermDict, i_op, flattened_indxs), enumerate(ops)))


def createColumnFunc(ops, indxs, enumerated_ops, max_op_row_index, permutation, opPermDict):
    # if permutation is not None:
    # 	indxs = permutedRowsIndexes(ops, indxs, max_op_row_index, permutation, opPermDict)
    columnMapFun = lambda i_op: Qobj(i_op[1].full()[indxs[i_op[0]]], shape=(i_op[1].shape[1], 1))
    return Qobj(tensor(list(map(columnMapFun, enumerated_ops))), dims=input.dims)


def permute(i, N, permutation):
    binS = bin(i)[2:].zfill(N)
    permutedBinS = "".join(map(lambda j: binS[permutation[j]], range(N)))
    return int(permutedBinS, 2)


def permuteColumn(opColumn, N, permutation):
    res = [[] for _ in range(2 ** N)]
    col = opColumn.full()
    for j in range(2 ** N):
        permuted_j = permute(j, N, permutation)
        res[permuted_j].append(col[j][0])
    o = Qobj(res, dims=opColumn.dims, shape=opColumn.shape)
    # print(o, opColumn)
    return o


def customTensor(ops, input, N, use_numpy=False, permutation=None):
    opPermDict = None
    # if permutation is not None:
    # 	ops, opPermDict = permutedOps(ops, permutation)
    max_op_row_index = list(map(lambda x: x.shape[0], ops))
    indxs = [0 for _ in range(len(ops))]
    enumerated_ops = list(enumerate(ops))
    res = array([])
    for q_index in range(input.shape[0]):
        fillIndxs(indxs, q_index, max_op_row_index)
        opColumn = createColumnFunc(ops, indxs, enumerated_ops, max_op_row_index, permutation, opPermDict)
        # if permutation is not None:
        # opColumn = opColumn.permute(permutation)
        # assert opColumn.permute(permutation) == (permuteColumn(opColumn, N, permutation))
        # opColumn = permuteColumn(opColumn, N, permutation)
        elem = (opColumn.dag() * input).data[0, 0] \
            if not use_numpy \
            else matrix(opColumn.full()).getH() @ input.full()

        res = append(res, array(elem))
        del opColumn
    res = Qobj(res, dims=input.dims)
    return res


input = ket("00101111111110010010111110")
ops = [
    sigmax(),
    hadamard_transform(),
    controlled_gate(sigmax()),
    hadamard_transform(),
    controlled_gate(sigmax()),
    controlled_gate(sigmax()),
    hadamard_transform(),
    controlled_gate(sigmax()),
    hadamard_transform(),
    controlled_gate(sigmax()),
    controlled_gate(sigmax()),
    controlled_gate(sigmax()),
    hadamard_transform(),
    controlled_gate(sigmax()),
    hadamard_transform(),
    controlled_gate(sigmax()),
    hadamard_transform()
]

# input = ket("110")
# ops = [controlled_gate(sigmax()), identity(2)]
# permutation = [0, 2, 1]

input_string = "01101"
input = ket(input_string)
ops = [
    controlled_gate(sigmax()),
    qeye(2),
    qeye(2),
    qeye(2),
]
permutation = [0, 4, 1, 2, 3]
assert input.permute(permutation) == permuteColumn(input, len(input_string), permutation)
psi = tensor(ops).permute(permutation) * input
test = (tensor(ops) * input).permute(permutation)
assert (psi == test)
test = (tensor(ops) * test.permute(permutation)).permute(permutation)
assert (input == test)

input_string = "01101"
input = ket(input_string)
ops = [
    controlled_gate(sigmax()),
    hadamard_transform(),
    controlled_gate(sigmax())
]
permutation = [0, 4, 1, 2, 3]

print("start")
psi = tensor(ops).permute(permutation) * input
print("benchmark psi created")

start = datetime.datetime.now()
res = customTensor(ops, input, len(input_string), use_numpy=False, permutation=permutation)
end = datetime.datetime.now()
# print(psi)
# print(res)
assert res == psi
print("one, qutip", (end - start))

start = datetime.datetime.now()
res = customTensor(ops, input, len(input_string), permutation=permutation)
end = datetime.datetime.now()
assert res == psi
print("one, qutip", (end - start))

assert (tensor(ops).permute(permutation) * res == input)
res = customTensor(ops, res, len(input_string), permutation=permutation)
print("two", res)
assert (res == input)

# ket("10010101001").data.tocoo().row[0]