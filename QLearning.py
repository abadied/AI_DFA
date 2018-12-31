import numpy as np
import random


class QLearningAlg(object):

    def __init__(self, alpha, n_episodes_param, epsilon, epsilon_min, decay_epsilon, discount_factor, max_steps, env):
        """

        :param alpha:
        :param n_episodes_param:
        :param epsilon:
        :param epsilon_min:
        :param decay_epsilon:
        :param discount_factor:
        :param max_steps:
        :param env:
        """
        self.alpha = alpha
        self.n_episodes = n_episodes_param
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.decay_epsilon = decay_epsilon
        self.discount_factor = discount_factor
        self.max_steps = max_steps
        self.env = env
        self.Q = None

    def q_learning_v2(self):
        """

        :return:
        """
        self.Q = np.zeros([len(self.env.all_possible_states), len(self.env.action_space)])
        experiment_epsilon = self.epsilon
        for episode in range(self.n_episodes):
            curr_rewards = 0
            curr_observation = self.env.reset()
            for current_step in range(self.max_steps):
                curr_observation_idx = self.env.all_possible_states.index(curr_observation.get_state_key())
                # pick an action in e-greedly manner
                if random.uniform(0, 1) < max(experiment_epsilon, self.epsilon_min):
                    action = self.env.sample_action_uniformly()  # random action sampled uniformly
                    action_idx = self.env.idx_from_action(action)
                else:
                    action_idx = np.argmax(self.Q[curr_observation_idx, :])  # best action according to q function, Q is a matrix of states on actions
                    action = self.env.action_from_idx(action_idx)
                # take an action and update the Q function
                next_observation, reward, done = self.env.step(action)  # new state from the enviorment
                next_observation_state_idx = self.env.all_possible_states.index(next_observation.get_state_key())

                if done:
                    target = reward
                    self.Q[curr_observation_idx, action_idx] = (1 - self.alpha) * self.Q[curr_observation_idx, action_idx] + self.alpha * target
                    curr_rewards += reward
                    # current_observation = env.reset()
                    break
                else:
                    target = reward + self.discount_factor * np.max(self.Q[next_observation_state_idx, :])
                    self.Q[curr_observation_idx, action_idx] = (1 - self.alpha) * self.Q[curr_observation_idx, action_idx] + self.alpha * target  # update state action field
                    curr_observation = next_observation

                experiment_epsilon = experiment_epsilon * self.decay_epsilon

    def get_policy(self):
        """

        :return:
        """
        if self.Q is None:
            return None

        policy = {}

        for i in range(len(self.Q)):
            policy[str(self.env.all_possible_states[i])] = self.env.action_space[np.argmax(self.Q[i])]

        return policy