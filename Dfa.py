from FAdo.fa import *


def alphabet(S):
    """Finds all letters in S
    Input: a set of strings: S
    Output: the alphabet of S"""
    result = set()
    for s in S:
        for a in s:
            result.add(a)
    return result


def prefixes(S):
    """Finds all prefixes in S
    Input: a set of strings: S
    Output: the set of all prefixes of S"""
    result = set()
    for s in S:
        for i in range(len(s) + 1):
            result.add(s[:i])
    return result


def suffixes(S):
    """Finds all suffixes in S
    Input: a set of strings: S
    Output: the set of all suffixes of S"""
    result = set()
    for s in S:
        for i in range(len(s) + 1):
            result.add(s[i:])
    return result


def catenate(A, B):
    """Determine the concatenation of two sets of words
    Input: two sets (or lists) of strings: A, B
    Output: the set AB"""

    return set(a + b for a in A for b in B)


def ql(S):
    """Returns the list of S in quasi-lexicographic order
    Input: collection of strings
    Output: a sorted list"""

    return sorted(S, key=lambda x: (len(x), x))


def build_pta(S):
    """Build a prefix tree acceptor from examples
    Input: the set of strings, S
    Output: a DFA representing PTA"""

    A = DFA()
    q = dict()
    for u in prefixes(S):
        q[u] = A.addState(u)
    for w in iter(q):
        u, a = w[:-1], w[-1:]
        if a != '':
            A.addTransition(q[u], a, q[w])
        if w in S:
            A.addFinal(q[w])
    A.setInitial(q[''])
    return A


def merge(q1, q2, A):
    """Join two states, i.e., q2 is absorbed by q1
    Input: q1, q2 state indexes and an NFA A
    Output: the NFA A updated"""
    n = len(A.States)
    for q in range(n):
        if q in A.delta:
            for a in A.delta[q]:
                if q2 in A.delta[q][a]: A.addTransition(q, a, q1)
        if q2 in A.delta:
            for a in A.delta[q2]:
                if q in A.delta[q2][a]: A.addTransition(q1, a, q)
    if q2 in A.Initial: A.addInitial(q1)
    if q2 in A.Final: A.addFinal(q1)
    A.deleteStates([q2])
    return A


def accepts(w, q, A):
    """Verify if in an NFA A, a state q recognizes given word
    Input: a string w, a state index (int) q, and an NFA A
    Output: yes or no as Boolean value"""

    ilist = A.epsilonClosure(q)
    for c in w:
        ilist = A.evalSymbol(ilist, c)
        if not ilist:
            return False
    return not A.Final.isdisjoint(ilist)


def make_candidate_states_list(U, A):
    """Build the sorted list of pairs of states to merge
    Input: a set of suffixes, U, and an NFA, A
    Output: a list of pairs of states, first most promising"""
    n = len(A.States)
    score = dict()
    langs = []
    pairs = []
    for i in range(n):
        langs.append(set(u for u in U if accepts(u, i, A)))
    for i in range(n-1):
        for j in range(i+1, n):
            score[i, j] = len(langs[i] & langs[j])
            pairs.append((i, j))
    pairs.sort(key = lambda x: -score[x])
    return pairs


def synthesize(S_plus, S_minus):
    """Infers an NFA consistent with the sample
    Input: the sets of examples and counter-examples
    Output: an NFA"""
    A = build_pta(S_plus).toNFA()
    secondAlphabet = alphabet(S_minus)
    for sigma in secondAlphabet:
        A.addSigma(sigma)
    U = suffixes(S_plus)
    joined = True
    while joined:
        pairs = make_candidate_states_list(U, A)
        joined = False
        for (p, q) in pairs:
            B = A.dup()
            merge(p, q, B)
            if not any(B.evalWordP(w) for w in S_minus):
                A=B
                joined = True
                break

    joined = True
    while joined:
        joined = False
        for p in range(len(A.States)):
            if not joined:
                for q in range(len(A.States)):
                    B = A.dup()
                    if p != q:
                        merge(p, q, B)
                        if not any(B.evalWordP(w) for w in S_minus):
                            A = B
                            joined = True
                            break
    return A

# s1 = set(["aa","aba","bba"])
# s1 = set([])
# print "alphabet: ", alphabet(s1)
# print "prefixes: ", prefixes(s1)
# print "suffixes: ", suffixes(s1)
# print "catenate: ", catenate(s1,s1)
# print "quasi-lexicographic order: ", ql(prefixes(s1))
# s1PTA = buildPTA(s1)
# print s1PTA
# print s1PTA.Final
# print "delta is: ", s1PTA.delta
# newPTA = DFA.toNFA(s1PTA)
# newPTA = merge(1,3,newPTA)
# newPTA.addTransition(0,'a',2)
# print accepts('aa', 0, newPTA)

# S_plus = set(["uc","rluc","rudluc","rulduc"])
# S_minus = set(["","u","c","r","rc","ru","ruc","ruuc","ruluc","rulc","ruduc","rduc","rul"])
# dfa = synthesize(S_plus, S_minus)
# print dfa.States
# print
# print dfa.Initial
# print
# print dfa.Final
# print
# print dfa.delta
# print
# print accepts("rul",0,dfa)
# dfa.SPRegExp()
# S_plus = set(["10","100","1000"])
# S_minus = set(["0"])
# dfa = synthesize(S_plus, S_minus)
# print dfa.States
# print
# print dfa.Initial
# print
# print dfa.Final
# print
# print dfa.delta

