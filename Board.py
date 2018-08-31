import random
import copy

room = []     #do not change here
roomHeight = 5 # walls included
roomWidth = 5 # walls included
OPS = ["up", "down", "left", "right", "clean", "pick", "putInBasket", "random", "idle"]
ROBOT_POSITION = 2, 1
BASKET_POSITION = [1, 2] #don't comment for all algorithms. can be changed.
# the i-j cell in the transition probability matrix indicates the probability to do action j given that the chosen action is i
# the matrix is ordered according to the order in OPS
TRAN_PROB_MAT = [[0.8, 0, 0.1, 0.1, 0, 0, 0, 0, 0],
                 [0, 0.8, 0.1, 0.1, 0, 0, 0, 0, 0],
                 [0.1, 0.1, 0.8, 0, 0, 0, 0, 0, 0],
                 [0.1, 0.1, 0, 0.8, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0.8, 0, 0, 0, 0.2],
                 [0, 0, 0, 0, 0, 0.8, 0, 0, 0.2],
                 [0, 0, 0, 0, 0, 0, 0.8, 0, 0.2],
                 [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0, 0.125],
                 [0, 0, 0, 0, 0, 0, 0, 0, 1]]

# for debugging purposes, you might want to use this deterministic transition probabilities matrix
# TRAN_PROB_MAT = [[1, 0, 0, 0, 0, 0, 0, 0, 0],
#                  [0, 1, 0, 0, 0, 0, 0, 0, 0],
#                  [0, 0, 1, 0, 0, 0, 0, 0, 0],
#                  [0, 0, 0, 1, 0, 0, 0, 0, 0],
#                  [0, 0, 0, 0, 1, 0, 0, 0, 0],
#                  [0, 0, 0, 0, 0, 1, 0, 0, 0],
#                  [0, 0, 0, 0, 0, 0, 1, 0, 0],
#                  [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0, 0.125],
#                  [0, 0, 0, 0, 0, 0, 0, 0, 1]]


DISCOUNT = 0.9

# these credits are for the dynamic programming solution
CLEANING_CREDIT = 10.
PICKING_CREDIT = 5.
PUTTING_CREDIT = 20.
FINISHING_CREDIT = 100.
NONE_MARKOVIAN_REWARD = 10000
MOVE_COST = 1.

def initRoom():
    for i in range(roomHeight):
        newRow = [0] * roomWidth
        room.append(newRow)
    for i in range(1, roomHeight - 1):
        for j in range(1, roomWidth - 1):
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
def scatteringStains():
    i = 1
    # while i <= (int)(math.sqrt(roomHeight * roomWidth)/2):
    #     num1 = random.randint(1, roomHeight - 2)
    #     num2 = random.randint(1, roomWidth - 2)
    #     if room[num1][num2] == 1:
    #         room[num1][num2] = 8
    #         i += 1
    room[1][1] = 8

# refer the guide
def scatteringFruits():
    i = 1
    # while i <= min(((int)(math.sqrt(roomHeight * roomWidth) / 2)), len(room[0]) - 1, 5):
    #     num1 = random.randint(1, roomHeight - 2)
    #     num2 = random.randint(1, roomWidth - 2)
    #     if room[num1][num2] == 1:
    #         room[num1][num2] = random.randint(3, 5)
    #         i += 1
    room[3][3] = random.randint(3,5)

initRoom()
initialRoom = copy.deepcopy(room)
scatteringStains()
scatteringFruits()

def printRoom(r):
    'prints the current room representation (for debugging)'
    for i in range((len(r))):
        print(r[i])