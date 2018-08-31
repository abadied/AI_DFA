import numpy as np

import StateGenericFunctions

policy = 0
stateActionValues = 0
exploreRate = 0
nEpisodes = 0
ops = 0
tran_prob_mat = 0
stepSize = 0
discount = 0
initialState = 0
allStates = 0

def initModule(policyParam, stateActionValuesParam, exploreRateParam, nEpisodesParam, opsParam, tran_prob_matParam, stepSizeParam, discountParam, initialStateParam, allStatesParam):
    """initializes the module's specific parameters"""
    global policy, stateActionValues, exploreRate, nEpisodes, ops, tran_prob_mat, stepSize, discount, initialState
    policy = policyParam
    stateActionValues = stateActionValuesParam
    exploreRate = exploreRateParam
    nEpisodes = nEpisodesParam
    ops = opsParam
    tran_prob_mat =tran_prob_matParam
    stepSize = stepSizeParam
    discount = discountParam
    initialState = initialStateParam
    allStates = allStatesParam

def computeReward_QLearning(allStates, state, action):
    return StateGenericFunctions.computeReward(allStates, state, action)

def chooseAction(state, stateActionValues):
    "choose an action based on epsilon greedy algorithm"
    optionalActions = stateActionValues[state.hash].keys()
    optionalActions = [op for op in optionalActions if not op == "random"]
    if np.random.binomial(1, exploreRate) == 1:
        # in this case we need to choose an action from the legal ones
        return np.random.choice(optionalActions)
    else:
        # choose the best action according to values we have at this point from state-action dict
        bestAction = optionalActions[0]
        for op in optionalActions:
            if stateActionValues[state.hash][op] > stateActionValues[state.hash][bestAction]:
                bestAction = op
        return bestAction

def computeBestAction(state):
    optionalActions = list(stateActionValues[state.hash].keys())
    bestAction = optionalActions[0]
    for op in optionalActions:
        if stateActionValues[state.hash][op] > stateActionValues[state.hash][bestAction]:
            bestAction = op
    return bestAction

def qLearning():
    "Q-Learning main function"
    global policy, stateActionValues, initialState, nEpisodes
    print("num of trials ", nEpisodes)
    for i in range(1,nEpisodes):
        if i%200 == 0:
            print("trial number ", i)
        currentState = initialState
        while not currentState.isEnd():

            # choosing an action to make according the current values of state-action pairs (and exploring rate, of course)
            currentAction = chooseAction(currentState, stateActionValues)

            realAction = StateGenericFunctions.computeActualAction(currentAction, currentState)
            reward = computeReward_QLearning(allStates, currentState, realAction)
            newState = currentState.nextState(realAction)

            # Q-Learning update
            optionalActions = list(stateActionValues[newState.hash].keys())
            bestAction = optionalActions[0]
            for op in optionalActions:
                if stateActionValues[newState.hash][op] > stateActionValues[newState.hash][bestAction]:
                    bestAction = op
            stateActionValues[currentState.hash][currentAction] += stepSize * (
                reward + discount * stateActionValues[newState.hash][bestAction] -
                stateActionValues[currentState.hash][currentAction])
            policy[currentState.hash] = computeBestAction(currentState)
            currentState = newState
    return policy