import numpy as np
import StateGenericFunctions

policy = 0
all_states = 0
ops = 0
computeRewardFunction = 0


class PolicyIteration(object):

    def __init__(self, policy_param, all_states_param, ops_param, compute_reward_function_param):
        """
        initializes the module's specific parameters
        :param policy_param:
        :param all_states_param:
        :param ops_param:
        :param compute_reward_function_param:
        :return:
        """
        self.policy = policy_param
        self.all_states = all_states_param
        self.ops = ops_param
        self.compute_reward_function = compute_reward_function_param

    @staticmethod
    def compute_reward_policy_iteration(_all_states, state, action):
        return StateGenericFunctions.compute_reward(_all_states, state, action)

    # # TODO: change to work on automata states
    # def policy_iteration(self):
    #     """
    #     Policy Iteration main function
    #     :return:
    #     """
    #     new_state_value = dict()
    #     for key in all_states.keys():
    #         new_state_value[key] = 0
    #     policy_improvement_ind = 0
    #     state_value = StateGenericFunctions.create_state_value_dictionary(all_states)
    #     while True:  # iterating on policies
    #         for stateKey in all_states.keys():  # applying bellman equation for all states
    #             new_state_value[stateKey] = StateGenericFunctions.expected_return(all_states, stateKey, policy[stateKey], state_value, ops, computeRewardFunction)
    #         sum = 0
    #         for stateKey in all_states.keys():
    #             sum += np.abs(new_state_value[stateKey] - state_value[stateKey])
    #         for key in state_value:
    #             state_value[key] = new_state_value[key]
    #
    #         if sum < 1e-2: # evaluation converged
    #             policy_improvement_ind += 1
    #             new_policy = dict()
    #             for stateKey in all_states.keys():
    #                 action_returns = []
    #                 # go through all actions and select the best one
    #                 for op in ops:
    #                     if all_states[stateKey].legal_op(op):
    #                         action_returns.append(
    #                             StateGenericFunctions.expected_return(all_states, stateKey, op, state_value, ops, computeRewardFunction))
    #                     else:
    #                         action_returns.append(-float('inf'))
    #                 best_action = np.argmax(action_returns)
    #                 new_policy[stateKey] = ops[best_action]
    #                 policy_changes = 0
    #             for key in policy.keys():
    #                 if new_policy[key] != policy[key]:
    #                     policy_changes += 1
    #             print("changed policy #", policy_improvement_ind, " and num of changes is: ", policy_changes)
    #             if policy_changes == 0:
    #                 break
    #             policy = new_policy
    #     return policy

    def policy_iteration_with_auto(self):
        """
        Policy Iteration main function
        :return:
        """
        policy_improvement_ind = 0
        new_state_value = StateGenericFunctions.create_state_value_dictionary_auto(all_states)
        state_value = StateGenericFunctions.create_state_value_dictionary_auto(all_states)
        while True:  # iterating on policies
            for stateKey in self.all_states:  # applying bellman equation for all states
                new_state_value[stateKey] = StateGenericFunctions.expected_return(self.all_states, stateKey, self.policy[stateKey], state_value, self.ops, self.compute_reward_function)
            sum = 0
            for stateKey in self.all_states:
                sum += np.abs(new_state_value[stateKey] - state_value[stateKey])
            for key in state_value:
                state_value[key] = new_state_value[key]

            if sum < 1e-2: # evaluation converged
                policy_improvement_ind += 1
                new_policy = dict()
                for stateKey in self.all_states:
                    action_returns = []
                    # go through all actions and select the best one
                    for op in self.ops:
                        if self.all_states[stateKey].legal_op(op):
                            action_returns.append(
                                StateGenericFunctions.expected_return(self.all_states, stateKey, op, state_value, self.ops, self.compute_reward_function))
                        else:
                            action_returns.append(-float('inf'))
                    best_action = np.argmax(action_returns)
                    new_policy[stateKey] = self.ops[best_action]
                    policy_changes = 0
                for key in self.policy.keys():
                    if new_policy[key] != self.policy[key]:
                        policy_changes += 1
                print("changed policy #", policy_improvement_ind, " and num of changes is: ", policy_changes)
                if policy_changes == 0:
                    break
                self.policy = new_policy
        return self.policy
