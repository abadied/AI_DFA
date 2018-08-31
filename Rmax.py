import numpy as np

import StateGenericFunctions

allStates = 0
currentState = 0
ops = 0
tran_prob_mat = 0
moves=0
stateActionsRmax = 0
stateActionsCounter = 0
discount = 0
initialState = 0
timeUntilKnown = 0

def initModule(allStatesParam, initialStateParam, opsParam, tran_prob_matParam, stateActionsRmaxParam, stateActionsCounterParam, discountParam, timeUntilKnownParam):
    """initializes the module's specific parameters"""
    global allStates, currentState, ops, tran_prob_mat, stateActionsRmax, stateActionsCounter, discount, initialState, timeUntilKnown
    allStates = allStatesParam
    initialState = initialStateParam
    ops = opsParam
    tran_prob_mat = tran_prob_matParam
    stateActionsRmax = stateActionsRmaxParam
    stateActionsCounter = stateActionsCounterParam
    discount = discountParam
    timeUntilKnown = timeUntilKnownParam

def computeBestActionRmax(stateKey):
    "givean a state, returns the best action to do in it according present knowledge (values in stateActionsRmax dictionary"
    global stateActionsRmax
    optionalActions = list(stateActionsRmax[stateKey].keys())
    bestAction = optionalActions[0]
    for op in optionalActions:
        if stateActionsRmax[stateKey][op]["value"] > stateActionsRmax[stateKey][bestAction]["value"]:
            bestAction = op
    return bestAction

def rmaxImpl():
    "Rmax main function"
    global stateActionsRmax, stateActionsCounter, moves, ops, tran_prob_mat, discount, currentState, allStates, initialState, timeUntilKnown
    print("num of state action pairs: ", stateActionsCounter)
    stateActionsRmaxTemp = stateActionsRmax
    counterKnownStates = 0
    while counterKnownStates < stateActionsCounter:
        currentState = initialState
        while True:
            moves += 1
            # computing best action to take
            bestAction = computeBestActionRmax(currentState.hash)
            stateActionsRmax[currentState.hash][bestAction]["totalVisits"] += 1.

            realAction = StateGenericFunctions.computeActualAction(bestAction, currentState)

            # updates
            reward = stateActionsRmax[currentState.hash][bestAction]["legalActions"][realAction]["reward"] = StateGenericFunctions.computeReward(allStates, currentState, realAction)
            stateActionsRmax[currentState.hash][bestAction]["legalActions"][realAction]["counterSpecificOp"] += 1.
            if stateActionsRmax[currentState.hash][bestAction]["totalVisits"] == timeUntilKnown:

                stateActionsRmax[currentState.hash][bestAction]["known"] = True
                counterKnownStates += 1

                if counterKnownStates % 50 == 0:
                    print("num of pairs found ", counterKnownStates)

                for action in stateActionsRmax[currentState.hash][bestAction]["legalActions"].keys():  # when a state-action pair becomes known, we know all transitions
                    stateActionsRmax[currentState.hash][bestAction]["legalActions"][action]["nextState"] = currentState.nextState(action).hash

                while True: #policy evaluation
                    newStateActionValue = dict()
                    for stateKey in allStates.keys():
                        newStateActionValue[stateKey] = dict()
                        for action in stateActionsRmax[stateKey]: # applying bellman equation for state-action pairs
                            newStateActionValue[stateKey][action] = 0
                            if not stateActionsRmax[stateKey][action]["totalVisits"] == 0:
                                for legalAction in stateActionsRmax[stateKey][action]["legalActions"]:
                                    prob = stateActionsRmax[stateKey][action]["legalActions"][legalAction]["counterSpecificOp"] / stateActionsRmax[stateKey][action]["totalVisits"]
                                    nextState = stateActionsRmax[stateKey][action]["legalActions"][legalAction]["nextState"]  # that's a string

                                    #computing next state value (for the best action taken in it)
                                    nextStateValue = -float('Inf')
                                    for possibleAction in stateActionsRmax[nextState].keys():
                                        if stateActionsRmax[nextState][possibleAction]["value"] > nextStateValue:
                                            nextStateValue = stateActionsRmax[nextState][possibleAction]["value"]
                                    newStateActionValue[stateKey][action] += prob * (stateActionsRmax[stateKey][action][
                                                                                         "legalActions"][legalAction]["reward"] + discount * nextStateValue)
                            else:
                                newStateActionValue[stateKey][action] = stateActionsRmax[stateKey][action]["value"]
                    sum = 0
                    for stateKey in allStates.keys():
                        for action in newStateActionValue[stateKey]:
                            sum += np.abs(stateActionsRmax[stateKey][action]["value"] - newStateActionValue[stateKey][action])
                    for stateKey in allStates.keys():
                        for action in newStateActionValue[stateKey]:
                            stateActionsRmax[stateKey][action]["value"] = newStateActionValue[stateKey][action]
                    if sum < 1:
                        break
            if currentState.isEnd():
                break
            currentState = currentState.nextState(realAction)
    policy = dict()
    for stateKey in allStates.keys():
        policy[stateKey] = computeBestActionRmax(stateKey)
    return policy