import AutomataLearning
import PolicyIteration
import QLearning
import Rmax
import Show
import StateGenericFunctions
import StateWithAuto
from State import *


chosen_algorithm = "automata_learning"
initial_state = State()
all_states = StateGenericFunctions.get_all_states(State(), OPS)
policy = None


def expected_return_for_non_markovian_reward(_all_states, state, _action):
    reward = StateGenericFunctions.compute_reward(_all_states, state, _action)
    if (not (state.dfa.Final == state.stateInAuto)) and (state.dfa.Final == state.next_state(
            action).stateInAuto):  # AutomataLearning.computeReward_NonMarkovian(state, state.nextState(action), action):
        reward += NONE_MARKOVIAN_REWARD
    return reward

##############
# Q-Learning #
##############


if chosen_algorithm == 'q_learning':
    print("Running Q-Learning")

    StateGenericFunctions.opening_print(all_states, room, print_room)
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
    QLearning.init_module(policy, state_action_values, explore_rate, n_episodes, OPS, TRAN_PROB_MAT, step_size, DISCOUNT, initial_state, all_states)
    policy = QLearning.q_learning()


####################
# Policy Iteration #
####################
if chosen_algorithm == 'policy_iteration':
    print("Running Policy Iteration")
    PolicyIteration.init_module(StateGenericFunctions.create_initial_policy(all_states), all_states, OPS, PolicyIteration.compute_reward_policy_iteration)
    StateGenericFunctions.opening_print(all_states, room, print_room)
    policy = PolicyIteration.policy_iteration()


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


#####################
# Automata Learning #
#####################
if chosen_algorithm == 'automata_learning':
    # TODO: add letter value dictionary for action and observation
    # TODO: add simulations of action observation and learn respective dfas
    # TODO: convert the state to work with automata states and rewards
    print("Running Automata Learning")
    dfa_dict = {'fruit': None,
                'stain': None,
                'put_in_basket': None}
    StateGenericFunctions.opening_print(all_states, room, print_room)
    max_word_length = 100
    for _key in dfa_dict:
        dfa_dict[_key] = AutomataLearning.learn_dfa(initial_state, max_word_length, _key)
    initial_state = StateWithAuto.StateWithAuto(dfa_dict, State(), room)
    allStatesWithAuto = StateGenericFunctions.get_all_states(initial_state, OPS)
    print("number of states after learning the automaton: ", len(allStatesWithAuto))
    initialPolicy = dict()
    for stateKey in allStatesWithAuto.keys():
        initialPolicy[stateKey] = "left"
    PolicyIteration.init_module(initialPolicy, allStatesWithAuto, OPS, expected_return_for_non_markovian_reward)
    policy = PolicyIteration.policy_iteration()
    all_states = allStatesWithAuto


# Showing the game - used by all algorithms
if policy is not None:
    Show.show_room(room, policy, all_states, initial_state, OPS, TRAN_PROB_MAT, StateGenericFunctions.FINAL_STATES)