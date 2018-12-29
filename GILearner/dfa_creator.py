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
        """

        :param set_plus:
        :param set_minus:
        :return:
        """
        e = EDSMSolver()
        for word in set_plus:
            e.add_pos(word)
        for word in set_minus:
            e.add_neg(word)
        e.run()
        e.dfa()
        e.alphabet()
        return e

    @staticmethod
    def get_accepting_states(e):
        """

        :param e:
        :return:
        """
        accepting_states = []
        number_of_states = e.state_count()
        for i in range(number_of_states):
            if e.is_accept(i):
                accepting_states.append(i)
        return accepting_states