from FAdo.fa import *


class DfaCreator(object):

    @staticmethod
    def alphabet(sentence):
        """Finds all letters in S
        Input: a set of strings: S
        Output: the alphabet of S"""
        result = set()
        for word in sentence:
            for letter in word:
                result.add(letter)
        return result

    @staticmethod
    def prefixes(sentence):
        """Finds all prefixes in S
        Input: a set of strings: S
        Output: the set of all prefixes of S"""
        result = set()
        for word in sentence:
            for i in range(len(word) + 1):
                result.add(word[:i])
        return result

    @staticmethod
    def suffixes(sentence):
        """Finds all suffixes in S
        Input: a set of strings: S
        Output: the set of all suffixes of S"""
        result = set()
        for word in sentence:
            for i in range(len(word) + 1):
                result.add(word[i:])
        return result

    @staticmethod
    def catenate(first_word_set, second_word_set):
        """Determine the concatenation of two sets of words
        Input: two sets (or lists) of strings: A, B
        Output: the set AB"""

        return set(first_word + sec_word for first_word in first_word_set for sec_word in second_word_set)

    @staticmethod
    def ql(sentence):
        """Returns the list of S in quasi-lexicographic order
        Input: collection of strings
        Output: a sorted list"""

        return sorted(sentence, key=lambda word: (len(word), word))

    @staticmethod
    def build_pta(sentence):
        """Build a prefix tree acceptor from examples
        Input: the set of strings, S
        Output: a DFA representing PTA"""

        det_auotmata = DFA()
        q = dict()
        for u in DfaCreator.prefixes(sentence):
            q[u] = det_auotmata.addState(u)
        for w in iter(q):
            u, a = w[:-1], w[-1:]
            if a != '':
                det_auotmata.addTransition(q[u], a, q[w])
            if w in sentence:
                det_auotmata.addFinal(q[w])
        det_auotmata.setInitial(q[''])
        return det_auotmata

    @staticmethod
    def merge(q1, q2, nfa):
        """Join two states, i.e., q2 is absorbed by q1
        Input: q1, q2 state indexes and an NFA A
        Output: the NFA A updated"""
        n = len(nfa.States)
        for q in range(n):
            if q in nfa.delta:
                for a in nfa.delta[q]:
                    if q2 in nfa.delta[q][a]:
                        nfa.addTransition(q, a, q1)
            if q2 in nfa.delta:
                for a in nfa.delta[q2]:
                    if q in nfa.delta[q2][a]:
                        nfa.addTransition(q1, a, q)
        if q2 in nfa.Initial:
            nfa.addInitial(q1)
        if q2 in nfa.Final:
            nfa.addFinal(q1)
        nfa.deleteStates([q2])
        return nfa

    @staticmethod
    def accepts(word, q, nfa):
        """Verify if in an NFA A, a state q recognizes given word
        Input: a string w, a state index (int) q, and an NFA A
        Output: yes or no as Boolean value"""

        ilist = nfa.epsilonClosure(q)
        for letter in word:
            ilist = nfa.evalSymbol(ilist, letter)
            if not ilist:
                return False
        return not nfa.Final.isdisjoint(ilist)

    @staticmethod
    def make_candidate_states_list(suffix_set, nfa):
        """Build the sorted list of pairs of states to merge
        Input: a set of suffixes, U, and an NFA, A
        Output: a list of pairs of states, first most promising"""
        n = len(nfa.States)
        score = dict()
        langs = []
        pairs = []
        for i in range(n):
            langs.append(set(u for u in suffix_set if DfaCreator.accepts(u, i, nfa)))
        for i in range(n-1):
            for j in range(i+1, n):
                score[i, j] = len(langs[i] & langs[j])
                pairs.append((i, j))
        pairs.sort(key=lambda x: -score[x])
        return pairs

    @staticmethod
    def synthesize(set_plus, set_minus):
        """Infers an NFA consistent with the sample
        Input: the sets of examples and counter-examples
        Output: an NFA"""
        nfa = DfaCreator.build_pta(set_plus).toNFA()
        second_alphabet = DfaCreator.alphabet(set_minus)
        for sigma in second_alphabet:
            nfa.addSigma(sigma)
        suffix_set = DfaCreator.suffixes(set_plus)
        joined = True
        # TODO: notice new parameter max states
        max_states = 500
        # while joined and len(nfa.States) > max_states:
        #     pairs = DfaCreator.make_candidate_states_list(suffix_set, nfa)
        #     joined = False
        #     for (p, q) in pairs:
        #         dup_nfa = nfa.dup()
        #         DfaCreator.merge(p, q, dup_nfa)
        #         if not any(dup_nfa.evalWordP(w) for w in set_minus):
        #             nfa = dup_nfa
        #             joined = True
        #             break

        # TODO: make it faster or blocked in the number of states merging
        joined = True
        # while joined:
        #     joined = False
        #     for p in range(len(nfa.States)):
        #         if not joined:
        #             for q in range(len(nfa.States)):
        #                 dup_nfa = nfa.dup()
        #                 if p != q:
        #                     DfaCreator.merge(p, q, dup_nfa)
        #                     if dup_nfa is not None:
        #                         if not any(dup_nfa.evalWordP(w) for w in set_minus):
        #                             nfa = dup_nfa
        #                             joined = True
        #                             break
        return nfa

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

