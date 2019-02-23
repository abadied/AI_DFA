from Board import *
import numpy as np
import random
import math

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
        self.state_room.append(stains)          # index 1
        self.state_room.append(fruits)          # index 2
        self.state_room.append(carried_fruits)  # index 3
        self.hash = repr(self.state_room)  # each stateRoom has a string that is it's name (and it's unique)
        self.end = len(self.state_room[1]) == 0 and len(self.state_room[2]) == 0 and self.state_room[3] == 0

    def get_possible_actions(self):
        possible_actions = []
        for op in OPS:
            if self.new_legal_op(op):
                possible_actions.append(op)
        return possible_actions

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
        if not self.new_legal_op(op):
            return copy.deepcopy(self)

        new_state = State()
        new_state.state_room = copy.deepcopy(self.state_room[:])  # deep copy
        if op == "up":
            new_state.state_room[0][0] = self.state_room[0][0] - 1
            new_state.end = len(new_state.state_room[1]) == 0 and len(new_state.state_room[2]) == 0 and \
                            new_state.state_room[3] == 0

        elif op == "down":
            new_state.state_room[0][0] = self.state_room[0][0] + 1
            new_state.end = len(new_state.state_room[1]) == 0 and len(new_state.state_room[2]) == 0 and \
                            new_state.state_room[3] == 0

        elif op == "left":
            new_state.state_room[0][1] = self.state_room[0][1] - 1
            new_state.end = len(new_state.state_room[1]) == 0 and len(new_state.state_room[2]) == 0 and \
                            new_state.state_room[3] == 0

        elif op == "right":
            new_state.state_room[0][1] = self.state_room[0][1] + 1
            new_state.end = len(new_state.state_room[1]) == 0 and len(new_state.state_room[2]) == 0 and \
                            new_state.state_room[3] == 0

        elif op == "clean":  # remove a stain from the current position only if there's a stain there
            if self.state_room[0] in self.state_room[1]:
                index = self.state_room[1].index(self.state_room[0])
                new_state.state_room[1] = new_state.state_room[1][0:index] + new_state.state_room[1][index + 1:]
                new_state.end = len(new_state.state_room[1]) == 0 and len(new_state.state_room[2]) == 0 and new_state.state_room[3] == 0
            else:
                return copy.deepcopy(self)
        elif op == "pick":  # pick a fruit from the current position only if there's a fruit there
            if self.state_room[0] in self.state_room[2]:
                index = self.state_room[2].index(self.state_room[0])
                new_state.state_room[2] = new_state.state_room[2][0:index] + new_state.state_room[2][index + 1:]
                new_state.state_room[3] += 1
                new_state.end = len(new_state.state_room[1]) == 0 and len(new_state.state_room[2]) == 0 and new_state.state_room[3] == 0
            else:
                return copy.deepcopy(self)
        elif op == "putInBasket":  # legalOp prevents putInBasket not in the basket
            new_state.state_room[3] = 0
            new_state.end = len(new_state.state_room[1]) == 0 and len(new_state.state_room[2]) == 0 and new_state.state_room[3] == 0
        elif op == "idle":
            return copy.deepcopy(self)
        elif op == "random":
            legal_ops = [op for op in OPS if self.new_legal_op(op)]
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
        real_action_index = None
        for i in range(len(OPS)):
            sum_prob += TRAN_PROB_MAT[action_index][i]
            if sum_prob > sample:
                real_action_index = i
                break
        if real_action_index:
            actual_op = OPS[real_action_index]
        else:
            raise ValueError("Un valid action index!")
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
        elif op == "putInBasket" and self.state_room[0] == BASKET_POSITION and self.state_room[3] > 0:
            return True
        return False

    def new_legal_op(self, op):
        """
        returns true iff @op is legal in @self state
        :param op:
        :return:
        """
        if op == "idle" and self.is_end():
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
        elif op == "clean":# and [row_position_of_robot, col_position_of_robot] in self.state_room[1]:
            return True
        elif op == "pick" and [row_position_of_robot, col_position_of_robot] in self.state_room[2]:
            return True
        elif op == "putInBasket" and self.state_room[0] == BASKET_POSITION and self.state_room[3] > 0:
            return True
        return False

    def get_observation(self):
        """
        return the state observation with certain probability
        :return: observation string
        """
        # TODO: add probabilities to observations
        row_pos = self.state_room[0][0]
        col_pos = self.state_room[0][1]
        right_wall = room[row_pos][col_pos + 1] == 0
        left_wall = room[row_pos][col_pos - 1] == 0
        upper_wall = room[row_pos - 1][col_pos] == 0
        downer_wall = room[row_pos + 1][col_pos] == 0

        obs_dict = {"w": right_wall and not left_wall and not upper_wall and not downer_wall,     # "right_wall"
                    "q": left_wall and not right_wall and not upper_wall and not downer_wall,     # "left_wall"
                    "e": upper_wall and not left_wall and not right_wall and not downer_wall,     # "upper_wall"
                    "t": downer_wall and not left_wall and not upper_wall and not right_wall,     # "downer_wall"
                    "x": left_wall and upper_wall and not right_wall and not downer_wall,         # "left_up_wall"
                    "y": left_wall and downer_wall and not upper_wall and not right_wall,         # "left_down_wall"
                    "z": right_wall and upper_wall and not left_wall and not downer_wall,         # "right_up_wall"
                    "a": right_wall and downer_wall and not upper_wall and not left_wall,         # "right_down_wall"
                    "v": right_wall and left_wall and not upper_wall and not downer_wall,         # "left_right_wall"
                    "j": upper_wall and downer_wall and not left_wall and not right_wall,         # "upper_downer_wall"
                    "f": upper_wall and downer_wall and not left_wall and right_wall,             # "up_down_right_wall"
                    "s": upper_wall and downer_wall and left_wall and not right_wall,             # "up_down_left_wall"
                    "b": not upper_wall and downer_wall and left_wall and right_wall,             # "right_left_down_wall"
                    "m": upper_wall and not downer_wall and left_wall and right_wall,             # "right_left_up_wall"
                    "n": not right_wall and not left_wall and not upper_wall and not downer_wall} # "no_walls"

        for key, val in obs_dict.items():
            if val:
                return key

        raise ValueError('unknown observation event')

    def print_state(self):
        """
        prints a string representation of the state
        :return:
        """
        print("State: robot- ", self.state_room[0], ", stains- ", self.state_room[1], ", fruits- ", self.state_room[2])

    def get_possible_rand_action(self):
        """
        returns possible action for curr state
        :return: action
        """

        rand = random.randint(0, len(self.get_possible_actions()) - 1)
        return self.get_possible_actions()[rand]


