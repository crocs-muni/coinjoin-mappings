from SSP import ssp
from collections import Counter, defaultdict
from itertools import combinations
import numpy as np

def preprocess_txos(txos):
    return [x.effective_value for x in txos]


def filter_submappings(numeric_submappings):
    return [sm for sm in numeric_submappings if len(sm[0]) < 31 and len(sm[1]) < 11]


def find_numeric_submappings(inputs, outputs, allowed_error=0):
    ssp_values = preprocess_txos(inputs) + [-x for x in preprocess_txos(outputs)]

    ssp_solutions = ssp(ssp_values, 0, allowed_error)

    sub_mappings = [[[x for x in s if x >= 0], [-x for x in s if x < 0]] for s in ssp_solutions]

    return sub_mappings


def submultiset(a, b_counter):

    for k, v in b_counter.items():
        if v < a.count(k):
            return False
    return True


def is_feasible(in_counter, out_counter, solution, mod_solutions):
    ins = []
    outs = []
    for ind in solution:
        i = mod_solutions[ind][0]
        o = mod_solutions[ind][1]
        ins += i
        outs += o
    
    if not submultiset(ins, in_counter):
        return False
    return submultiset(outs, out_counter)

def is_complete(inputs, _outputs, solution, mod_solutions):
    # checking just inputs as outputs do not need to match - some can be owned by the coordinator
    ins = []
    for ind in solution:
        i = mod_solutions[ind][0]
        ins += i
    
    if len(ins) != len(inputs):
        return False
    
    ins.sort()
    return ins == inputs

def rec_enum_mappings(mod_solutions, in_vals, out_vals, in_counter, out_counter, index, solution, added):

    if not is_feasible(in_counter, out_counter, solution, mod_solutions) or index > len(mod_solutions):
        return
    
    if is_complete(in_vals, out_vals, solution, mod_solutions):
        yield solution
        return
    
    if index > 0 and added:
        # partial mapping can be repeated
        yield from rec_enum_mappings(mod_solutions, in_vals, out_vals, in_counter, out_counter, index, solution + [index - 1], True)
    
    if index == len(mod_solutions):
        # last item added
        return

    yield from rec_enum_mappings(mod_solutions, in_vals, out_vals, in_counter, out_counter, index + 1, solution + [index], True)
    yield from rec_enum_mappings(mod_solutions, in_vals, out_vals, in_counter, out_counter, index + 1, solution, False)


def get_mappings(inputs, outputs, numeric_submappings):

    in_vals = preprocess_txos(inputs)
    out_vals = preprocess_txos(outputs)
    in_counter = Counter(in_vals)
    out_counter = Counter(out_vals)
    in_vals.sort()
    out_vals.sort()
  
    yield from rec_enum_mappings(numeric_submappings, in_vals, out_vals, in_counter, out_counter, 0, [], False)


def rec_n_subm_to_vector(in_counter, out_counter, in_indices, in_len, out_indices, vector):
    if len(in_counter) == 0 and len(out_counter) == 0:
        yield vector
        return
    
    if len(in_counter) > 0: 
        v = in_counter[0][0]
        count = in_counter[0][1]

        for c in combinations(in_indices[v], count):
            vect_copy = vector[::]
            for i in c:
                vect_copy[i] = 1

            yield from rec_n_subm_to_vector(in_counter[1:], out_counter, in_indices, in_len, out_indices, vect_copy)
    else:
        v = out_counter[0][0]
        count = out_counter[0][1]

        for c in combinations(out_indices[v], count):
            vect_copy = vector[::]
            for i in c:
                vect_copy[i + in_len] = 1

            yield from rec_n_subm_to_vector(in_counter, out_counter[1:], in_indices, in_len, out_indices, vect_copy)



def n_subm_to_vector(nsubm, in_indices, in_len, out_indices, out_len):

    in_counter = Counter(nsubm[0])
    out_counter = Counter(nsubm[1])

    yield from rec_n_subm_to_vector(list(in_counter.items()), list(out_counter.items()), in_indices, in_len, out_indices, [0]*(in_len+out_len))




def values_to_indice_dict(values):

    inds = defaultdict(list)

    for i,v in enumerate(values):
        inds[v.effective_value].append(i)
    return inds


def rec_nmap_to_maps(subm_variants, nmap, vector, result, previous_sm, last_i):
    if (vector == 2).any():
        return
    
    if len(nmap) == 0:
        yield result
        return
    
    start = 0
    if previous_sm == nmap[0]:
        start = last_i + 1
    
    for i in range(start, len(subm_variants[nmap[0]])):
        yield from rec_nmap_to_maps(subm_variants, nmap[1:], vector + subm_variants[nmap[0]][i], result + [subm_variants[nmap[0]][i]], nmap[0], i)

def vector_to_subm(vector, inputs, outputs):
    ins = []
    outs = []
    for i, d in enumerate(vector):
        if d == 0:
            continue
        if i < len(inputs):
            ins.append(inputs[i])
        else:
            outs.append(outputs[i - len(inputs)])
    return (ins, outs)


def nmap_to_maps(subm_variants, nmap, inputs, outputs):

    for m in rec_nmap_to_maps(subm_variants, nmap, np.array([0 for _ in range(len(inputs)+len(outputs))]), [], -1, -1):
        yield [vector_to_subm(s, inputs, outputs) for s in m]


def get_numeric_mappings(inputs, outputs, max_error=0):
    numeric_submappings = find_numeric_submappings(inputs, outputs, max_error)

    numeric_submappings = filter_submappings(numeric_submappings)

    for nm in get_mappings(inputs, outputs, numeric_submappings):
        yield [numeric_submappings[i] for i in nm]

def get_all_mappings(inputs, outputs, max_error=0):

    numeric_submappings = find_numeric_submappings(inputs, outputs, max_error)

    numeric_submappings = filter_submappings(numeric_submappings)

    in_indices = values_to_indice_dict(inputs)
    out_indices = values_to_indice_dict(outputs)

    subm_variants = []

    for nsubm in numeric_submappings:
        subm_variants.append(list(n_subm_to_vector(nsubm, in_indices, len(inputs), out_indices, len(outputs))))


    for nmap in get_mappings(inputs, outputs, numeric_submappings):
        yield from nmap_to_maps(subm_variants, nmap, inputs, outputs)
        
