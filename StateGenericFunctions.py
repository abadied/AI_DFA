import Board
import numpy as np

FINAL_STATES = []

def openingPrint(allStates, room, printRoom):
    "a recommended print of the room and number of states, to be able to follow the game flow"
    print("room representation: ")
    printRoom(room)
    print("number of states: ", len(list(allStates.keys())))

def getAllStatesImpl(currentState, allStates, ops):
    "recursive function to get all states starting from @currentState using the actions in @ops"
    global FINAL_STATES
    for i in ops:
        if currentState.legalOp(i):
            newState = currentState.nextState(i)
            if newState.hash not in allStates.keys():  # maybe it's better to use hash function in order to construct allStates
                allStates[newState.hash] = newState
                if not newState.isEnd():
                    getAllStatesImpl(newState, allStates, ops)
                else:
                    FINAL_STATES.append(newState.hash)

def getAllStates(initialState, ops):
    "returns all states starting from @initialState using the actions in @ops"
    allStates = dict()
    allStates[initialState.hash] = initialState
    getAllStatesImpl(initialState, allStates, ops)
    return allStates

def computeReward(allStates, state, action):
    "computes reward for a state&action pair. returns positive reward only for ending the game"
    if not state.isEnd() and state.nextState(action).isEnd():
        return Board.FINISHING_CREDIT
    return -Board.MOVE_COST

#using another reward function would give different results, for example the following function:
def computeReward2(allStates, state, action):
    """computes reward for a state&action pair. returns positive reward for every action that makes progress in the game.
    this function computes the reward of an action given that the robot succeeded to make it"""
    if action == "clean" and state.stateRoom[0] in state.stateRoom[1]:
        return Board.CLEANING_CREDIT
    elif action == "pick" and state.stateRoom[0] in state.stateRoom[2]:
        return Board.PICKING_CREDIT
    elif action == "putInBasket":
        return Board.PUTTING_CREDIT * state.stateRoom[3]
    return 0

def createInitialPolicy(allStates):
    "initializing a policy that selects a random action for all states (except final ones)"
    policy = dict()
    for key in allStates.keys():
        policy[key] = "random"
        if allStates[key].isEnd():
            policy[key] = "idle"
    return policy

def createStateValueDictionary(allStates):
    "initial state value - 0 for all states"
    stateValue = dict()
    for key in allStates.keys():
        stateValue[key] = 0.
    return stateValue

def expectedReturn(allStates, stateKey, action, stateValue, ops, computeRewardFunction):
    """computes the expected discounted return from @allStates[@stateKey] using @action, and according the 
       current @stateValue dictionary"""
    # initailize total return
    returns = 0.0
    returns -= Board.MOVE_COST

    for i in range(len(ops)):
        prob = Board.TRAN_PROB_MAT[ops.index(action)][i]
        realAction = ops[i]
        if allStates[stateKey].legalOp(realAction):
            newState = allStates[stateKey].nextState(realAction)
            reward = float(computeRewardFunction(allStates, allStates[stateKey], realAction))
            returns += prob * (reward + Board.DISCOUNT * stateValue[newState.hash])
        elif not allStates[stateKey].isEnd():
            returns += prob * Board.DISCOUNT * stateValue[stateKey]
        else:
            returns = 100
    return returns

def getProbSAS(state1, state2, action):
    """"given state1 and action, returns the probability to reach state2
        in case that action is 'random' the function returns -1
        if state1 is a final state, than it leads by any action to itself in probability 1"""
    if action == 'random':
        return -1.0
    actionIndex = Board.OPS.index(action)
    possibleActionsIndices = [numOp for numOp in range(len(Board.OPS)) if Board.TRAN_PROB_MAT[actionIndex][numOp] > 0]
    sum = 0.0
    for numOp in possibleActionsIndices:
        if state1.actualNextState(Board.OPS[numOp]).hash == state2.hash:
            sum += Board.TRAN_PROB_MAT[actionIndex][numOp]
    return sum

def getRewardSA(allStates, state, action, rewardFunction):
    """given an action, returns expectation of the reward for applying @action in @self according the given @rewardFunction."""
    expectedReward = 0.
    actionIndex = Board.OPS.index(action)
    for op in Board.OPS:
        opIndex = Board.OPS.index(op)
        expectedReward += Board.TRAN_PROB_MAT[actionIndex][opIndex] * rewardFunction(allStates, state, op)
    return expectedReward

def computeActualAction(actionChosen, currentState):
    """computing the actual action that was taken when choosing @actionChosen in @currentState."""
    actionIndex = Board.OPS.index(actionChosen)
    sample = np.random.uniform(0.000000001, 1.)
    sumProb = 0
    for i in range(len(Board.OPS)):
        sumProb += Board.TRAN_PROB_MAT[actionIndex][i]
        if sumProb > sample:
            realActionIndex = i
            break
    realAction = Board.OPS[realActionIndex]
    if not currentState.legalOp(realAction):
        realAction = "idle"
    return realAction