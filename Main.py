
from PolicyIteration import PolicyIteration
import StateGenericFunctions
from State import *
import random
from AutomataLearning import AutomataLearner
import Constants
from QLearning import QLearningAlg
from env_class import Env
from AutomatasState import AutomatasState
from room import Room


def sample_initial_state():
    return State()


def sample_action():
    random_op = random.randint(0, len(OPS) - 1)
    return OPS[int(random_op)]


def add_probabilities_to_auto_dict(initial_automata_state, s_minus, s_plus, all_states, ops):
    transition_matrix_dict = {}

    for op in ops:
        transition_matrix_dict[op] = np.zeros([len(all_states), len(all_states)])

    def insert_probs(words):
        for word in words:
            initial_automata_state.reset()
            curr_state = initial_automata_state.get_state_key()
            i = 0
            while i < len(word):
                op_letter = word[i]
                obs_letter = word[i + 1]
                i += 2

                curr_state_idx = all_states.index(curr_state)
                op = Constants.letter_value_dictionary[op_letter]
                initial_automata_state.next_state(op, obs_letter)
                next_state = initial_automata_state.get_state_key()
                next_state_idx = all_states.index(next_state)
                transition_matrix_dict[op][curr_state_idx][next_state_idx] += 1
                curr_state = next_state

    insert_probs(s_plus)
    insert_probs(s_minus)

    # normalize values in every matrix
    for action_key in transition_matrix_dict:
        transition_matrix_dict[action_key] / transition_matrix_dict[action_key].sum(axis=1, keepdims=True)

    return transition_matrix_dict


def main():
    policy = None
    all_states = StateGenericFunctions.get_all_states(State(), OPS)

    # Hyper parameters
    alpha = 0.75
    discount_factor = 0.999
    epsilon_min = 0
    epsilon = 1
    decay_epsilon = 0.99999999
    max_steps = 100
    episodes = 5000

    print("Running Automata Learning")
    dfa_dict = {
                # 'end': None,
                # 'pick': None,
                'clean': None,
                # 'putInBasket': None}
                }
    StateGenericFunctions.opening_print(all_states, room, print_room)
    max_word_length = 200
    automata_learner = AutomataLearner(letter_value_dictionary=Constants.letter_value_dictionary, reward_value_dict={})
    real_initial_state = State()

    # TEST NEW LEARNING FUNCTION
    dfa_dict, words_dict = automata_learner.learn_all_dfas(initial_state=real_initial_state,
                                                           max_word_length=max_word_length,
                                                           dfa_dict=dfa_dict)

    initial_state = '0' * len(list(dfa_dict.keys()))

    # one boolean list for each wall , fruit, stain, basket
    # observable_list = [[0, 1], [0, 1], [0, 1], [0, 1], [0, 1], [0, 1], [0, 1]]
    observable_list = [[0, 1], [0, 1], [0, 1], [0, 1]]

    all_auto_states = StateGenericFunctions.get_all_automatas_states(dfa_dict, observable_list)

    if Constants.optimization_algorithm == 'policy_iteration':
        initial_automata_state = AutomatasState(dfa_dict)
        transition_matrix_dict = add_probabilities_to_auto_dict(initial_automata_state,
                                                                words_dict['s_minus'],
                                                                words_dict['s_plus'],
                                                                all_auto_states, Constants.OPS)

        # use policy iteration for the combinations
        initial_policy = dict()

        for state_key in all_auto_states:
            initial_policy[str(state_key)] = "left"

        state_action_values = dict()
        for state_key in all_auto_states:
            state_action_values[str(state_key)] = dict()
            for action in OPS:
                state_action_values[str(state_key)][action] = 0.0

        accepting_states_dict = {}
        # num_of_obs = len(observable_list)
        dfa_keys_list = list(dfa_dict.keys())

        for i in range(len(dfa_keys_list)):
            accepting_states_dict[i] = {}
            accepting_states_dict[i]['states'] = dfa_dict[dfa_keys_list[i]]['accepting_states']
            accepting_states_dict[i]['reward'] = dfa_dict[dfa_keys_list[i]]['reward']

        policy_iteration = PolicyIteration(initial_policy, all_auto_states, Constants.OPS, transition_matrix_dict,
                                           accepting_states_dict)
        policy = policy_iteration.policy_iteration()

    elif Constants.optimization_algorithm == 'q_learning':
        automata_state = AutomatasState(dfa_dict=dfa_dict)
        env = Env(real_initial_state, automata_state, Constants.OPS, StateGenericFunctions.compute_reward, all_auto_states)
        q_learning = QLearningAlg(alpha, episodes, epsilon, epsilon_min, decay_epsilon, discount_factor, max_steps, env)
        q_learning.q_learning_v2()
        policy = q_learning.get_policy()

    # Showing the game - used by all algorithms
    if policy is not None:
        cls_room = Room(room, policy, all_states, real_initial_state, OPS, TRAN_PROB_MAT,
                        StateGenericFunctions.FINAL_STATES, dfa_dict)
        cls_room.show_room()


if __name__ == '__main__':
    main()
