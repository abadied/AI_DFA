import Board as bd
import Constants


class AutomatasState:
    """This class represents a specific state of the game combined with the state in the automaton.
       it contains all parameters to fully characterize specific pair"""

    def __init__(self, dfa_dict):
        """

        :type dfa: DFA
        """
        self.state_in_auto = {}
        self.dfa_dict = dfa_dict

        # initiate state in automata's
        for dfa_key in self.dfa_dict:
            self.state_in_auto[dfa_key] = self.dfa_dict[dfa_key]['dfa'].Initial

    def next_state(self, op, obs):
        "givan a pair state and a legal operation, returns the next pair state"
        if op == "idle":
            return self
        new_auto_state = AutomatasState(self.dfa_dict)
        new_state_in_auto = {}

        for dfa_key in self.dfa_dict:
            new_state_in_auto[dfa_key]['current_state'] = self.dfa_dict[dfa_key]['dfa'].evalSymbol(self.state_in_auto, new_state_in_auto[dfa_key]['current_state'],
                                                                                  Constants.value_letter_dictionary[op])
            new_state_in_auto[dfa_key]['current_state'] = self.dfa_dict[dfa_key]['dfa'].evalSymbol(self.state_in_auto, new_state_in_auto[dfa_key]['current_state'],
                                                                                  Constants.value_letter_dictionary[obs])
        new_auto_state.state_in_auto = new_state_in_auto
        return new_auto_state

    def legal_op(self, op):
        """

        :param op:
        :return:
        """
        auomatas_possible_transitions = set()
        for dfa_key in self.dfa_dict:
            auomatas_possible_transitions.add(self.dfa_dict[dfa_key]['dfa'].evalSymbol(self.state_in_auto, self.dfa_dict[dfa_key]['current_state'],
                                                                                  Constants.value_letter_dictionary[op]))

        return op in auomatas_possible_transitions

    def get_state_key(self):
        """

        :return:
        """
        state_key = []
        for dfa_key in self.dfa_dict:
            state_key.append(self.dfa_dict[dfa_key]['current_state'])

        return state_key

    def print_state(self):
        """
        just for debug"
        :return:
        """
        pass
