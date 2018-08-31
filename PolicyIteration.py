import numpy as np

import StateGenericFunctions

policy = 0
allStates = 0
ops = 0
computeRewardFunction = 0

def initModule(policyParam, allStatesParam, opsParam, computeRewardFunctionParam):
    """initializes the module's specific parameters"""
    global policy, allStates, ops, computeRewardFunction
    policy = policyParam
    allStates = allStatesParam
    ops = opsParam
    computeRewardFunction = computeRewardFunctionParam

def computeReward_PolicyIteration(allStates, state, action):
    return StateGenericFunctions.computeReward(allStates, state, action)

def policyIteration():
    "Policy Iteration main function"
    global policy, allStates, ops, computeRewardFunction
    newStateValue = dict()
    for key in allStates.keys():
        newStateValue[key] = 0
    policyImprovementInd = 0
    stateValue = StateGenericFunctions.createStateValueDictionary(allStates)
    while True:  # iterating on policies
        for stateKey in allStates.keys():  # applying bellman equation for all states
            newStateValue[stateKey] = StateGenericFunctions.expectedReturn(allStates, stateKey, policy[stateKey], stateValue, ops, computeRewardFunction)
        sum = 0
        for stateKey in allStates.keys():
            sum += np.abs(newStateValue[stateKey] - stateValue[stateKey])
        for key in stateValue:
            stateValue[key] = newStateValue[key]

        if sum < 1e-2: # evaluation converged
            policyImprovementInd += 1
            newPolicy = dict()
            for stateKey in allStates.keys():
                actionReturns = []
                # go through all actions and select the best one
                for op in ops:
                    if (allStates[stateKey].legalOp(op)):
                        actionReturns.append(
                            StateGenericFunctions.expectedReturn(allStates, stateKey, op, stateValue, ops, computeRewardFunction))
                    else:
                        actionReturns.append(-float('inf'))
                bestAction = np.argmax(actionReturns)
                newPolicy[stateKey] = ops[bestAction]
                policyChanges = 0
            for key in policy.keys():
                if newPolicy[key] != policy[key]:
                    policyChanges += 1
            print("changed policy #", policyImprovementInd, " and num of changes is: ", policyChanges)
            if policyChanges == 0:
                break
            policy = newPolicy
    return policy