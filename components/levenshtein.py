def idsc_dict(insertions, deletions, substitutions, correct):
    return {"i": insertions, "d": deletions, "s": substitutions, "c": correct}


def join_dicts(*dicts):
    i = 0
    d = 0
    s = 0
    c = 0
    for idsc in dicts:
        i += idsc["i"]
        d += idsc["d"]
        s += idsc["s"]
        c += idsc["c"]
    return idsc_dict(i, d, s, c)


def levenshtein(word, reference):
    d = [[(0, dict()) for j in range(len(reference)+1)] for i in range(len(word)+1)]

    for i in range(len(word)+1):
        d[i][0] = (i, idsc_dict(i, 0, 0, 0))

    for j in range(len(reference)+1):
        d[0][j] = (j, idsc_dict(0, j, 0, 0))

    for j in range(len(reference)):
        for i in range(len(word)):
            if word[i] == reference[j]:
                substitution_cost = 0
                substitution_dict = idsc_dict(0, 0, 0, 1)
            else:
                substitution_cost = 1
                substitution_dict = idsc_dict(0, 0, 1, 0)

            d[i+1][j+1] = min((d[i][j+1][0] + 1, join_dicts(d[i][j+1][1], idsc_dict(1, 0, 0, 0))),
                              (d[i+1][j][0] + 1, join_dicts(d[i+1][j][1], idsc_dict(0, 1, 0, 0))),
                              (d[i][j][0] + substitution_cost, join_dicts(d[i][j][1], substitution_dict)),
                              key=lambda x: x[0])

    return d[len(word)][len(reference)]


def manual_levenshtein(word, options):
    best_match = ("", len(word),)
    for reference in options:
        distance = levenshtein(word.lower(), reference.lower())[0]
        if distance < best_match[1]:
            best_match = (reference, distance,)
    return best_match
