from Board import *
import numpy as np


class State:

    """This class represents a specific state of the game. it contains all parameters to fully
    characterize specific situation"""

    def __init__(self):
        self.state_room = [[ROBOT_POSITION[0], ROBOT_POSITION[1]]]  # list of lists: lists for the robot coordinates, stains and fruits location
        stains = []
        fruits = []
        carried_fruits = 0  # num of fruits the robot is holding
        for i in range(len(room)):
            for j in range(len(room[0])):
                if room[i][j] == 8:
                    stains.append([i, j])
                if room[i][j] in [3, 4, 5]:
                    fruits.append([i, j])
        self.state_room.append(stains)
        self.state_room.append(fruits)
        self.state_room.append(carried_fruits)
        self.hash = repr(self.state_room)  # each stateRoom has a string that is it's name (and it's unique)
        self.end = len(self.state_room[1]) == 0 and len(self.state_room[2]) == 0 and self.state_room[3] == 0

    def is_end(self):
        """
        returns true iff self is a final state
        :return:
        """
        return self.end

    def next_state(self, op):
        """
        givan a state and an operation, returns the next room's state
        :param op:
        :return:
        """
        if not self.legal_op(op):
            return self

        new_state = State()
        new_state.state_room = copy.deepcopy(self.state_room[:])  # deep copy
        if op == "up":
            new_state.state_room[0][0] = self.state_room[0][0] - 1
        elif op == "down":
            new_state.state_room[0][0] = self.state_room[0][0] + 1
        elif op == "left":
            new_state.state_room[0][1] = self.state_room[0][1] - 1
        elif op == "right":
            new_state.state_room[0][1] = self.state_room[0][1] + 1
        elif op == "clean":  # remove a stain from the current position only if there's a stain there
            if self.state_room[0] in self.state_room[1]:
                index = self.state_room[1].index(self.state_room[0])
                new_state.state_room[1] = new_state.state_room[1][0:index] + new_state.state_room[1][index + 1:]
                new_state.end = new_state.is_end()
            else:
                return self
        elif op == "pick":  # pick a fruit from the current position only if there's a fruit there
            if self.state_room[0] in self.state_room[2]:
                index = self.state_room[2].index(self.state_room[0])
                new_state.state_room[2] = new_state.state_room[2][0:index] + new_state.state_room[2][index + 1:]
                new_state.state_room[3] += 1
                new_state.end = new_state.is_end()
            else:
                return self
        elif op == "putInBasket":  # legalOp prevents putInBasket not in the basket
            new_state.state_room[3] = 0
            new_state.end = new_state.is_end()
        elif op == "idle":
            return self
        elif op == "random":
            legal_ops = [op for op in OPS if self.legal_op(op)]
            return self.next_state(np.random.choice(legal_ops))
        new_state.hash = repr(new_state.state_room)
        return new_state

    def probablistic_next_state(self, op):
        """givan a state and an operation to apply, computes a possible action to take by the TRAN_PROB_MAT imported from Board.py 
            and returns the next room's state after applying the actual action"""
        global TRAN_PROB_MAT
        action_index = OPS.index(op)
        sample = np.random.uniform(0.000000001, 1.)
        sum_prob = 0
        for i in range(len(OPS)):
            sum_prob += TRAN_PROB_MAT[action_index][i]
            if sum_prob > sample:
                real_action_index = i
                break
        actual_op = OPS[real_action_index]
        return self.next_state(actual_op)

    def legal_op(self, op):
        """
        returns true iff @op is legal in @self state
        :param op:
        :return:
        """
        if op == "idle":
            return True
        if self.is_end():
            return False
        row_position_of_robot = self.state_room[0][0]
        col_position_of_robot = self.state_room[0][1]
        occupied = [0, 7, 10]  # these numbers represent wall, basket, cabinet and man appropriately
        if op == "up" and room[row_position_of_robot - 1][col_position_of_robot] not in occupied:
            return True
        elif op == "down" and room[row_position_of_robot + 1][col_position_of_robot] not in occupied:
            return True
        elif op == "left" and room[row_position_of_robot][col_position_of_robot - 1] not in occupied:
            return True
        elif op == "right" and room[row_position_of_robot][col_position_of_robot + 1] not in occupied:
            return True
        elif op in ["clean", "pick"]:
            return True
        elif op == "putInBasket" and self.state_room[0] == BASKET_POSITION:
            return True
        return False

    def get_observation(self):
        """
        return the state observation with certain probability
        :return: observation string
        """
        row_pos = self.state_room[0][0]
        col_pos = self.state_room[0][1]
        if row_pos == 0:
            if col_pos == 0:
                return 'x'
            if col_pos == room_width:
                return 'z'
            return 'e'
        elif row_pos == room_height:
            if col_pos == 0:
                return 'y'
            if col_pos == room_width:
                return 'a'
            return 't'
        elif col_pos == 0:
            return 'q'
        elif col_pos == room_width:
            return 'w'
        return 'n'

    def print_state(self):
        """
        prints a string representation of the state
        :return:
        """
        print("State: robot- ", self.state_room[0], ", stains- ", self.state_room[1], ", fruits- ", self.state_room[2])