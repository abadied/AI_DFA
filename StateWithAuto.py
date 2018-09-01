import copy
import Board as bd


class StateWithAuto:
    """This class represents a specific state of the game combined with the state in the automaton. 
       it contains all parameters to fully characterize specific pair"""

    def __init__(self, dfa, state_in_room_param, room_param):
        """

        :type dfa: DFA
        """
        self.state_in_room = state_in_room_param
        self.state_room = self.state_in_room.state_room
        self.state_in_auto = dfa.Initial
        self.dfa = dfa
        self.room = room_param
        self.state_pair = copy.deepcopy(self.state_in_room.stateRoom)
        self.state_pair.append(sorted(list(self.state_in_auto)))
        self.hash = repr(self.state_pair)    # each (stateInRoom, stateInAuto) pair has a string that is it's name (and it's unique)
        self.end = len(self.state_in_room.state_room[1]) == 0 \
                   and len(self.state_in_room.state_room[2]) == 0 \
                   and self.state_in_room.state_oom[3] == 0

    def is_end(self):
        return self.end

    def next_state(self, op):
        "givan a pair state and a legal operation, returns the next pair state"
        if op == "idle":
            return self
        new_auto_state = StateWithAuto(self.dfa, self.state_in_room, self.room)
        new_state_in_room = self.state_in_room.next_state(op)
        new_state_in_auto = self.dfa.evalSymbol(self.state_in_auto, op[0])
        new_auto_state.state_in_room = new_state_in_room
        new_auto_state.state_room = new_auto_state.state_in_room.stateRoom
        new_auto_state.state_in_auto = new_state_in_auto
        new_auto_state.state_pair = copy.deepcopy(new_auto_state.state_in_room.stateRoom)
        new_auto_state.state_pair.append(sorted(list(new_auto_state.state_in_auto)))
        new_auto_state.hash = repr(new_auto_state.state_pair)
        return new_auto_state

    def legal_op(self, op):
        if op == "idle":
            return True
        if self.is_end():
            return False
        row_position_of_robot = self.state_in_room.stateRoom[0][0]
        col_position_of_robot = self.state_in_room.stateRoom[0][1]
        occupied = [0, 7, 10]   # these numbers represent wall, basket, cabinet and man appropriately
        if op == "up" and self.room[row_position_of_robot - 1][col_position_of_robot] not in occupied:
            return True
        elif op == "down" and self.room[row_position_of_robot + 1][col_position_of_robot] not in occupied:
            return True
        elif op == "left" and self.room[row_position_of_robot][col_position_of_robot - 1] not in occupied:
            return True
        elif op == "right" and self.room[row_position_of_robot][col_position_of_robot + 1] not in occupied:
            return True
        elif op in ["clean", "pick"]:
            return True
        elif op == "putInBasket" and self.state_room[0] == bd.BASKET_POSITION:
            return True
        return False

    def print_state(self):
        """
        just for debug"
        :return:
        """
        print("State in board:\trobot: ", self.state_in_room.stateRoom[0], ", stains: ", self.state_in_room.stateRoom[1], ", fruits: ", self.state_in_room.stateRoom[2], \
              "State in auto:\t", self.dfa.States[self.state_in_auto])