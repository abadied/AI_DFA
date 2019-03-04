import Board
import numpy as np
import math
from itertools import product
import Constants
import copy
import random
FINAL_STATES = []


def opening_print(all_states, room, print_room):
    """
    a recommended print of the room and number of states, to be able to follow the game flow
    :param all_states:
    :param room:
    :param print_room:
    :return:
    """
    print("room representation: ")
    print_room(room)
    # print("number of states: ", len(list(all_states.keys())))


def get_all_states_impl(current_state, all_states, ops):
    """
    recursive function to get all states starting from @currentState using the actions in @ops
    :param current_state:
    :param all_states:
    :param ops:
    :return:
    """
    # TODO: check!
    global FINAL_STATES
    for i in ops:
        if current_state.new_legal_op(i):
            new_state = current_state.next_state(i)
            if new_state.hash not in all_states.keys():  # maybe it's better to use hash function in order to construct allStates
                all_states[new_state.hash] = new_state
                if not new_state.is_end():
                    get_all_states_impl(new_state, all_states, ops)
                else:
                    FINAL_STATES.append(new_state.hash)


def get_all_states(initial_state, ops):
    """
    returns all states starting from @initialState using the actions in @ops
    :param initial_state:
    :param ops:
    :return:
    """
    all_states = dict()
    all_states[initial_state.hash] = initial_state
    get_all_states_impl(initial_state, all_states, ops)
    return all_states


def compute_reward(allStates, state, action):
    """
    computes reward for a state&action pair. returns positive reward only for ending the game
    :param allStates:
    :param state:
    :param action:
    :return:
    """
    if not state.is_end() and state.next_state(action).is_end():
        return Board.FINISHING_CREDIT
    return -Board.MOVE_COST


# using another reward function would give different results, for example the following function:
def compute_reward_2(allStates, state, action):
    """computes reward for a state&action pair. returns positive reward for every action that makes progress in the game.
    this function computes the reward of an action given that the robot succeeded to make it"""
    if action == "clean" and state.state_room[0] in state.state_room[1]:
        return Board.CLEANING_CREDIT
    elif action == "pick" and state.state_room[0] in state.state_room[2]:
        return Board.PICKING_CREDIT
    elif action == "putInBasket":
        return Board.PUTTING_CREDIT * state.state_room[3]
    return 0


def compute_reward_by_type(state, action, type):
    if type == 'end':
        if not state.is_end() and state.next_state(action).is_end():
            return Board.FINISHING_CREDIT

    elif type == 'clean':
        if action == "clean" and state.state_room[0] in state.state_room[1]:
            return Board.CLEANING_CREDIT
    elif type == 'pick':
        if action == "pick" and state.state_room[0] in state.state_room[2]:
            return Board.PICKING_CREDIT
    elif type == 'putInBasket':
        if action == "putInBasket" and state.state_room[3] > 0 and state.state_room[0] == Board.BASKET_POSITION:
            return Board.PUTTING_CREDIT * state.state_room[3]
    return 0


def create_initial_policy(all_states):
    """
    initializing a policy that selects a random action for all states (except final ones)
    :param all_states:
    :return:
    """
    
    policy = dict()
    for key in all_states.keys():
        policy[key] = "random"
        if all_states[key].is_end():
            policy[key] = "idle"
    return policy


def create_state_value_dictionary(all_states):
    """
    initial state value - 0 for all states
    :param all_states:
    :return:
    """
    state_value = dict()
    for key in all_states.keys():
        state_value[key] = 0.
    return state_value


def create_state_value_dictionary_auto(all_states):
    """
    initial state value - 0 for all states
    :param all_states:
    :return:
    """
    state_value = dict()
    for key in all_states:
        state_value[str(key)] = 0.
    return state_value


def expected_return(all_states, state_key, action, state_value, ops, compute_reward_function):
    """computes the expected discounted return from @allStates[@stateKey] using @action, and according the 
       current @stateValue dictionary"""
    # initailize total return
    returns = 0.0
    returns -= Board.MOVE_COST

    for i in range(len(ops)):
        prob = Board.TRAN_PROB_MAT[ops.index(action)][i]
        real_action = ops[i]
        if all_states[state_key].new_legal_op(real_action):
            newState = all_states[state_key].next_state(real_action)
            reward = float(compute_reward_function(all_states, all_states[state_key], real_action))
            returns += prob * (reward + Board.DISCOUNT * state_value[newState.hash])
        elif not all_states[state_key].is_end():
            returns += prob * Board.DISCOUNT * state_value[state_key]
        else:
            returns = 100
    return returns


# def expected_return_automatas(auto_state, state_key, action):
#     """computes the expected discounted return from @allStates[@stateKey] using @action, and according the
#        current @stateValue dictionary"""
#     # initailize total return
#     returns = 0.0
#     returns -= Board.MOVE_COST
#     curr_auto_state = state_key
#     new_auto_state = copy.deepcopy(auto_state)
#     reward = 0
#     # need to find common possible observations and multiply by their probability with the optional score
#     new_auto_state[dfa_counter] = list(dfa_dict[dfa_key]['dfa'].evalSymbol(curr_auto_state[dfa_counter], Constants.value_letter_dictionary[action]))[0]
#     dfa_counter += 1
#
#     observations = get_states_intersection(new_auto_state, dfa_dict, Constants.OBS)
#
#     for obs in observations:
#         dfa_counter = 0
#         for dfa_key in dfa_dict.keys():
#             curr_dfa = dfa_dict[dfa_key]
#             try:
#                 new_auto_state_observation = curr_dfa['dfa'].evalSymbol(new_auto_state[dfa_counter], Constants.value_letter_dictionary[obs])
#                 new_auto_state[dfa_counter] = new_auto_state_observation
#             except NameError as e:
#                 # TODO: in case the letter is doesnt belong to the automata sigma - fix
#                 pass
#             if new_auto_state[dfa_counter] in dfa_dict[dfa_key]['dfa'].Final or new_auto_state[dfa_counter] in dfa_dict[dfa_key]['dfa'].Final:
#                 try:
#                     # TODO: throws key error exceptions on curr_dfa['dfa'].delta[curr_auto_state[dfa_counter]] - fix
#                     reward += curr_dfa['dfa'].delta[curr_auto_state[dfa_counter]][Constants.value_letter_dictionary[obs] + '_counter'] * dfa_dict[dfa_key]['reward']
#                 except:
#                     reward += dfa_dict[dfa_key]['reward']
#             dfa_counter += 1
#
#         returns += (reward + Board.DISCOUNT * state_value[str(new_auto_state)])
#
#     return returns


def get_prob_sas(state1, state2, action):
    """"given state1 and action, returns the probability to reach state2
        in case that action is 'random' the function returns -1
        if state1 is a final state, than it leads by any action to itself in probability 1"""
    if action == 'random':
        return -1.0
    action_index = Board.OPS.index(action)
    possible_actions_indices = [numOp for numOp in range(len(Board.OPS)) if Board.TRAN_PROB_MAT[action_index][numOp] > 0]
    sum = 0.0
    for numOp in possible_actions_indices:
        if state1.actualNextState(Board.OPS[numOp]).hash == state2.hash:
            sum += Board.TRAN_PROB_MAT[action_index][numOp]
    return sum


def get_reward_sa(all_states, state, action, reward_function):
    """
    given an action, returns expectation of the reward for applying @action in @self according the given @rewardFunction.
    :param all_states:
    :param state:
    :param action:
    :param reward_function:
    :return:
    """
    expected_reward = 0.
    action_index = Board.OPS.index(action)
    for op in Board.OPS:
        op_index = Board.OPS.index(op)
        expected_reward += Board.TRAN_PROB_MAT[action_index][op_index] * reward_function(all_states, state, op)
    return expected_reward


def compute_actual_action(action_chosen, current_state):
    """
    computing the actual action that was taken when choosing @actionChosen in @currentState.
    :param action_chosen:
    :param current_state:
    :return:
    """
    action_index = Board.OPS.index(action_chosen)
    sample = np.random.uniform(0.000000001, 1.)
    sum_prob = 0
    for i in range(len(Board.OPS)):
        sum_prob += Board.TRAN_PROB_MAT[action_index][i]
        if sum_prob > sample:
            real_action_index = i
            break
    real_action = Board.OPS[real_action_index]
    if not current_state.new_legal_op(real_action):
        real_action = "idle"
    return real_action


def create_possible_ops_dict(state):
    possible_ops_dict = {}
    for _op in state.get_possible_actions():
        possible_ops_dict[_op] = 0

    return possible_ops_dict


def get_least_common_op(possible_actions_dict: dict):
    # TODO: returns the same action each time for every simulation
    min_val = math.inf
    op = None
    for _op in possible_actions_dict.keys():
        if possible_actions_dict[_op] < min_val:
            min_val = possible_actions_dict[_op]
            op = _op
    possible_actions_dict[op] += 1
    return op


def get_random_op(possible_actions_dict: dict):
    possible_ops_list = list(possible_actions_dict.keys())
    rand_idx = random.randint(0, len(possible_ops_list) - 1)
    return possible_ops_list[rand_idx]


def get_all_automatas_states(dfa_dict: dict, observables: list = list()):
    """
    returns a list of integers from 0 to the highest number represented by the automatas states
    for example - if there are 3, 2 and 2 state for the respective automatas then a list from 0 to 322 will be the output.
    :param dfa_dict:
    :param observables:
    :return: list
    """
    state_lengths = []
    for obs in observables:
        state_lengths.append(obs)

    for dfa_key in dfa_dict:
        state_lengths.append(list(range(dfa_dict[dfa_key]['dfa'].state_count())))

    all_auto_states = list(product(*state_lengths))
    all_auto_states = list(map(lambda x: list(x), all_auto_states))
    return all_auto_states


def get_states_intersection(states_list: list, dfa_dict: dict, options_list: list):
    """
    for a given state list, a dfa dictionary and an operation lists this function will return the possible operations
    for all automatas in the dictionary from current states
    :param states_list: list of current automatas states
    :param dfa_dict: dictionary of all automatas
    :param options_list: list of possible operations/observations
    :return: set of possible operations/observations
    """
    possible_ops = set()
    for op in options_list:
        is_possible = True
        state_idx = 0
        op_letter = Constants.value_letter_dictionary[op]
        for dfa_key in dfa_dict.keys():
            try:
                curr_auto_state = states_list[state_idx]
                keys_list = list(dfa_dict[dfa_key]['dfa'].delta[curr_auto_state].keys())
                if op_letter not in keys_list:
                    is_possible = False
            except Exception as e:
                is_possible = False
            state_idx += 1
        if is_possible:
            possible_ops.add(op)

    return possible_ops
