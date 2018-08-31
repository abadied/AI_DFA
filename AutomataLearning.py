import copy
import math

import Dfa

# all the constructed automata have the alphabet {'u','d','r','l','c'}, which relates to the actions
# ["up", "down", "left", "right", "clean"].

initialState = 0
maxWordLength = 0


def init_automata_learning(initialStateParam, maxWordLengthParam):
    """initializes the module's specific parameter"""
    global initialState, maxWordLength
    initialState = initialStateParam
    maxWordLength = maxWordLengthParam


def compute_reward_non_markovian(state1, state2, action):
    """this function computes if the non-markovian reward should be get for the given action and states. the current implementation gives the reward for cleaning a 
        stain right after moving up, i.e. nextState(@state1, "up") = @state2, and @action = "clean" , when @action is performed in @state2 """
    if action == "clean"  and (not state1 == None) and (not state1.hash == state2.hash) and state1.nextState("up").hash == state2.hash and state2.stateRoom[0] in state2.stateRoom[1]:
        return True
    return False


def convert_num_to_word(num):
    """
    converts @num to the @return word. the word is in sigma*
    :param num:
    :return:
    """
    word = ""
    while num:
        num, value = divmod(num, 6)
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


def learn_dfa():
    """computes an automaton from sets of words up to specific length. acception of a word is determined by the function 
       computeReward_NonMarkovian. current implementation assumes that there is a single accepting state, and for every
       accepted word, all words which this word is a prefix of them, are also accepted, because the reward was received
       in this sequence of actions/letters"""
    global initialState, maxWordLength
    sPlus = set()
    sMinus = set()
    counter = 0
    numOfWords = 0

    while counter < math.pow(6,maxWordLength): # in order to learn all words up to length wordLength, we need to iterate on all numbers up to pow(6,wordLength).
                                    # each number corresponds to a 'word' which is a series of actions.
        formerState = None
        currentState = initialState
        word = convert_num_to_word(counter)
        counter += 1
        if word == "" and counter > 1:
            continue
        numOfWords += 1
        wordToRead = word
        nonMarkovianReward = False

        while not (currentState.isEnd() or wordToRead == ""):  #assuming that the initial state is not an accepting state
            action = convert_letter_to_action(wordToRead[0:1])
            wordToRead = wordToRead[1:]
            nonMarkovianReward = nonMarkovianReward or compute_reward_non_markovian(formerState, currentState, action)
            formerState = copy.deepcopy(currentState)
            currentState = currentState.nextState(action)

        if nonMarkovianReward:
            sPlus.add(word)
        else:
            sMinus.add(word)
    dfa = Dfa.synthesize(sPlus, sMinus)
    return dfa