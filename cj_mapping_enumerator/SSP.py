

class static_values:
    def __init__(self, values, target):
        self.values = values
        self.target = target

def unique_w_counts(values):
    # returns sorted list of pairs (value, count)
    values.sort()
    result = [(values[0], 1)]

    for i in range(1, len(values)):
        if values[i] != values[i - 1]:
            result.append((values[i], 1))
        else:
            result[-1] = (values[i], result[-1][1] + 1)
    return result

def ssp(values: list[int], target: int, allowed_error:int=0) -> list[list[int]]:
    # returns all unique SSP solutions (same values are treated as indistinguishable) 
    unique_values = unique_w_counts(values)

    remaining_positive = sum([v[0]*v[1] for v in unique_values if v[0] > 0])
    solutions = rec_ssp(static_values(unique_values, target), (0, 0), 0, [], remaining_positive, allowed_error)

    values.sort()

    valued_solutions = [list(values[i] for i in range(len(s)) if s[i] == 1) for s in solutions]

    return valued_solutions

def next_index(index, value):
    if index[1] >= value[1] - 1:
        return (index[0] + 1, 0)
    return (index[0], index[1] + 1)


def rec_ssp(static_values, index, s, decisions, remaining_positive, allowed_error):
    result = []

    if s - allowed_error <= static_values.target <= s + 10 and decisions and decisions[-1] != 0:
        # add new decisions leading to the target sum
        result += [decisions]
    
    if index[0] >= len(static_values.values) or s + remaining_positive + allowed_error < 0:
        # end of array or not enough remaining values to sum to 0
        return result
    
    next_i = next_index(index, static_values.values[index[0]])

    v = static_values.values[index[0]][0]
    if v > 0:
        remaining_positive -= v
    
    if index[1] > 0:
        if decisions[-1] == 0:
            # if a value was excluded once don't use it later
            return result + rec_ssp(static_values, next_i, s, decisions + [0], remaining_positive, allowed_error)

    return result + rec_ssp(static_values, next_i, s + v, decisions + [1], remaining_positive, allowed_error) + rec_ssp(static_values, next_i, s, decisions + [0], remaining_positive, allowed_error)

