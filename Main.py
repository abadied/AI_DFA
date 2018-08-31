import AutomataLearning
import Dfa
import PolicyIteration
import QLearning
import Rmax
import Show
import StateGenericFunctions
import StateWithAuto
from State import *


##############
# Q-Learning #
##############

print("Running Q-Learning")
allStates = StateGenericFunctions.getAllStates(State(), OPS)
initialState = State()
StateGenericFunctions.openingPrint(allStates, room, printRoom)
policy = StateGenericFunctions.createInitialPolicy(allStates)
stateValue = StateGenericFunctions.createStateValueDictionary(allStates)
nEpisodes = 20000
stepSize = alpha = 0.5
exploreRate = epsilon = 0.1
stateActionValues = dict()
for stateKey in allStates.keys():
    stateActionValues[stateKey] = dict()
    for action in OPS:
        if allStates[stateKey].legalOp(action):
            stateActionValues[stateKey][action] = 0.0
QLearning.initModule(policy, stateActionValues, exploreRate, nEpisodes, OPS, TRAN_PROB_MAT, stepSize, DISCOUNT, State(), allStates)
policy = QLearning.qLearning()


####################
# Policy Iteration #
####################

print("Running Policy Iteration")
allStates = StateGenericFunctions.getAllStates(State(), OPS)
initialState = State()
PolicyIteration.initModule(StateGenericFunctions.createInitialPolicy(allStates), allStates, OPS, PolicyIteration.computeReward_PolicyIteration)
StateGenericFunctions.openingPrint(allStates, room, printRoom)
policy = PolicyIteration.policyIteration()


########
# Rmax #
########

print("Running Rmax")
allStates = StateGenericFunctions.getAllStates(State(), OPS)
initialState = State()
StateGenericFunctions.openingPrint(allStates, room, printRoom)
maxReward = max(CLEANING_CREDIT, PICKING_CREDIT, PUTTING_CREDIT, FINISHING_CREDIT)
maxValue = 1. / (1. - DISCOUNT) * maxReward
stateActionsRmax = dict()
stateActionsRmax["heaven"] = dict()
stateActionsRmax["heaven"]["idle"] = {"reward" : maxReward, "value" : maxValue}
stateActionsCounter = 0             # used for stop condition- this is the maximal number of "known" states
for stateKey in allStates.keys():
    stateActionsRmax[stateKey] = dict()
    for action in OPS:
        if allStates[stateKey].legalOp(action):
            stateActionsRmax[stateKey][action] = { "known" : False, "totalVisits" : 0. , "value" : maxValue, "legalActions" : dict()}
            stateActionsCounter += 1
            for realAction in OPS:
                if allStates[stateKey].legalOp(realAction):
                    stateActionsRmax[stateKey][action]["legalActions"][realAction] = {"counterSpecificOp" : 0. , "reward" : maxReward, "nextState" : "heaven"}
timeUntilKnown = 10
Rmax.initModule(allStates, State(), OPS, TRAN_PROB_MAT, stateActionsRmax, stateActionsCounter, DISCOUNT, timeUntilKnown)
policy = Rmax.rmaxImpl()


#####################
# Automata Learning #
#####################

print("Running Automata Learning")


def expectedReturnForNonMarkovianReward(allStates, state, action):
    reward = StateGenericFunctions.computeReward(allStates, state, action)
    if (not (state.dfa.Final == state.stateInAuto)) and (state.dfa.Final == state.nextState(action).stateInAuto):#AutomataLearning.computeReward_NonMarkovian(state, state.nextState(action), action):
        reward += NONE_MARKOVIAN_REWARD
    return reward


basicOps = ["up", "down", "left", "right", "clean"]
allOps = ["up", "down", "left", "right", "clean", "pick", "putInBasket", "random", "idle"]
allStates = StateGenericFunctions.getAllStates(State(), allOps)
StateGenericFunctions.openingPrint(allStates, room, printRoom)
maxWordLength = 4
AutomataLearning.init_automata_learning(State(), maxWordLength)
dfa = AutomataLearning.learn_dfa()
initialState = StateWithAuto.StateWithAuto(dfa, State(), room)
allStatesWithAuto = StateGenericFunctions.getAllStates(initialState, basicOps)
print("number of states after learning the automaton: ", len(allStatesWithAuto))
initialPolicy = dict()
for stateKey in allStatesWithAuto.keys():
    initialPolicy[stateKey] = "left"
PolicyIteration.initModule(initialPolicy, allStatesWithAuto, basicOps, expectedReturnForNonMarkovianReward)
policy = PolicyIteration.policyIteration()
allStates = allStatesWithAuto


# Showing the game - used by all algorithms
Show.showRoom(room, policy, allStates, initialState, OPS, TRAN_PROB_MAT, StateGenericFunctions.FINAL_STATES)