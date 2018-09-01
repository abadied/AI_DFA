import numpy as np
import StateGenericFunctions

policy = 0
stateActionValues = 0
exploreRate = 0
nEpisodes = 0
ops = 0
tran_prob_mat = 0
stepSize = 0
discount = 0
initial_state = 0
all_states = 0


def init_module(policy_param, state_action_values_param, explore_rate_param, n_episodes_param, ops_param,
                tran_prob_mat_param, step_size_param, discount_param, initial_state_param, all_states_param):
    """
    initializes the module's specific parameters
    :param policy_param:
    :param state_action_values_param:
    :param explore_rate_param:
    :param n_episodes_param:
    :param ops_param:
    :param tran_prob_mat_param:
    :param step_size_param:
    :param discount_param:
    :param initial_state_param:
    :param all_states_param:
    :return:
    """
    global policy, stateActionValues, exploreRate, nEpisodes, ops, tran_prob_mat, stepSize, discount, initial_state
    policy = policy_param
    stateActionValues = state_action_values_param
    exploreRate = explore_rate_param
    nEpisodes = n_episodes_param
    ops = ops_param
    tran_prob_mat = tran_prob_mat_param
    stepSize = step_size_param
    discount = discount_param
    initialState = initial_state_param
    allStates = all_states_param


def compute_reward_q_learning(_all_states, state, action):
    return StateGenericFunctions.compute_reward(_all_states, state, action)


def choose_action(state, state_action_values):
    """
    choose an action based on epsilon greedy algorithm
    :param state:
    :param state_action_values:
    :return:
    """
    optional_actions = state_action_values[state.hash].keys()
    optional_actions = [op for op in optional_actions if not op == "random"]
    if np.random.binomial(1, exploreRate) == 1:
        # in this case we need to choose an action from the legal ones
        return np.random.choice(optional_actions)
    else:
        # choose the best action according to values we have at this point from state-action dict
        best_action = optional_actions[0]
        for op in optional_actions:
            if state_action_values[state.hash][op] > state_action_values[state.hash][best_action]:
                best_action = op
        return best_action


def compute_best_action(state):
    optional_actions = list(stateActionValues[state.hash].keys())
    best_action = optional_actions[0]
    for op in optional_actions:
        if stateActionValues[state.hash][op] > stateActionValues[state.hash][best_action]:
            best_action = op
    return best_action


def q_learning():
    """
    Q-Learning main function
    :return:
    """
    global policy, stateActionValues, initial_state, nEpisodes
    print("num of trials ", nEpisodes)
    for i in range(1, nEpisodes):
        if i % 200 == 0:
            print("trial number ", i)
        current_state = initial_state
        while not current_state.is_end():

            # choosing an action to make according the current values of state-action pairs (and exploring rate, of course)
            current_action = choose_action(current_state, stateActionValues)

            real_action = StateGenericFunctions.compute_actual_action(current_action, current_state)
            reward = compute_reward_q_learning(all_states, current_state, real_action)
            new_state = current_state.next_state(real_action)

            # Q-Learning update
            optional_actions = list(stateActionValues[new_state.hash].keys())
            best_action = optional_actions[0]
            for op in optional_actions:
                if stateActionValues[new_state.hash][op] > stateActionValues[new_state.hash][best_action]:
                    best_action = op
            stateActionValues[current_state.hash][current_action] += stepSize * (
                reward + discount * stateActionValues[new_state.hash][best_action] -
                stateActionValues[current_state.hash][current_action])
            policy[current_state.hash] = compute_best_action(current_state)
            current_state = new_state
    return policy
