from GILearner.gi_learning import EDSMSolver
# e = EDSMSolver()
# e.add_pos("cab")
# e.add_pos("caa")
# e.add_pos("ca")
# e.add_neg("cba")
# e.add_neg("cbb")
# e.add_pos("ab")
# e.add_neg("c")
# e.run()
# print(e.dfa())
# print(e.alphabet())
# print(e.neg_count())


class DFACreator(object):

    @staticmethod
    def create_dfa(set_plus, set_minus):
        e = EDSMSolver()
        for word in set_plus:
            e.add_pos(word)
        for word in set_minus:
            e.add_neg(word)
        e.run()
        e.dfa()
        e.alphabet()
        return e