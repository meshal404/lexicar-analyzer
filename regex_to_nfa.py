from common import NFA, EPS

ESCAPES = {'t': '\t', 'n': '\n', 'r': '\r'}
PRECEDENCE = {'|': 1, '.': 2}


def tokenize(regex):
    tokens = []
    i = 0
    while i < len(regex):
        c = regex[i]

        if c == '\\':
            next_char = ESCAPES.get(regex[i + 1], regex[i + 1])
            tokens.append(('CHAR', {next_char}))
            i += 2

        elif c == '[':
            chars = set()
            i += 1
            while regex[i] != ']':
                if regex[i] == '\\':
                    chars.add(ESCAPES.get(regex[i + 1], regex[i + 1]))
                    i += 2
                elif regex[i + 1] == '-' and regex[i + 2] != ']':
                    for code in range(ord(regex[i]), ord(regex[i + 2]) + 1):
                        chars.add(chr(code))
                    i += 3
                else:
                    chars.add(regex[i])
                    i += 1
            tokens.append(('CHAR', chars))
            i += 1

        elif c in '|*+?()':
            tokens.append(('OP', c))
            i += 1

        else:
            tokens.append(('CHAR', {c}))
            i += 1

    return tokens


def add_concat(tokens):
    result = []
    for k in range(len(tokens)):
        result.append(tokens[k])

        if k + 1 < len(tokens):
            left = tokens[k]
            right = tokens[k + 1]

            left_ends = (left[0] == 'CHAR'
                         or left == ('OP', ')')
                         or (left[0] == 'OP' and left[1] in '*+?'))
            right_starts = (right[0] == 'CHAR'
                            or right == ('OP', '('))

            if left_ends and right_starts:
                result.append(('OP', '.'))

    return result


def to_postfix(tokens):
    output = []
    stack = []

    for tok in tokens:
        kind, value = tok

        if kind == 'CHAR':
            output.append(tok)

        elif value in '*+?':
            output.append(tok)

        elif value == '(':
            stack.append(tok)

        elif value == ')':
            while stack[-1] != ('OP', '('):
                output.append(stack.pop())
            stack.pop()

        else:
            while (stack and stack[-1] != ('OP', '(')
                   and PRECEDENCE[stack[-1][1]] >= PRECEDENCE[value]):
                output.append(stack.pop())
            stack.append(tok)

    while stack:
        output.append(stack.pop())

    return output


def thompson(postfix, token_name, priority):
    nfa = NFA()
    stack = []

    for kind, value in postfix:

        if kind == 'CHAR':
            s = nfa.new_state()
            e = nfa.new_state()
            for ch in value:
                nfa.add(s, ch, e)
            stack.append((s, e))

        elif value == '.':
            s2, e2 = stack.pop()
            s1, e1 = stack.pop()
            nfa.add(e1, EPS, s2)
            stack.append((s1, e2))

        elif value == '|':
            s2, e2 = stack.pop()
            s1, e1 = stack.pop()
            s = nfa.new_state()
            e = nfa.new_state()
            nfa.add(s, EPS, s1)
            nfa.add(s, EPS, s2)
            nfa.add(e1, EPS, e)
            nfa.add(e2, EPS, e)
            stack.append((s, e))

        elif value == '*':
            s1, e1 = stack.pop()
            s = nfa.new_state()
            e = nfa.new_state()
            nfa.add(s, EPS, s1)
            nfa.add(s, EPS, e)
            nfa.add(e1, EPS, s1)
            nfa.add(e1, EPS, e)
            stack.append((s, e))

        elif value == '+':
            s1, e1 = stack.pop()
            s = nfa.new_state()
            e = nfa.new_state()
            nfa.add(s, EPS, s1)
            nfa.add(e1, EPS, s1)
            nfa.add(e1, EPS, e)
            stack.append((s, e))

        elif value == '?':
            s1, e1 = stack.pop()
            s = nfa.new_state()
            e = nfa.new_state()
            nfa.add(s, EPS, s1)
            nfa.add(s, EPS, e)
            nfa.add(e1, EPS, e)
            stack.append((s, e))

    start, end = stack.pop()
    nfa.start = start
    nfa.accept[end] = (token_name, priority)
    return nfa


def regex_to_nfa(regex, token_name, priority):
    tokens = tokenize(regex)
    tokens = add_concat(tokens)
    postfix = to_postfix(tokens)
    return thompson(postfix, token_name, priority)
