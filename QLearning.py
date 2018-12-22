import numpy as np
import StateGenericFunctions
import pyqlearning.qlearning.greedy_q_learning

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


class QLearning(object):

    def __init__(self, policy_param, state_action_values_param, explore_rate_param, n_episodes_param, ops_param,
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
        self.policy = policy_param
        self.stateActionValues = state_action_values_param
        self.exploreRate = explore_rate_param
        self.nEpisodes = n_episodes_param
        self.ops = ops_param
        self.tran_prob_mat = tran_prob_mat_param
        self.stepSize = step_size_param
        self.discount = discount_param
        self.initialState = initial_state_param
        self.allStates = all_states_param


    def compute_reward_q_learning(self, type, state, action):
        return StateGenericFunctions.compute_reward_by_type(state, action, type)


    def choose_action(self, state, state_action_values):
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


    def compute_best_action(self, state):
        optional_actions = list(stateActionValues[state.hash].keys())
        best_action = optional_actions[0]
        for op in optional_actions:
            if stateActionValues[state.hash][op] > stateActionValues[state.hash][best_action]:
                best_action = op
        return best_action


    def q_learning(self):
        """
        Q-Learning main function
        :return:
        """
        global  stateActionValues
        print("num of trials ", self.nEpisodes)
        for i in range(1,  self.nEpisodes):
            if i % 200 == 0:
                print("trial number ", i)
            current_state = initial_state
            while not current_state.is_end():

                # choosing an action to make according the current values of state-action pairs (and exploring rate, of course)
                current_action = choose_action(current_state,  self.stateActionValues)

                real_action = StateGenericFunctions.compute_actual_action(current_action, current_state)
                reward = compute_reward_q_learning(all_states, current_state, real_action)
                new_state = current_state.next_state(real_action)

                # Q-Learning update
                optional_actions = list( self.stateActionValues[new_state.hash].keys())
                best_action = optional_actions[0]
                for op in optional_actions:
                    if  self.stateActionValues[new_state.hash][op] > stateActionValues[new_state.hash][best_action]:
                        best_action = op
                self.stateActionValues[current_state.hash][current_action] += stepSize * (
                    reward + discount * self.stateActionValues[new_state.hash][best_action] -
                    self.stateActionValues[current_state.hash][current_action])
                policy[current_state.hash] = compute_best_action(current_state)
                current_state = new_state
        return policy
