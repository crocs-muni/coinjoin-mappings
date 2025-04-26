
def merge_txos(txos, groups):
    txo_groups = []
    for gid, g in enumerate(groups):
        group = []
        for i in txos:
            if i.address in g:
                group.append(i)
            
        if len(group) >= 1:
            txo_groups.append((group, gid))

    new_txos = []
    group_ids = []

    for txo in txos:

        for g in txo_groups:
            if txo in g[0]:
                break
        else:
            new_txos.append(txo)
            group_ids.append(None)
    
    for g, gid in txo_groups:
        ntxo = g[0]
        for t in g[1:]:
            ntxo.effective_value += t.effective_value
            ntxo.address += "," + t.address
        new_txos.append(ntxo)
        group_ids.append(gid)
    return new_txos, group_ids
        



def preprocess(inputs, outputs, groups):

    inputs, in_gids = merge_txos(inputs, groups)
    outputs, out_gids = merge_txos(outputs, groups)

    merge_ids = set([x for x in in_gids if x is not None]).intersection(set([x for x in out_gids if x is not None]))
    
    new_inputs = [inputs[i] for i in range(len(inputs)) if in_gids[i] is None or in_gids[i] not in merge_ids]
    new_outputs = [outputs[i] for i in range(len(outputs)) if out_gids[i] is None or out_gids[i] not in merge_ids]

    for gid in merge_ids:
        i_index = in_gids.index(gid)
        o_index = out_gids.index(gid)
        inp = inputs[i_index]
        outp = outputs[o_index]

        if inp.effective_value > outp.effective_value:
            inp.effective_value -= outp.effective_value
            inp.address += "," + outp.address
            new_inputs.append(inp)
        else:
            outp.effective_value -= inp.effective_value
            outp.address += "," + inp.address
            new_outputs.append(outp)
        
    return new_inputs, new_outputs
