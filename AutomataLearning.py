import copy
import math

from Dfa import DfaCreator
import StateGenericFunctions as gf


class AutomataLearner(object):

    def __init__(self, letter_value_dictionary, reward_value_dict):
        self.letter_value_dictionary = letter_value_dictionary
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
        # if letter == "u":
        #     return "up"
        # if letter == "d":
        #     return "down"
        # if letter == "l":
        #     return "left"
        # if letter == "r":
        #     return "right"
        # if letter == "c":
        #     return "clean"
        # if letter == "p":
        #     return "pick"
        # if letter == "k":
        #     return "putInBasket"
        # if letter == "w":
        #     return "right_wall"
        # if letter == "q":
        #     return "left_wall"
        # if letter == "e":
        #     return "upper_wall"
        # if letter == "t":
        #     return "downer_wall"
        # if letter == "f":
        #     return "fruit"
        # if letter == "s":
        #     return "stain"
        # if letter == "b":
        #     return "basket"

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
        num_of_words = 0

        while counter < math.pow(6, max_word_length): # in order to learn all words up to length wordLength, we need to iterate on all numbers up to pow(6,wordLength).
                                        # each number corresponds to a 'word' which is a series of actions.
            current_state = initial_state
            word = self.convert_num_to_word(counter)
            counter += 1
            if word == "" and counter > 1:
                continue
            num_of_words += 1
            word_to_read = word
            non_markovian_reward = False

            while not (current_state.is_end() or word_to_read == ""):  #assuming that the initial state is not an accepting state
                action = self.convert_letter_to_value(word_to_read[0:1])
                word_to_read = word_to_read[1:]
                former_state = copy.deepcopy(current_state)
                non_markovian_reward = self.check_reward_type(reward_type, former_state, action)
                current_state = current_state.next_state(action)

            if non_markovian_reward:
                s_plus.add(word)
            else:
                s_minus.add(word)
        dfa = DfaCreator.synthesize(s_plus, s_minus)
        return dfa
