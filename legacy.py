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
    new_state_value = StateGenericFunctions.create_state_value_dictionary_auto(self.all_states)
    state_value = StateGenericFunctions.create_state_value_dictionary_auto(self.all_states)
    while True:  # iterating on policies
        for stateKey in self.all_states:  # applying bellman equation for all states
            new_state_value[str(stateKey)] = StateGenericFunctions.expected_return_automatas(self.dfa_dict, stateKey,
                                                                                             self.policy[str(stateKey)],
                                                                                             state_value)
        sum = 0
        # summarize the improvement in the value function
        for stateKey in self.all_states:
            sum += np.abs(new_state_value[str(stateKey)] - state_value[str(stateKey)])
        # update new values
        for key in state_value:
            state_value[key] = new_state_value[key]

        # update new policy
        if sum < 1e-2:  # evaluation converged
            policy_improvement_ind += 1
            new_policy = dict()
            for stateKey in self.all_states:
                action_returns = []
                # go through all actions and select the best one
                possible_ops = StateGenericFunctions.get_states_intersection(stateKey, self.dfa_dict, self.ops)
                if len(possible_ops) > 0:
                    for op in possible_ops:
                        if self.all_states[stateKey].legal_op(op):
                            action_returns.append(
                                StateGenericFunctions.expected_return_automatas(self.dfa_dict, stateKey, op,
                                                                                state_value))
                        else:
                            action_returns.append(-float('inf'))
                    best_action = np.argmax(action_returns)
                    new_policy[stateKey] = self.ops[best_action]
                    policy_changes = 0

            # check how many actions have changed
            for key in self.policy.keys():
                if new_policy[key] != self.policy[key]:
                    policy_changes += 1
            print("changed policy #", policy_improvement_ind, " and num of changes is: ", policy_changes)
            if policy_changes == 0:
                break
            self.policy = new_policy
    return self.policy



########
# Rmax #
########
if chosen_algorithm == 'r_max':
    print("Running Rmax")
    StateGenericFunctions.opening_print(all_states, room, print_room)
    maxReward = max(CLEANING_CREDIT, PICKING_CREDIT, PUTTING_CREDIT, FINISHING_CREDIT)
    maxValue = 1. / (1. - DISCOUNT) * maxReward
    state_actions_r_max = dict()
    state_actions_r_max["heaven"] = dict()
    state_actions_r_max["heaven"]["idle"] = {"reward" : maxReward, "value" : maxValue}
    state_actions_counter = 0             # used for stop condition- this is the maximal number of "known" states
    for stateKey in all_states.keys():
        state_actions_r_max[stateKey] = dict()
        for action in OPS:
            if all_states[stateKey].legal_op(action):
                state_actions_r_max[stateKey][action] = {"known" : False, "totalVisits" : 0. , "value" : maxValue, "legalActions" : dict()}
                state_actions_counter += 1
                for realAction in OPS:
                    if all_states[stateKey].legal_op(realAction):
                        state_actions_r_max[stateKey][action]["legalActions"][realAction] = {"counterSpecificOp" : 0. , "reward" : maxReward, "nextState" : "heaven"}
    time_until_known = 10
    Rmax.init_module(all_states, State(), OPS, TRAN_PROB_MAT, state_actions_r_max, state_actions_counter, DISCOUNT, time_until_known)
    policy = Rmax.r_max_impl()

    # def add_probabilities_to_auto_dict(dfa_dict: dict):
    #     for dfa_key in dfa_dict.keys():
    #         curr_dict = dfa_dict[dfa_key]
    #         dfa = curr_dict['dfa']
    #         delta_dict = dfa.delta
    #         words_dict = curr_dict['words_dict']
    #         s_plus = words_dict['s_plus']
    #         s_minus = words_dict['s_minus']
    #
    #         for word in s_plus:
    #             curr_state = 0
    #             for letter in word:
    #                 counter_key  = letter + '_counter'
    #                 if counter_key not in delta_dict[curr_state].keys():
    #                     delta_dict[curr_state][counter_key] = 0
    #                 delta_dict[curr_state][counter_key] += 1
    #                 curr_state = delta_dict[curr_state][letter]
    #
    #         for word in s_minus:
    #             curr_state = 0
    #             for letter in word:
    #                 counter_key = letter + '_counter'
    #                 try:
    #                     if counter_key not in delta_dict[curr_state].keys():
    #                         delta_dict[curr_state][counter_key] = 0
    #                     delta_dict[curr_state][counter_key] += 1
    #                     old_state=curr_state
    #                     curr_state = delta_dict[curr_state][letter]
    #                 except Exception as e:
    #                     # TODO: check occurrences of letters in curr state key!!!
    #                     # print(e)
    #                     if type(curr_state) is not int:
    #                         print(delta_dict[old_state][letter])
    #                     continue
    #
    #         for state in delta_dict.keys():
    #             state_sum = 0
    #             for letter_key in delta_dict[state].keys():
    #                 if 'counter' in letter_key:
    #                     state_sum += delta_dict[state][letter_key]
    #
    #             for letter_key in delta_dict[state].keys():
    #                 if 'counter' in letter_key:
    #                     delta_dict[state][letter_key] /= state_sum

    if chosen_algorithm == 'q_learning':

        policy = StateGenericFunctions.create_initial_policy(all_states)
        state_value = StateGenericFunctions.create_state_value_dictionary(all_states)
        n_episodes = 20000
        step_size = alpha = 0.5
        explore_rate = epsilon = 0.1
        state_action_values = dict()
        for stateKey in all_states.keys():
            state_action_values[stateKey] = dict()
            for action in OPS:
                if all_states[stateKey].legal_op(action):
                    state_action_values[stateKey][action] = 0.0


    def compute_reward_q_learning(self, state, action):
        return StateGenericFunctions.compute_reward(None, state, action)

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


    def compute_best_action(self, state, state_action_values):
        optional_actions = list(state_action_values[state].keys())
        best_action = optional_actions[0]
        for op in optional_actions:
            if state_action_values[state][op] > state_action_values[state][best_action]:
                best_action = op
        return best_action

    def q_learning(self, state_action_values, initial_state, dfa_dict):
        """
        Q-Learning main function
        :return:
        """

        q_policy = {}
        print("num of trials ", self.n_episodes)
        for i in range(1, self.n_episodes):
            if i % 200 == 0:
                print("trial number ", i)
            current_state = initial_state
            while not current_state.is_end():

                # choosing an action to make according the current values of state-action pairs (and exploring rate, of course)
                current_action = self.choose_action(current_state,  state_action_values)

                real_action = StateGenericFunctions.compute_actual_action(current_action, current_state)
                reward = self.compute_reward_q_learning(all_states, current_state, auto_type)
                new_state = current_state.next_state(real_action)

                # Q-Learning update
                optional_actions = list(state_action_values[new_state].keys())
                best_action = optional_actions[0]

                for op in optional_actions:
                    if state_action_values[new_state][op] > state_action_values[new_state][best_action]:

                        best_action = op
                        state_action_values[current_state.hash][current_action] += \
                            stepSize * (reward + discount * state_action_values[new_state.hash][best_action]
                                        - state_action_values[current_state.hash][current_action])

                q_policy[current_state] = self.compute_best_action(current_state, state_action_values)
                current_state = new_state
        return policy


def add_probabilities_to_auto_dict(dfa_dict: dict):
    for dfa_key in dfa_dict.keys():
        curr_dict = dfa_dict[dfa_key]
        dfa = curr_dict['dfa']
        transition_matrix = dfa.dfa()
        probability_matrix = np.copy(transition_matrix)
        probability_matrix.fill(0)
        alphabet_dictionary = dfa.alphabet()
        words_dict = curr_dict['words_dict']
        s_plus = words_dict['s_plus']
        s_minus = words_dict['s_minus']

        for word in s_plus:
            curr_state = 0
            for letter in word:
                probability_matrix[curr_state][alphabet_dictionary[letter]] += 1
                curr_state = transition_matrix[curr_state][alphabet_dictionary[letter]]

        for word in s_minus:
            curr_state = 0
            for letter in word:
                probability_matrix[curr_state][alphabet_dictionary[letter]] += 1
                curr_state = transition_matrix[curr_state][alphabet_dictionary[letter]]

        # divide each row by its sum
        probability_matrix / probability_matrix.sum(axis=1, keepdims=True)

        dfa_dict['probability_matrix'] = probability_matrix