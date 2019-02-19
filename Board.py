import random
import copy

room = []   # do not change here
room_height = 3  # walls included
room_width = 6  # walls included
# OPS = ["up", "down", "left", "right", "clean", "pick", "putInBasket", "random", "idle"]
# OPS = ["up", "down", "left", "right", "clean", "pick", "putInBasket", "idle"]
OPS = ["up", "down", "left", "right", "clean", "pick", "putInBasket"]

ROBOT_POSITION = 1, 1
BASKET_POSITION = [1, 2]    # don't comment for all algorithms. can be changed.

# the i-j cell in the transition probability matrix indicates the probability to do action j
# given that the chosen action is i
# the matrix is ordered according to the order in OPS
# TRAN_PROB_MAT = [[0.8, 0, 0.1, 0.1, 0, 0, 0, 0, 0],
#                  [0, 0.8, 0.1, 0.1, 0, 0, 0, 0, 0],
#                  [0.1, 0.1, 0.8, 0, 0, 0, 0, 0, 0],
#                  [0.1, 0.1, 0, 0.8, 0, 0, 0, 0, 0],
#                  [0, 0, 0, 0, 0.8, 0, 0, 0, 0.2],
#                  [0, 0, 0, 0, 0, 0.8, 0, 0, 0.2],
#                  [0, 0, 0, 0, 0, 0, 0.8, 0, 0.2],
#                  [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0, 0.125],
#                  [0, 0, 0, 0, 0, 0, 0, 0, 1]]

# TRAN_PROB_MAT = [[0.8, 0, 0.1, 0.1, 0, 0, 0, 0],
#                  [0, 0.8, 0.1, 0.1, 0, 0, 0, 0],
#                  [0.1, 0.1, 0.8, 0, 0, 0, 0, 0],
#                  [0.1, 0.1, 0, 0.8, 0, 0, 0, 0],
#                  [0, 0, 0, 0, 0.8, 0, 0, 0.2],
#                  [0, 0, 0, 0, 0, 0.8, 0, 0.2],
#                  [0, 0, 0, 0, 0, 0, 0.8, 0.2],
#                  [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125],
#                  [0, 0, 0, 0, 0, 0, 0, 1]]

# for debugging purposes, you might want to use this deterministic transition probabilities matrix
TRAN_PROB_MAT = [[1, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 1, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 1, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 1, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 1, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 1, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 1, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 1, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 1]]


DISCOUNT = 0.9

# these credits are for the dynamic programming solution
CLEANING_CREDIT = 10.
PICKING_CREDIT = 5.
PUTTING_CREDIT = 20.
FINISHING_CREDIT = 100.
MOVE_COST = 1.


def init_room():
    for i in range(room_height):
        new_row = [0] * room_width
        room.append(new_row)
    for i in range(1, room_height - 1):
        for j in range(1, room_width - 1):
            room[i][j] = 1
    # walls = []
    # for i in range(1, roomWidth/2 - 2):
    #     walls.append([roomHeight / 2, i])
    # for i in range(1, roomHeight/2 + 1):
    #     walls.append([i, roomWidth / 2])
    # for i in range(2):
    #     walls.append([roomHeight / 2, i + roomWidth/2 + 1])
    # for i in range(roomHeight / 2 + 3, roomHeight):
    #     walls.append([i, roomWidth / 2 + 2])
    # for [i, j] in walls:
    #     room[i][j] = 0
    room[ROBOT_POSITION[0]][ROBOT_POSITION[1]] = 9  # initial robot's location
    room[BASKET_POSITION[0]][BASKET_POSITION[1]] = 2  # initial basket's location


# refer the guide
def scattering_stains():
    i = 1
    # while i <= (int)(math.sqrt(roomHeight * roomWidth)/2):
    #     num1 = random.randint(1, roomHeight - 2)
    #     num2 = random.randint(1, roomWidth - 2)
    #     if room[num1][num2] == 1:
    #         room[num1][num2] = 8
    #         i += 1
    room[1][3] = 8


# refer the guide
def scattering_fruits():
    i = 1
    # while i <= min(((int)(math.sqrt(roomHeight * roomWidth) / 2)), len(room[0]) - 1, 5):
    #     num1 = random.randint(1, roomHeight - 2)
    #     num2 = random.randint(1, roomWidth - 2)
    #     if room[num1][num2] == 1:
    #         room[num1][num2] = random.randint(3, 5)
    #         i += 1
    # room[3][3] = random.randint(3, 5)


init_room()
initial_room = copy.deepcopy(room)
scattering_stains()
scattering_fruits()


def print_room(r):
    'prints the current room representation (for debugging)'
    for i in range((len(r))):
        print(r[i])