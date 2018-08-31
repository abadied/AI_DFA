from Board import *
import numpy as np


class State:

    """This class represents a specific state of the game. it contains all parameters to fully
    characterize specific situation"""

    def __init__(self):
        self.stateRoom = [[ROBOT_POSITION[0], ROBOT_POSITION[1]]]  # list of lists: lists for the robot coordinates, stains and fruits location
        stains = []
        fruits = []
        carriedFruits = 0  # num of fruits the robot is holding
        for i in range(len(room)):
            for j in range(len(room[0])):
                if room[i][j] == 8:
                    stains.append([i, j])
                if room[i][j] in [3, 4, 5]:
                    fruits.append([i, j])
        self.stateRoom.append(stains)
        self.stateRoom.append(fruits)
        self.stateRoom.append(carriedFruits)
        self.hash = repr(self.stateRoom)  # each stateRoom has a string that is it's name (and it's unique)
        self.end = len(self.stateRoom[1]) == 0 and len(self.stateRoom[2]) == 0 and self.stateRoom[3] == 0

    def isEnd(self):
        "returns true iff self is a final state"
        self.end = len(self.stateRoom[1]) == 0 and len(self.stateRoom[2]) == 0 and self.stateRoom[3] == 0
        return self.end

    def nextState(self, op):
        "givan a state and an operation, returns the next room's state"
        if not self.legalOp(op):
            return self

        newState = State()
        newState.stateRoom = copy.deepcopy(self.stateRoom[:])  # deep copy
        if op == "up":
            newState.stateRoom[0][0] = self.stateRoom[0][0] - 1
        elif op == "down":
            newState.stateRoom[0][0] = self.stateRoom[0][0] + 1
        elif op == "left":
            newState.stateRoom[0][1] = self.stateRoom[0][1] - 1
        elif op == "right":
            newState.stateRoom[0][1] = self.stateRoom[0][1] + 1
        elif op == "clean":  # remove a stain from the current position only if there's a stain there
            if self.stateRoom[0] in self.stateRoom[1]:
                index = self.stateRoom[1].index(self.stateRoom[0])
                newState.stateRoom[1] = newState.stateRoom[1][0:index] + newState.stateRoom[1][index + 1:]
                newState.end = newState.isEnd()
            else:
                return self
        elif op == "pick":  # pick a fruit from the current position only if there's a fruit there
            if self.stateRoom[0] in self.stateRoom[2]:
                index = self.stateRoom[2].index(self.stateRoom[0])
                newState.stateRoom[2] = newState.stateRoom[2][0:index] + newState.stateRoom[2][index + 1:]
                newState.stateRoom[3] += 1
                newState.end = newState.isEnd()
            else:
                return self
        elif op == "putInBasket":  # legalOp prevents putInBasket not in the basket
            newState.stateRoom[3] = 0
            newState.end = newState.isEnd()
        elif op == "idle":
            return self
        elif op == "random":
            legalOps = [op for op in OPS if self.legalOp(op)]
            return self.nextState(np.random.choice(legalOps))
        newState.hash = repr(newState.stateRoom)
        return newState

    def probablisticNextState(self, op):
        """givan a state and an operation to apply, computes a possible action to take by the TRAN_PROB_MAT imported from Board.py 
            and returns the next room's state after applying the actual action"""
        global TRAN_PROB_MAT
        actionIndex = OPS.index(op)
        sample = np.random.uniform(0.000000001, 1.)
        sumProb = 0
        for i in range(len(OPS)):
            sumProb += TRAN_PROB_MAT[actionIndex][i]
            if sumProb > sample:
                realActionIndex = i
                break
        actualOp = OPS[realActionIndex]
        return self.nextState(actualOp)

    def legalOp(self, op):
        "returns true iff @op is legal in @self state"
        if op == "idle":
            return True
        if self.isEnd():
            return False
        row_positionOfRobot = self.stateRoom[0][0]
        col_positionOfRobot = self.stateRoom[0][1]
        occupied = [0, 7, 10]  # these numbers represent wall, basket, cabinet and man appropriately
        if op == "up" and room[row_positionOfRobot - 1][col_positionOfRobot] not in occupied:
            return True
        elif op == "down" and room[row_positionOfRobot + 1][col_positionOfRobot] not in occupied:
            return True
        elif op == "left" and room[row_positionOfRobot][col_positionOfRobot - 1] not in occupied:
            return True
        elif op == "right" and room[row_positionOfRobot][col_positionOfRobot + 1] not in occupied:
            return True
        elif op in ["clean", "pick"]:
            return True
        elif op == "putInBasket" and self.stateRoom[0] == BASKET_POSITION:
            return True
        return False

    def printState(self):
        "prints a string representation of the state"
        print("State: robot- ", self.stateRoom[0], ", stains- ", self.stateRoom[1], ", fruits- ", self.stateRoom[2])