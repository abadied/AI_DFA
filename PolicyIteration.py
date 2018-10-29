import numpy as np
import StateGenericFunctions

policy = 0
all_states = 0
ops = 0
computeRewardFunction = 0


def init_module(policy_param, all_states_param, ops_param, compute_reward_function_param):
    """
    initializes the module's specific parameters
    :param policy_param:
    :param all_states_param:
    :param ops_param:
    :param compute_reward_function_param:
    :return:
    """
    global policy, all_states, ops, computeRewardFunction
    policy = policy_param
    all_states = all_states_param
    ops = ops_param
    computeRewardFunction = compute_reward_function_param


def compute_reward_policy_iteration(_all_states, state, action):
    return StateGenericFunctions.compute_reward(_all_states, state, action)

# TODO: change to work on automata states
def policy_iteration():
    """
    Policy Iteration main function
    :return:
    """
    global policy, all_states, ops, computeRewardFunction
    new_state_value = dict()
    for key in all_states.keys():
        new_state_value[key] = 0
    policy_improvement_ind = 0
    state_value = StateGenericFunctions.create_state_value_dictionary(all_states)
    while True:  # iterating on policies
        for stateKey in all_states.keys():  # applying bellman equation for all states
            new_state_value[stateKey] = StateGenericFunctions.expected_return(all_states, stateKey, policy[stateKey], state_value, ops, computeRewardFunction)
        sum = 0
        for stateKey in all_states.keys():
            sum += np.abs(new_state_value[stateKey] - state_value[stateKey])
        for key in state_value:
            state_value[key] = new_state_value[key]

        if sum < 1e-2: # evaluation converged
            policy_improvement_ind += 1
            new_policy = dict()
            for stateKey in all_states.keys():
                action_returns = []
                # go through all actions and select the best one
                for op in ops:
                    if all_states[stateKey].legal_op(op):
                        action_returns.append(
                            StateGenericFunctions.expected_return(all_states, stateKey, op, state_value, ops, computeRewardFunction))
                    else:
                        action_returns.append(-float('inf'))
                best_action = np.argmax(action_returns)
                new_policy[stateKey] = ops[best_action]
                policy_changes = 0
            for key in policy.keys():
                if new_policy[key] != policy[key]:
                    policy_changes += 1
            print("changed policy #", policy_improvement_ind, " and num of changes is: ", policy_changes)
            if policy_changes == 0:
                break
            policy = new_policy
    return policy
