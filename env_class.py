import numpy as np


class Env(object):

    def __init__(self, real_world_init_state, simulated_state_init_state, action_space, reward_function, all_possible_states):
        """

        :param real_world_init_state:
        :param simulated_state_init_state:
        :param action_space:
        :param reward_function:
        :param all_possible_states:
        """
        self.real_init_state = real_world_init_state
        self.real_current_state = real_world_init_state
        self.simulated_current_state = simulated_state_init_state
        self.action_space = action_space
        self.reward_function = reward_function
        self.all_possible_states = all_possible_states

    def reset(self):
        """

        :return:
        """
        self.real_current_state = self.real_init_state
        self.simulated_current_state.reset()
        return self.simulated_current_state

    def sample_action_uniformly(self):
        """

        :return:
        """
        idx = None
        while idx is None:
            possible_idx = int(np.random.uniform(0, len(self.action_space) - 1, 1))
            if self.real_current_state.new_legal_op(self.action_space[possible_idx]):
                idx = possible_idx

        return self.action_space[idx]

    def step(self, action):
        """

        :param action:
        :return:
        """
        reward = self.reward_function(None, self.real_current_state, action)
        self.real_current_state, _ = self.real_current_state.next_state(action)
        obs = self.real_current_state.get_observation()
        self.simulated_current_state.next_state(action, obs)
        return self.simulated_current_state, reward, self.real_current_state.is_end()

    def action_from_idx(self, idx):
        return self.action_space[idx]

    def idx_from_action(self, action):
        return self.action_space.index(action)