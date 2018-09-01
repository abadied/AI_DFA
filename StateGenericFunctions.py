import Board
import numpy as np

FINAL_STATES = []


def opening_print(all_states, room, print_room):
    """
    a recommended print of the room and number of states, to be able to follow the game flow
    :param all_states:
    :param room:
    :param print_room:
    :return:
    """
    print("room representation: ")
    print_room(room)
    print("number of states: ", len(list(all_states.keys())))


def get_all_states_impl(current_state, all_states, ops):
    """
    recursive function to get all states starting from @currentState using the actions in @ops
    :param current_state:
    :param all_states:
    :param ops:
    :return:
    """
    global FINAL_STATES
    for i in ops:
        if current_state.legal_op(i):
            new_state = current_state.next_state(i)
            if new_state.hash not in all_states.keys():  # maybe it's better to use hash function in order to construct allStates
                all_states[new_state.hash] = new_state
                if not new_state.is_end():
                    get_all_states_impl(new_state, all_states, ops)
                else:
                    FINAL_STATES.append(new_state.hash)


def get_all_states(initial_state, ops):
    """
    returns all states starting from @initialState using the actions in @ops
    :param initial_state:
    :param ops:
    :return:
    """
    all_states = dict()
    all_states[initial_state.hash] = initial_state
    get_all_states_impl(initial_state, all_states, ops)
    return all_states


def compute_reward(allStates, state, action):
    """
    computes reward for a state&action pair. returns positive reward only for ending the game
    :param allStates:
    :param state:
    :param action:
    :return:
    """
    if not state.is_end() and state.next_state(action).is_end():
        return Board.FINISHING_CREDIT
    return -Board.MOVE_COST


# using another reward function would give different results, for example the following function:
def compute_reward_2(allStates, state, action):
    """computes reward for a state&action pair. returns positive reward for every action that makes progress in the game.
    this function computes the reward of an action given that the robot succeeded to make it"""
    if action == "clean" and state.stateRoom[0] in state.stateRoom[1]:
        return Board.CLEANING_CREDIT
    elif action == "pick" and state.stateRoom[0] in state.stateRoom[2]:
        return Board.PICKING_CREDIT
    elif action == "putInBasket":
        return Board.PUTTING_CREDIT * state.stateRoom[3]
    return 0


def create_initial_policy(all_states):
    """
    initializing a policy that selects a random action for all states (except final ones)
    :param all_states:
    :return:
    """
    
    policy = dict()
    for key in all_states.keys():
        policy[key] = "random"
        if all_states[key].is_end():
            policy[key] = "idle"
    return policy


def create_state_value_dictionary(all_states):
    """
    initial state value - 0 for all states
    :param all_states:
    :return:
    """
    state_value = dict()
    for key in all_states.keys():
        state_value[key] = 0.
    return state_value


def expected_return(all_states, state_key, action, state_value, ops, compute_reward_function):
    """computes the expected discounted return from @allStates[@stateKey] using @action, and according the 
       current @stateValue dictionary"""
    # initailize total return
    returns = 0.0
    returns -= Board.MOVE_COST

    for i in range(len(ops)):
        prob = Board.TRAN_PROB_MAT[ops.index(action)][i]
        real_action = ops[i]
        if all_states[state_key].legal_op(real_action):
            newState = all_states[state_key].next_state(real_action)
            reward = float(compute_reward_function(all_states, all_states[state_key], real_action))
            returns += prob * (reward + Board.DISCOUNT * state_value[newState.hash])
        elif not all_states[state_key].is_end():
            returns += prob * Board.DISCOUNT * state_value[state_key]
        else:
            returns = 100
    return returns


def get_prob_sas(state1, state2, action):
    """"given state1 and action, returns the probability to reach state2
        in case that action is 'random' the function returns -1
        if state1 is a final state, than it leads by any action to itself in probability 1"""
    if action == 'random':
        return -1.0
    action_index = Board.OPS.index(action)
    possible_actions_indices = [numOp for numOp in range(len(Board.OPS)) if Board.TRAN_PROB_MAT[action_index][numOp] > 0]
    sum = 0.0
    for numOp in possible_actions_indices:
        if state1.actualNextState(Board.OPS[numOp]).hash == state2.hash:
            sum += Board.TRAN_PROB_MAT[action_index][numOp]
    return sum


def get_reward_sa(all_states, state, action, reward_function):
    """
    given an action, returns expectation of the reward for applying @action in @self according the given @rewardFunction.
    :param all_states:
    :param state:
    :param action:
    :param reward_function:
    :return:
    """
    expected_reward = 0.
    action_index = Board.OPS.index(action)
    for op in Board.OPS:
        op_index = Board.OPS.index(op)
        expected_reward += Board.TRAN_PROB_MAT[action_index][op_index] * reward_function(all_states, state, op)
    return expected_reward


def compute_actual_action(action_chosen, current_state):
    """
    computing the actual action that was taken when choosing @actionChosen in @currentState.
    :param action_chosen:
    :param current_state:
    :return:
    """
    action_index = Board.OPS.index(action_chosen)
    sample = np.random.uniform(0.000000001, 1.)
    sum_prob = 0
    for i in range(len(Board.OPS)):
        sum_prob += Board.TRAN_PROB_MAT[action_index][i]
        if sum_prob > sample:
            real_action_index = i
            break
    real_action = Board.OPS[real_action_index]
    if not current_state.legal_op(real_action):
        real_action = "idle"
    return real_action
