import copy
import math

from Dfa import DfaCreator
import StateGenericFunctions as gf
import Constants
from GILearner.dfa_creator import DFACreator


class AutomataLearner(object):

    def __init__(self, letter_value_dictionary, reward_value_dict):
        self.letter_value_dictionary = letter_value_dictionary
        self.value_letter_dictionary = {letter_value_dictionary[key]: key for key in letter_value_dictionary.keys()}
        self.sorted_keys = sorted(list(letter_value_dictionary.keys()))
        self.reward_value_dict = reward_value_dict

    def convert_num_to_word(self, num):
        """
        converts @num to the @return word. the word is in sigma*
        :param num:
        :return:
        """
        word = ""
        while num:
            num, value = divmod(num, 14)
            if value == 0:
                return ""
            else:
                word = self.sorted_keys[value - 1] + word
        return word

    def convert_letter_to_value(self, letter):
        return self.letter_value_dictionary[letter]

    def convert_value_to_letter(self, value):
        return self.value_letter_dictionary[value]

    def check_reward_type(self, reward_type, state, action):
        return gf.compute_reward_by_type(state, action, reward_type) > 0

    def learn_dfa(self, initial_state, max_word_length, reward_type):
        """computes an automaton from sets of words up to specific length. acception of a word is determined by the function
           computeReward_NonMarkovian. current implementation assumes that there is a single accepting state, and for every
           accepted word, all words which this word is a prefix of them, are also accepted, because the reward was received
           in this sequence of actions/letters"""
        s_plus = set()
        s_minus = set()
        counter = 0

        while counter < 200:
            current_state = initial_state
            counter += 1
            word = ""
            num_of_steps_counter = 0
            states_cash_dict = dict()
            states_cash_dict[current_state.hash] = gf.create_possible_ops_dict(current_state)

            while not current_state.is_end() and num_of_steps_counter < max_word_length:
                # action = gf.get_least_common_op(states_cash_dict[current_state.hash])
                action = gf.get_random_op(states_cash_dict[current_state.hash])
                current_action_letter = self.convert_value_to_letter(action)
                non_markovian_reward = self.check_reward_type(reward_type, current_state, action)
                current_state = current_state.next_state(action)
                if current_state.hash not in states_cash_dict.keys():
                    states_cash_dict[current_state.hash] = gf.create_possible_ops_dict(current_state)
                observation = current_state.get_observation()
                word += current_action_letter + observation
                num_of_steps_counter += 1

                if non_markovian_reward:
                    s_plus.add(word)
                else:
                    s_minus.add(word)
        # dfa = DfaCreator.synthesize(s_plus, s_minus)
        dfa = DfaCreator.create_and_minimize_dfa(s_plus, s_minus)

        words_dict = {'s_plus': s_plus,
                      's_minus': s_minus}
        return dfa, words_dict

    def learn_all_dfas(self, initial_state, max_word_length, dfa_dict):
        """computes an automaton from sets of words up to specific length. acception of a word is determined by the function
           computeReward_NonMarkovian. current implementation assumes that there is a single accepting state, and for every
           accepted word, all words which this word is a prefix of them, are also accepted, because the reward was received
           in this sequence of actions/letters"""
        counter = 0

        reward_dict = {}
        for _key in dfa_dict:
            reward_dict[_key] = {'last_value': False, 's_plus': set(), 's_minus': set()}

        while counter < 20:
            current_state = copy.deepcopy(initial_state)
            counter += 1
            word = ""
            num_of_steps_counter = 0
            states_cash_dict = dict()
            states_cash_dict[current_state.hash] = gf.create_possible_ops_dict(current_state)

            while not current_state.is_end() and num_of_steps_counter < max_word_length:
                # action = gf.get_least_common_op(states_cash_dict[current_state.hash])
                action = gf.get_random_op(states_cash_dict[current_state.hash])
                current_action_letter = self.convert_value_to_letter(action)
                for _key in dfa_dict:
                    reward_dict[_key]['last_value'] = self.check_reward_type(_key, current_state, action)
                current_state = current_state.next_state(action)
                if current_state.hash not in states_cash_dict.keys():
                    states_cash_dict[current_state.hash] = gf.create_possible_ops_dict(current_state)
                observation = current_state.get_observation()
                word += current_action_letter + observation
                num_of_steps_counter += 1

                for _key in reward_dict:
                    if reward_dict[_key]['last_value']:
                        reward_dict[_key]['s_plus'].add(word)
                    else:
                        reward_dict[_key]['s_minus'].add(word)

        complete_dfa_dict = {}
        words_dict = {}
        for _key in dfa_dict:
            s_plus = reward_dict[_key]['s_plus']
            s_minus = reward_dict[_key]['s_minus']
            new_dfa = DFACreator.create_dfa(s_plus, s_minus)

            # TODO: make addition of sets
            words_dict = {'s_plus': s_plus,
                          's_minus': s_minus}
            complete_dfa_dict[_key] = {'dfa': new_dfa,
                                       # 'words_dict': words_dict,
                                       'current_state': 0,
                                       'reward': Constants.credits[_key],
                                       'accepting_states': DFACreator.get_accepting_states(new_dfa)}

        return complete_dfa_dict, words_dict

    # def learn_dfa(self, initial_state, max_word_length, reward_type):
    #     """computes an automaton from sets of words up to specific length. acception of a word is determined by the function
    #        computeReward_NonMarkovian. current implementation assumes that there is a single accepting state, and for every
    #        accepted word, all words which this word is a prefix of them, are also accepted, because the reward was received
    #        in this sequence of actions/letters"""
    #     s_plus = set()
    #     s_minus = set()
    #     counter = 0
    #     num_of_words = 0
    #
    #     while counter < math.pow(6, max_word_length): # in order to learn all words up to length wordLength, we need to iterate on all numbers up to pow(6,wordLength).
    #                                     # each number corresponds to a 'word' which is a series of actions.
    #         current_state = initial_state
    #         word = self.convert_num_to_word(counter)
    #         counter += 1
    #         if word == "" and counter > 1:
    #             continue
    #         num_of_words += 1
    #         word_to_read = word
    #         non_markovian_reward = False
    #
    #         while not (current_state.is_end() or word_to_read == ""):  #assuming that the initial state is not an accepting state
    #             action = self.convert_letter_to_value(word_to_read[0:1])
    #             word_to_read = word_to_read[1:]
    #             former_state = copy.deepcopy(current_state)
    #             non_markovian_reward = self.check_reward_type(reward_type, former_state, action)
    #             current_state = current_state.next_state(action)
    #
    #         if non_markovian_reward:
    #             s_plus.add(word)
    #         else:
    #             s_minus.add(word)
    #     dfa = DfaCreator.synthesize(s_plus, s_minus)
    #     return dfa
