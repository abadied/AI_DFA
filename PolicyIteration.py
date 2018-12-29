import numpy as np
import StateGenericFunctions

policy = 0
all_states = 0
ops = 0
computeRewardFunction = 0


class PolicyIteration(object):

    def __init__(self, policy_param, all_states_param, ops_param, transition_matrix, accepting_states):
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
        self.transition_matrix = transition_matrix
        self.accepting_states = accepting_states
        self.value_func = None

    @staticmethod
    def compute_reward_policy_iteration(_all_states, state, action):
        return StateGenericFunctions.compute_reward(_all_states, state, action)

    # def policy_iteration_with_auto_new(self):
    #     # TODO: cahange to get in init all the transition matrix for every action, change the policy iteration to work
    #     # TODO: the same as in mdp - compute according to the transition function on the new state, reward will
    #     # TODO: be given if the automata state is an accepting one.
    #     """
    #     Policy Iteration main function
    #     :return:
    #     """
    #     policy_improvement_ind = 0
    #     new_state_value = StateGenericFunctions.create_state_value_dictionary_auto(self.all_states)
    #     state_value = StateGenericFunctions.create_state_value_dictionary_auto(self.all_states)
    #     while True:  # iterating on policies
    #         for stateKey in self.all_states:  # applying bellman equation for all states
    #             new_state_value[str(stateKey)] = StateGenericFunctions.expected_return_automatas(self.initial_auto_state,
    #                                                                                              self.policy[str(stateKey)],
    #                                                                                              state_value)
    #         sum = 0
    #         # summarize the improvement in the value function
    #         for stateKey in self.all_states:
    #             sum += np.abs(new_state_value[str(stateKey)] - state_value[str(stateKey)])
    #         # update new values
    #         for key in state_value:
    #             state_value[key] = new_state_value[key]
    #
    #         # update new policy
    #         if sum < 1e-2: # evaluation converged
    #             policy_improvement_ind += 1
    #             new_policy = dict()
    #             for stateKey in self.all_states:
    #                 action_returns = []
    #                 # go through all actions and select the best one
    #                 possible_ops = StateGenericFunctions.get_states_intersection(stateKey, self.dfa_dict, self.ops)
    #                 if len(possible_ops) > 0:
    #                     for op in possible_ops:
    #                         if self.all_states[stateKey].legal_op(op):
    #                             action_returns.append(
    #                                 StateGenericFunctions.expected_return_automatas(self.dfa_dict, stateKey, op, state_value))
    #                         else:
    #                             action_returns.append(-float('inf'))
    #                     best_action = np.argmax(action_returns)
    #                     new_policy[stateKey] = self.ops[best_action]
    #                     policy_changes = 0
    #
    #             # check how many actions have changed
    #             for key in self.policy.keys():
    #                 if new_policy[key] != self.policy[key]:
    #                     policy_changes += 1
    #             print("changed policy #", policy_improvement_ind, " and num of changes is: ", policy_changes)
    #             if policy_changes == 0:
    #                 break
    #             self.policy = new_policy
    #     return self.policy

    def compute_expected_reward(self, state, action):
        """

        :param state:
        :param action:
        :return:
        """
        reward = 0
        action_tran_matrix = self.transition_matrix[action]
        for next_state in self.all_states:
            tran_prob = action_tran_matrix[state][next_state]
            if tran_prob > 0:
                for automata_loc in self.accepting_states.keys():
                    if next_state[automata_loc] in self.accepting_states[automata_loc]['states']:
                        reward += self.accepting_states[automata_loc]['reward'] * tran_prob
        return reward

    def policy_iteration(self, epsilon=0.01, gamma=0.9):
        """
        This function simulate policy iteration over this set of states(allStates) and return a proper policy
        :param epsilon: 0.01
        :param gamma: 0.9
        :return: best policy according to gamma and epsilon
        """
        while True:
            change = False
            self.set_value_function(epsilon=epsilon, gamma=gamma)
            for state in self.all_states:
                possible_states = self.get_possible_states(state)
                max_change = 0
                max_op = None
                for op in self.ops:
                    if op != self.policy[state] and state.legalOp(op):
                        action_reward = self.compute_expected_reward(state, op)
                        sigma_param = 0
                        for next_state in possible_states:
                            sigma_param += self.transition_matrix[op][state][next_state] * self.value_func[next_state]
                        curr_reward = action_reward + gamma * sigma_param
                        curr_change = curr_reward - self.value_func[state]
                        if curr_change > max_change:
                            max_change = curr_change
                            max_op = op

                if max_change > 0:
                    self.policy[state] = max_op
                    self.value_func[state] += max_change
                    change = True

            if not change:
                break
        return self.policy

    def set_value_function(self, epsilon=0.01, gamma=0.9):
        """
        This function finds the matching value function the the given policy according to gamma and epsilon
        :param epsilon: 0.01
        :param gamma: 0.9
        :return: a value function matching the given policy
        """
        if self.value_func is None:
            value_func = dict()
            for key in self.all_states:
                value_func[key] = 0

        while True:
            changed = False
            for curr_state in self.all_states:
                action = self.policy[curr_state]
                sigma_param = 0
                action_reward = self.compute_expected_reward(curr_state, action)
                possible_states = self.get_possible_states(curr_state)
                for next_state in possible_states:
                    sigma_param += self.transition_matrix[action][curr_state][next_state] * value_func[next_state]
                curr_reward = action_reward + gamma * sigma_param
                value_func[curr_state] = curr_reward
                if abs(curr_reward - value_func[curr_state]) >= epsilon:
                    changed = True
            if not changed:
                break

    def get_possible_states(self, state):
        """

        :param state:
        :return:
        """
        possible_states = []
        for tran_mat in self.transition_matrix:
            for next_state in self.all_states:
                if tran_mat[state][next_state] > 0:
                    possible_states.append(next_state)
        return possible_states

