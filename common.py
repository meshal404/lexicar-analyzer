EPS = ""   # the epsilon "symbol"
ALPHABET = [chr(c) for c in range(32, 127)] + ["\t", "\n", "\r"]

# Rules everyone follows:
#  - states are ints 0..size-1
#  - a symbol is ONE character (or EPS). Person 1 expands [a-z] into single chars.
#  - accept[state] = (token_name, priority). SMALLER priority number = earlier in spec = wins.


class NFA:
    def __init__(self):
        self.size = 0        # number of states
        self.start = 0
        self.edges = {}      # (state, symbol) -> set of next states
        self.accept = {}     # state -> (token_name, priority)

    def new_state(self):
        self.size += 1
        return self.size - 1

    def add(self, src, symbol, dst):
        self.edges.setdefault((src, symbol), set()).add(dst)


class DFA:
    def __init__(self):
        self.size = 0
        self.start = 0
        self.edges = {}      # (state, char) -> next state   (missing = dead end)
        self.accept = {}     # state -> (token_name, priority)
        self.dead = None

    def new_state(self):
        self.size += 1
        return self.size - 1

    def step(self, state, ch):
        return self.edges.get((state, ch))   # None means stuck