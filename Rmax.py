import numpy as np

import StateGenericFunctions

all_states = 0
current_state = 0
ops = 0
tran_prob_mat = 0
moves=0
state_actions_r_max = 0
state_actions_counter = 0
discount = 0
initial_state = 0
time_until_known = 0


def init_module(all_states_param, initial_state_param, ops_param, tran_prob_mat_param, state_actions_r_max_param,
                state_actions_counter_param, discount_param, time_until_known_param):
    """
    initializes the module's specific parameters
    :param all_states_param:
    :param initial_state_param:
    :param ops_param:
    :param tran_prob_mat_param:
    :param state_actions_r_max_param:
    :param state_actions_counter_param:
    :param discount_param:
    :param time_until_known_param:
    :return:
    """
    global all_states, current_state, ops, tran_prob_mat, state_actions_r_max, state_actions_counter, discount, initial_state, time_until_known
    allStates = all_states_param
    initialState = initial_state_param
    ops = ops_param
    tran_prob_mat = tran_prob_mat_param
    state_actions_r_max = state_actions_r_max_param
    state_actions_counter = state_actions_counter_param
    discount = discount_param
    time_until_known = time_until_known_param


def compute_best_action_r_max(state_key):
    """
    givean a state, returns the best action to do in it according present knowledge (values in stateActionsRmax dictionary
    :param state_key:
    :return:
    """
    global state_actions_r_max
    optional_actions = list(state_actions_r_max[state_key].keys())
    best_action = optional_actions[0]
    for op in optional_actions:
        if state_actions_r_max[state_key][op]["value"] > state_actions_r_max[state_key][best_action]["value"]:
            best_action = op
    return best_action


def r_max_impl():
    """
    Rmax main function
    :return:
    """
    global state_actions_r_max, state_actions_counter, moves, ops, tran_prob_mat, discount, current_state, all_states,\
        initial_state, time_until_known

    print("num of state action pairs: ", state_actions_counter)
    state_actions_rmax_temp = state_actions_r_max
    counter_known_states = 0
    while counter_known_states < state_actions_counter:
        current_state = initial_state
        while True:
            moves += 1
            # computing best action to take
            best_action = compute_best_action_r_max(current_state.hash)
            state_actions_r_max[current_state.hash][best_action]["totalVisits"] += 1.

            real_action = StateGenericFunctions.compute_actual_action(best_action, current_state)

            # updates
            reward = state_actions_r_max[current_state.hash][best_action]["legalActions"][real_action]["reward"] =\
                StateGenericFunctions.compute_reward(all_states, current_state, real_action)

            state_actions_r_max[current_state.hash][best_action]["legalActions"][real_action]["counterSpecificOp"] += 1.
            if state_actions_r_max[current_state.hash][best_action]["totalVisits"] == time_until_known:

                state_actions_r_max[current_state.hash][best_action]["known"] = True
                counter_known_states += 1

                if counter_known_states % 50 == 0:
                    print("num of pairs found ", counter_known_states)

                for action in state_actions_r_max[current_state.hash][best_action]["legalActions"].keys():  # when a state-action pair becomes known, we know all transitions
                    state_actions_r_max[current_state.hash][best_action]["legalActions"][action]["nextState"] = current_state.next_state(action).hash

                while True:     # policy evaluation
                    new_state_action_value = dict()
                    for stateKey in all_states.keys():
                        new_state_action_value[stateKey] = dict()
                        for action in state_actions_r_max[stateKey]: # applying bellman equation for state-action pairs
                            new_state_action_value[stateKey][action] = 0
                            if not state_actions_r_max[stateKey][action]["totalVisits"] == 0:
                                for legal_action in state_actions_r_max[stateKey][action]["legalActions"]:
                                    prob = state_actions_r_max[stateKey][action]["legalActions"][legal_action]["counterSpecificOp"] / state_actions_r_max[stateKey][action]["totalVisits"]
                                    next_state = state_actions_r_max[stateKey][action]["legalActions"][legal_action]["nextState"]  # that's a string

                                    #computing next state value (for the best action taken in it)
                                    next_state_value = -float('Inf')
                                    for possibleAction in state_actions_r_max[next_state].keys():
                                        if state_actions_r_max[next_state][possibleAction]["value"] > next_state_value:
                                            next_state_value = state_actions_r_max[next_state][possibleAction]["value"]
                                    new_state_action_value[stateKey][action] += prob * (state_actions_r_max[stateKey][action][
                                                                                         "legalActions"][legal_action]["reward"] + discount * next_state_value)
                            else:
                                new_state_action_value[stateKey][action] = state_actions_r_max[stateKey][action]["value"]
                    sum = 0
                    for stateKey in all_states.keys():
                        for action in new_state_action_value[stateKey]:
                            sum += np.abs(state_actions_r_max[stateKey][action]["value"] - new_state_action_value[stateKey][action])
                    for stateKey in all_states.keys():
                        for action in new_state_action_value[stateKey]:
                            state_actions_r_max[stateKey][action]["value"] = new_state_action_value[stateKey][action]
                    if sum < 1:
                        break
            if current_state.is_end():
                break
            current_state = current_state.next_state(real_action)
    policy = dict()
    for stateKey in all_states.keys():
        policy[stateKey] = compute_best_action_r_max(stateKey)
    return policy