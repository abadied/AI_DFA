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
            self.state_in_auto[dfa_key] = 0

        self.curr_obs = {'left_wall': 0,
                         'right_wall': 0,
                         'upper_wall': 0,
                         'downer_wall': 0,
                         # 'fruit': 0,
                         # 'stain': 0,
                         # 'basket': 0
                         }

    def next_state(self, op, obs):
        "givan a pair state and a legal operation, returns the next pair state"

        if op == "idle":
            return self

        # new_auto_state = AutomatasState(self.dfa_dict)
        # new_state_in_auto = {}

        for dfa_key in self.dfa_dict:
            # TODO: convert op and obs to relevant numbers according to alphabet from the automata
            alphabet_mapping = self.dfa_dict[dfa_key]['dfa'].alphabet()
            op_idx = int(alphabet_mapping[Constants.value_letter_dictionary[op]])
            obs_idx = int(alphabet_mapping[obs])
            dfa_matrix = self.dfa_dict[dfa_key]['dfa'].dfa()
            self.state_in_auto[dfa_key] = dfa_matrix[self.state_in_auto[dfa_key]][op_idx]
            self.state_in_auto[dfa_key] = dfa_matrix[self.state_in_auto[dfa_key]][obs_idx]

        def initialize_obs_dict():
            for obs_key in self.curr_obs.keys():
                self.curr_obs[obs_key] = 0

        # update obs

        if obs == 'w':    # right wall
            initialize_obs_dict()
            self.curr_obs['right_wall'] = 1

        elif obs == 'q':    # left wall
            initialize_obs_dict()
            self.curr_obs['left_wall'] = 1

        elif obs == 'e':    # upper wall
            initialize_obs_dict()
            self.curr_obs['upper_wall'] = 1

        elif obs == 't':    # downer wall
            initialize_obs_dict()
            self.curr_obs['downer_wall'] = 1

        elif obs == 'x':    # left up wall
            initialize_obs_dict()
            self.curr_obs['left_wall'] = 1
            self.curr_obs['upper_wall'] = 1

        elif obs == 'y':    # left down wall
            initialize_obs_dict()
            self.curr_obs['left_wall'] = 1
            self.curr_obs['downer_wall'] = 1

        elif obs == 'z':    # right up wall
            initialize_obs_dict()
            self.curr_obs['right_wall'] = 1
            self.curr_obs['upper_wall'] = 1

        elif obs == 'a':    # right down wall
            initialize_obs_dict()
            self.curr_obs['right_wall'] = 1
            self.curr_obs['downer_wall'] = 1

        elif obs == 'v':    # left right wall
            initialize_obs_dict()
            self.curr_obs['right_wall'] = 1
            self.curr_obs['left_wall'] = 1

        elif obs == 'j':    # upper downer wall
            initialize_obs_dict()
            self.curr_obs['upper_wall'] = 1
            self.curr_obs['downer_wall'] = 1

        elif obs == 'f':      # up down right walls
            initialize_obs_dict()
            self.curr_obs['upper_wall'] = 1
            self.curr_obs['downer_wall'] = 1
            self.curr_obs['right_wall'] = 1

        elif obs == 's':    # up down left walls
            initialize_obs_dict()
            self.curr_obs['upper_wall'] = 1
            self.curr_obs['downer_wall'] = 1
            self.curr_obs['left_wall'] = 1

        elif obs == 'b':    # right left down walls
            initialize_obs_dict()
            self.curr_obs['left_wall'] = 1
            self.curr_obs['downer_wall'] = 1
            self.curr_obs['right_wall'] = 1

        elif obs == 'm':    # right left up walls
            initialize_obs_dict()
            self.curr_obs['upper_wall'] = 1
            self.curr_obs['left_wall'] = 1
            self.curr_obs['right_wall'] = 1

        elif obs == 'n':    # no walls
            initialize_obs_dict()

        else:
            raise ValueError('unknown obs: ' + obs)

        return self.get_state_key()

    def legal_op(self, op):
        """

        :param op:
        :return:
        """

        if op == "idle":
            return True

        if op == "up" and self.curr_obs['upper_wall']:
            return False
        elif op == "down" and self.curr_obs['downer_wall']:
            return False
        elif op == "left" and self.curr_obs['left_wall']:
            return False
        elif op == "right" and self.curr_obs['right_wall']:
            return False
        else:
            return True

    def get_state_key(self):
        """

        :return:
        """
        state_key = []
        for obs_key in self.curr_obs.keys():
            state_key.append(self.curr_obs[obs_key])
        for dfa_key in self.dfa_dict.keys():
            state_key.append(self.state_in_auto[dfa_key])

        return state_key

    def reset(self):
        # initiate state in automata's
        for dfa_key in self.dfa_dict:
            self.state_in_auto[dfa_key] = 0

        self.curr_obs = {'left_wall': 0,
                         'right_wall': 0,
                         'upper_wall': 0,
                         'downer_wall': 0,
                         # 'fruit': 0,
                         # 'stain': 0,
                         # 'basket': 0
                         }

    def print_state(self):
        """
        just for debug"
        :return:
        """
        pass
