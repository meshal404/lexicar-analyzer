from common import NFA, DFA, EPS, ALPHABET

def epsilon_closure(nfa, states):
    result = set(states)
    todo = list(states)
    while todo:
        s = todo.pop()
        for t in nfa.edges.get((s, EPS), set()):
            if t not in result:
                result.add(t)
                todo.append(t)

    return frozenset(result)


def move(nfa, states, symbol):
    result = set()
    for s in states:
        result |= nfa.edges.get((s, symbol), set())

    return result


def combine(nfas):
    big = NFA()
    big.start = big.new_state()
    offset = 1
    for n in nfas:
        for _ in range(n.size):
            big.new_state()

        for (s, sym), targets in n.edges.items():
            for t in targets:
                big.add(s + offset, sym, t + offset)

        for s, info in n.accept.items():
            big.accept[s + offset] = info

        big.add(big.start, EPS, n.start + offset)
        offset += n.size
    return big


def nfa_to_dfa(nfa, alphabet=ALPHABET):
    dfa = DFA()
    start_set = epsilon_closure(nfa,{nfa.start})
    ids = {start_set: dfa.new_state()}
    dfa.start = ids[start_set]
    todo = [start_set]

    while todo:
        current = todo.pop()
        cur_id = ids[current]

        accepting = [nfa.accept[s] for s in current if s in nfa.accept]
        if accepting:
            dfa.accept[cur_id] = min(accepting, key=lambda info: info[1])

        for ch in alphabet:
            target = epsilon_closure(nfa, move(nfa, current, ch))
            if target not in ids:
                ids[target] = dfa.new_state()
                todo.append(target)
            dfa.edges[(cur_id, ch)] = ids[target]

    empty = frozenset()
    if empty in ids:
        dfa.dead = ids[empty]
    return dfa
