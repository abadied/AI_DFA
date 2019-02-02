from tkinter import *
import numpy as np
import copy
from AutomatasState import AutomatasState
import time

ROOM = []
INIT_ROOM = []
ROOM_HEIGHT = 0
ROOM_WIDTH = 0
COLOR_DICT = {0: "black", 0.5: "gray", 1: "white", 2: "basket", 3: "banana", 4: "strawberry", 5: "grapes", 8: "stain", 9: "robot"}
OPS = []
TRAN_PROB_MAT = []
OBJECT_IN_ROBOT_POSITION = 1
ALL_STATES = dict()
CURRENT_STATE = []
CURRENT_AUTO_STATE = None
INIT_STATE = []
POLICY = dict()
NUM_OF_PICKED_FRUITS = 0
root = Tk()
root.title("POMDP REDUCTION")
ROBOT_BAR = []
BASKET_BAR = []
FIRST_SHOW = True
FINAL_STATES = ""


def show_room(room, policy, all_states, initial_state, operations, tran_prob_mat, final_state, dfa_dict):
    global ROOM, INIT_ROOM, ROOM_HEIGHT, ROOM_WIDTH, OPS, TRAN_PROB_MAT, ALL_STATES, CURRENT_STATE, INIT_STATE, POLICY,\
        c, FIRST_SHOW, FINAL_STATES, CURRENT_AUTO_STATE
    CURRENT_AUTO_STATE = AutomatasState(dfa_dict)
    ROOM = room
    INIT_ROOM = copy.deepcopy(room)
    ROOM_HEIGHT = len(room)
    ROOM_WIDTH = len(room[0])
    OPS = operations
    TRAN_PROB_MAT = tran_prob_mat
    CURRENT_STATE = initial_state
    INIT_STATE = copy.deepcopy(initial_state)
    ALL_STATES = all_states
    POLICY = policy
    FINAL_STATES = final_state
    c = Canvas(root, height=50 * (ROOM_HEIGHT + 3), width=max(50 * ROOM_WIDTH, 300), bg='white', bd=0)

    # creating grid
    for i in range(0, 50 * ROOM_WIDTH, 50):
        c.create_line([(i, 0), (i, 50 * ROOM_HEIGHT)])
    for i in range(0, 50 * ROOM_HEIGHT, 50):
        c.create_line([(0, i), (50 * ROOM_WIDTH, i)])

    # by pressing: 'r' the game is stopped (restarted)
    #              'n' we see what the policy orders to do in the next step
    #              'p' shows a full episode
    root.bind('<r>', restart)
    root.bind('<n>', next_move)
    root.bind('<p>', play_episode)

    for i in range(ROOM_HEIGHT):
        for j in range(ROOM_WIDTH):
            create_image(room[i][j], i, j, c)
    create_image(9, ROOM_HEIGHT, 0, c)
    create_image(2, ROOM_HEIGHT + 1, 0, c)
    for i in range(ROOM_WIDTH):
        create_image(0.5, ROOM_HEIGHT + 2, i, c)

    coords1 = (1, 50 * ROOM_HEIGHT + 100, 100, 50 * ROOM_HEIGHT + 199)
    coords2 = (100, 50 * ROOM_HEIGHT + 100, 200, 50 * ROOM_HEIGHT + 199)
    coords3 = (200, 50 * ROOM_HEIGHT + 100, 300, 50 * ROOM_HEIGHT + 199)

    item1 = c.create_rectangle(coords1, outline="black", fill="red")
    item4 = c.create_text(50, 50 * ROOM_HEIGHT + 125, fill="black", font="Times 14 italic bold", text="restart")
    c.tag_bind(item1, "<1>", restart)
    c.tag_bind(item4, "<1>", restart)

    item2 = c.create_rectangle(coords2, outline="black", fill="yellow")
    item5 = c.create_text(150, 50 * ROOM_HEIGHT + 125, fill="black", font="Times 14 italic bold", text="next move")
    c.tag_bind(item2, "<1>", next_move)
    c.tag_bind(item5, "<1>", next_move)

    item3 = c.create_rectangle(coords3, outline="black", fill="green")
    item6 = c.create_text(250, 50 * ROOM_HEIGHT + 125, fill="black", font="Times 14 italic bold", text="play episode")
    c.tag_bind(item3, "<1>", play_episode)
    c.tag_bind(item6, "<1>", play_episode)

    if FIRST_SHOW:
        c.delete()
    FIRST_SHOW = False
    c.pack()
    root.mainloop()


def create_image(image_num, row, col, c):
    "paints the image imageName in [row][col] square."
    if image_num in [0, 1]:
        c.create_rectangle(col * 50, row * 50, (col + 1) * 50, (row + 1) * 50, fill=COLOR_DICT[image_num])
    elif image_num == 0.5:
        c.create_rectangle(col * 50, row * 50, (col + 1) * 50, (row + 1) * 50, fill=COLOR_DICT[image_num], outline = COLOR_DICT[0.5])
    elif image_num == 0.99:
        c.create_rectangle(col * 50, row * 50 + 1, (col + 1) * 50, (row + 1) * 50 - 1, fill=COLOR_DICT[1], outline = COLOR_DICT[1])
    else:
        strTemp = "gif_pictures/" + COLOR_DICT[image_num] + ".gif"
        filename = PhotoImage(file="gif_pictures/" + COLOR_DICT[image_num] + ".gif")
        image = c.create_image(col * 50 + 25, row * 50 + 25, image=filename)
        if image_num == 9:  # robot => therefore the position update
            currentPosition = row, col
        label = Label(image=filename)
        label.image = filename


def restart(event):
    print("Reseting game")
    global ROOM, INIT_ROOM, CURRENT_STATE, INIT_STATE, OBJECT_IN_ROBOT_POSITION, ROBOT_BAR, BASKET_BAR, NUM_OF_PICKED_FRUITS, CURRENT_AUTO_STATE
    ROOM = copy.deepcopy(INIT_ROOM)
    CURRENT_STATE = copy.deepcopy(INIT_STATE)
    CURRENT_AUTO_STATE.reset()
    OBJECT_IN_ROBOT_POSITION = 1
    ROBOT_BAR = []
    BASKET_BAR = []
    NUM_OF_PICKED_FRUITS = 0
    for i in range(ROOM_HEIGHT):
        for j in range(ROOM_WIDTH):
            if ROOM[i][j] == 0:
                create_image(0, i, j, c)
            else:
                create_image(1, i, j, c)
    for i in range(ROOM_HEIGHT):
        for j in range(ROOM_WIDTH):
            create_image(ROOM[i][j], i, j, c)
    create_image(9, ROOM_HEIGHT, 0, c)
    create_image(2, ROOM_HEIGHT + 1, 0, c)
    for i in range(ROOM_WIDTH - 1):
        create_image(0.99, ROOM_HEIGHT, i + 1, c)
        create_image(0.99, ROOM_HEIGHT + 1, i + 1, c)


def next_move(event):
    take_next_move()


# def take_next_move():
#     global CURRENT_STATE, POLICY
#     actionTried = POLICY[CURRENT_STATE.hash]
#     actionIndex = OPS.index(POLICY[CURRENT_STATE.hash])
#     sample = np.random.uniform(0.000000001, 1.)
#     sumProb = 0
#     for i in range(len(OPS)):
#         sumProb += TRAN_PROB_MAT[actionIndex][i]
#         if sumProb > sample:
#             realActionIndex = i
#             break
#     if CURRENT_STATE.legal_op(OPS[realActionIndex]):
#         execute_action(OPS[realActionIndex])
#         CURRENT_STATE = CURRENT_STATE.next_state(OPS[realActionIndex])
#     print("tried to do: ", actionTried, ", action taken: ", OPS[realActionIndex])
#     return

def take_next_move():
    global CURRENT_STATE, POLICY, CURRENT_AUTO_STATE
    actionTried = POLICY[str(CURRENT_AUTO_STATE.get_state_key())]
    actionIndex = OPS.index(POLICY[str(CURRENT_AUTO_STATE.get_state_key())])
    sample = np.random.uniform(0.000000001, 1.)
    sumProb = 0
    for i in range(len(OPS)):
        sumProb += TRAN_PROB_MAT[actionIndex][i]
        if sumProb > sample:
            realActionIndex = i
            break
    if CURRENT_STATE.is_end():
        execute_action(OPS[-1])

    elif CURRENT_STATE.legal_op(OPS[realActionIndex]):
        execute_action(OPS[realActionIndex])
        CURRENT_STATE = CURRENT_STATE.next_state(OPS[realActionIndex])
        observation = CURRENT_STATE.get_observation()
        CURRENT_AUTO_STATE.next_state(OPS[realActionIndex], observation)
    print("tried to do: ", actionTried, ", action taken: ", OPS[realActionIndex])
    return


def play_episode(event):
    global CURRENT_STATE, POLICY, FINAL_STATES
    while True:
        c.update_idletasks()
        take_next_move()
        time.sleep(0.25)
        if CURRENT_STATE.hash in FINAL_STATES:
            break


def execute_action(action):
    if action in ["up", "down", "left", "right"]:
        move_robot(action, CURRENT_STATE.state_room[0][0], CURRENT_STATE.state_room[0][1])
    elif action in ["clean", "pick", "putInBasket"]:
        non_move_action(CURRENT_STATE.state_room[0][0], CURRENT_STATE.state_room[0][1], action)


def move_robot(direction, row, col):
    global ROOM, OBJECT_IN_ROBOT_POSITION, c
    create_image(OBJECT_IN_ROBOT_POSITION, row, col, c)
    ROOM[row][col] = OBJECT_IN_ROBOT_POSITION
    if direction == "up":
        OBJECT_IN_ROBOT_POSITION = ROOM[row - 1][col]
        ROOM[row - 1][col] = 9
        create_image(9, row - 1, col, c)
    elif direction == "down":
        OBJECT_IN_ROBOT_POSITION = ROOM[row + 1][col]
        ROOM[row + 1][col] = 9
        create_image(9, row + 1, col, c)
    elif direction == "left":
        OBJECT_IN_ROBOT_POSITION = ROOM[row][col - 1]
        ROOM[row][col - 1] = 9
        create_image(9, row, col - 1, c)
    elif direction == "right":
        OBJECT_IN_ROBOT_POSITION = ROOM[row][col + 1]
        ROOM[row][col + 1] = 9
        create_image(9, row, col + 1, c)


def non_move_action(row, col, action):
    global OBJECT_IN_ROBOT_POSITION, NUM_OF_PICKED_FRUITS, ROBOT_BAR, BASKET_BAR
    if (action == "clean" and ROOM[row][col] in [3, 4, 5]) or (action == "pick" and ROOM[row][col] == 8):
        return
    if action in ["clean", "pick"]:
        create_image(1, row, col, c)
        create_image(9, row, col, c)
    if action == "pick":
        NUM_OF_PICKED_FRUITS += 1
        ROBOT_BAR.append(OBJECT_IN_ROBOT_POSITION)
        create_image(OBJECT_IN_ROBOT_POSITION, ROOM_HEIGHT, NUM_OF_PICKED_FRUITS, c)
    OBJECT_IN_ROBOT_POSITION = 1
    if action == "putInBasket":
        OBJECT_IN_ROBOT_POSITION = 2
        numOfObjects = len(ROBOT_BAR)
        for object in range(numOfObjects):
            BASKET_BAR.append(ROBOT_BAR[object])
        ROBOT_BAR = []
        NUM_OF_PICKED_FRUITS = 0
        #erasing robot's bar
        c.create_rectangle(50, ROOM_HEIGHT * 50 + 1, (ROOM_WIDTH) * 50, (ROOM_HEIGHT + 1) * 50, fill=COLOR_DICT[1], outline="white")
        for object in range(len(BASKET_BAR)): #creating basket bar
            create_image(BASKET_BAR[object], ROOM_HEIGHT + 1, object + 1, c)