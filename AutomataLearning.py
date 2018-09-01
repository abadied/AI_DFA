import copy
import math

import Dfa


def convert_num_to_word(num):
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
        elif value == 1:
            word = "u" + word
        elif value == 2:
            word = "d" + word
        elif value == 3:
            word = "l" + word
        elif value == 4:
            word = "r" + word
        elif value == 5:
            word = "c" + word
        elif value == 6:
            word = "p" + word
        elif value == 7:
            word = "k" + word
        elif value == 8:
            word = "w" + word
        elif value == 9:
            word = "q" + word
        elif value == 10:
            word = "e" + word
        elif value == 11:
            word = "t" + word
        elif value == 12:
            word = "f" + word
        elif value == 13:
            word = "s" + word
        elif value == 14:
            word = "b" + word
    return word


def convert_letter_to_action(letter):
    if letter == "u":
        return "up"
    if letter == "d":
        return "down"
    if letter == "l":
        return "left"
    if letter == "r":
        return "right"
    if letter == "c":
        return "clean"
    if letter == "p":
        return "pick"
    if letter == "k":
        return "putInBasket"


def convert_letter_to_observation(letter):
    if letter == "w":
        return "right_wall"
    if letter == "q":
        return "left_wall"
    if letter == "e":
        return "upper_wall"
    if letter == "t":
        return "downer_wall"
    if letter == "f":
        return "fruit"
    if letter == "s":
        return "stain"
    if letter == "b":
        return "basket"


def check_reward_type(reward_type, state):
    if reward_type == 'fruit':
        pass
    elif reward_type == 'clean_stain':
        pass
    elif reward_type == 'put_in_basket':
        pass


def learn_dfa(initial_state, max_word_length, reward_type):
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
        former_state = None
        current_state = initial_state
        word = convert_num_to_word(counter)
        counter += 1
        if word == "" and counter > 1:
            continue
        num_of_words += 1
        word_to_read = word
        non_markovian_reward = False

        while not (current_state.is_end() or word_to_read == ""):  #assuming that the initial state is not an accepting state
            action = convert_letter_to_action(word_to_read[0:1])
            word_to_read = word_to_read[1:]
            _reward = check_reward_type(reward_type, former_state)
            former_state = copy.deepcopy(current_state)
            current_state = current_state.next_state(action)

        if non_markovian_reward:
            s_plus.add(word)
        else:
            s_minus.add(word)
    dfa = Dfa.synthesize(s_plus, s_minus)
    return dfa
