import copy

class StateWithAuto:
    """This class represents a specific state of the game combined with the state in the automaton. 
       it contains all parameters to fully characterize specific pair"""

    def __init__(self, dfa, stateInRoomParam, roomParam):
        """

        :type dfa: DFA
        """
        self.stateInRoom = stateInRoomParam
        self.stateRoom = self.stateInRoom.stateRoom
        self.stateInAuto = dfa.Initial
        self.dfa = dfa
        self.room = roomParam
        self.statePair = copy.deepcopy(self.stateInRoom.stateRoom)
        self.statePair.append(sorted(list(self.stateInAuto)))
        self.hash = repr(self.statePair)    # each (stateInRoom, stateInAuto) pair has a string that is it's name (and it's unique)
        self.end = len(self.stateInRoom.stateRoom[1]) == 0 and len(self.stateInRoom.stateRoom[2]) == 0 and self.stateInRoom.stateRoom[3] == 0

    def isEnd(self):
        self.end = len(self.stateInRoom.stateRoom[1]) == 0 and len(self.stateInRoom.stateRoom[2]) == 0 and self.stateInRoom.stateRoom[3] == 0
        return self.end

    def nextState(self, op):
        "givan a pair state and a legal operation, returns the next pair state"
        if op == "idle":
            return self
        newAutoState = StateWithAuto(self.dfa, self.stateInRoom, self.room)
        newStateInRoom = self.stateInRoom.nextState(op)
        newStateInAuto = self.dfa.evalSymbol(self.stateInAuto, op[0])
        newAutoState.stateInRoom = newStateInRoom
        newAutoState.stateRoom = newAutoState.stateInRoom.stateRoom
        newAutoState.stateInAuto = newStateInAuto
        newAutoState.statePair = copy.deepcopy(newAutoState.stateInRoom.stateRoom)
        newAutoState.statePair.append(sorted(list(newAutoState.stateInAuto)))
        newAutoState.hash = repr(newAutoState.statePair)
        return newAutoState

    def legalOp(self, op):
        if op == "idle":
            return True
        if self.isEnd():
            return False
        row_positionOfRobot = self.stateInRoom.stateRoom[0][0]
        col_positionOfRobot = self.stateInRoom.stateRoom[0][1]
        occupied = [0,7,10] # these numbers represent wall, basket, cabinet and man appropriately
        if op == "up" and self.room[row_positionOfRobot - 1][col_positionOfRobot] not in occupied:
            return True
        elif op == "down" and self.room[row_positionOfRobot + 1][col_positionOfRobot] not in occupied:
            return True
        elif op == "left" and self.room[row_positionOfRobot][col_positionOfRobot - 1] not in occupied:
            return True
        elif op == "right" and self.room[row_positionOfRobot][col_positionOfRobot + 1] not in occupied:
            return True
        elif op in ["clean", "pick"]:
            return True
        elif op == "putInBasket"  and self.stateRoom[0] == self.basketPosition:
            return True
        return False

    def printState(self):
        "just for debug"
        print("State in board:\trobot: ", self.stateInRoom.stateRoom[0], ", stains: ", self.stateInRoom.stateRoom[1], ", fruits: ", self.stateInRoom.stateRoom[2], \
              "State in auto:\t", self.dfa.States[self.stateInAuto])