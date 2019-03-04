
from tkinter import *
import numpy as np
import copy
from AutomatasState import AutomatasState
import time
import os

class Room(object):
    def __init__(self, room, policy, all_states, initial_state, operations, tran_prob_mat, final_state, dfa_dict):
        self.color_dict = {0: "black", 0.5: "gray", 1: "white", 2: "basket", 3: "banana", 4: "strawberry", 5: "grapes",
                           8: "stain", 9: "robot"}
        self.object_in_robot_pos = 1
        self.num_of_picked_fruits = 0
        self.root = Toplevel()
        self.root.title("POMDP REDUCTION")
        self.robot_bar = []
        self.basket_bar = []
        self.first_show = True
        self.current_auto_state = AutomatasState(dfa_dict)
        self.room = room
        self.init_room = copy.deepcopy(room)
        self.room_height = len(room)
        self.room_width = len(room[0])
        self.ops = operations
        self.tran_prob_matrix = tran_prob_mat
        self.current_state = copy.deepcopy(initial_state)
        self.init_state = copy.deepcopy(initial_state)
        self.all_states = all_states
        self.policy = policy
        self.final_states = final_state
        self.canvas = None

    def show_room(self):

        self.canvas = Canvas(self.root, height=50 * (self.room_height + 3), width=max(50 * self.room_width, 300), bg='white', bd=0)

        # creating grid
        for i in range(0, 50 * self.room_width, 50):
            self.canvas.create_line([(i, 0), (i, 50 * self.room_height)])
        for i in range(0, 50 * self.room_height, 50):
            self.canvas.create_line([(0, i), (50 * self.room_width, i)])

        # by pressing: 'r' the game is stopped (restarted)
        #              'n' we see what the policy orders to do in the next step
        #              'p' shows a full episode
        self.root.bind('<r>', self.restart)
        self.root.bind('<n>', self.next_move)
        self.root.bind('<p>', self.play_episode)

        for i in range(self.room_height):
            for j in range(self.room_width):
                self.create_image(self.room[i][j], i, j)
        self.create_image(9, self.room_height, 0)
        self.create_image(2, self.room_height + 1, 0)
        for i in range(self.room_width):
            self.create_image(0.5, self.room_height + 2, i)

        coords1 = (1, 50 * self.room_height + 100, 100, 50 * self.room_height + 199)
        coords2 = (100, 50 * self.room_height + 100, 200, 50 * self.room_height + 199)
        coords3 = (200, 50 * self.room_height + 100, 300, 50 * self.room_height + 199)

        item1 = self.canvas.create_rectangle(coords1, outline="black", fill="red")
        item4 = self.canvas.create_text(50, 50 * self.room_height + 125, fill="black", font="Times 14 italic bold", text="restart")
        self.canvas.tag_bind(item1, "<1>", self.restart)
        self.canvas.tag_bind(item4, "<1>", self.restart)

        item2 = self.canvas.create_rectangle(coords2, outline="black", fill="yellow")
        item5 = self.canvas.create_text(150, 50 * self.room_height + 125, fill="black", font="Times 14 italic bold",
                                        text="next move")
        self.canvas.tag_bind(item2, "<1>", self.next_move)
        self.canvas.tag_bind(item5, "<1>", self.next_move)

        item3 = self.canvas.create_rectangle(coords3, outline="black", fill="green")
        item6 = self.canvas.create_text(250, 50 * self.room_height + 125, fill="black", font="Times 14 italic bold",
                                        text="play episode")
        self.canvas.tag_bind(item3, "<1>", self.play_episode)
        self.canvas.tag_bind(item6, "<1>", self.play_episode)

        if self.first_show:
            self.canvas.delete()
        self.first_show = False
        self.canvas.pack()
        self.root.mainloop()

    def create_image(self, image_num, row, col):
        "paints the image imageName in [row][col] square."
        if image_num in [0, 1]:
            self.canvas.create_rectangle(col * 50, row * 50, (col + 1) * 50, (row + 1) * 50, fill=self.color_dict[image_num])
        elif image_num == 0.5:
            self.canvas.create_rectangle(col * 50, row * 50, (col + 1) * 50, (row + 1) * 50, fill=self.color_dict[image_num],
                                         outline=self.color_dict[0.5])
        elif image_num == 0.99:
            self.canvas.create_rectangle(col * 50, row * 50 + 1, (col + 1) * 50, (row + 1) * 50 - 1, fill=self.color_dict[1],
                                         outline=self.color_dict[1])
        else:
            print(os.getcwd())
            path = "gif_pictures\\" + self.color_dict[image_num] + ".gif"
            filename = PhotoImage(file=path)
            filename = PhotoImage(file="gif_pictures/" + self.color_dict[image_num] + ".gif")
            _ = self.canvas.create_image(col * 50 + 25, row * 50 + 25, image=filename)
            label = Label(image=filename)
            label.image = filename

    def restart(self, event):
        print("Reseting game")
        self.room = copy.deepcopy(self.init_room)
        self.current_state = copy.deepcopy(self.init_state)
        self.current_auto_state.reset()
        self.object_in_robot_pos = 1
        self.robot_bar = []
        self.basket_bar = []
        self.num_of_picked_fruits = 0
        for i in range(self.room_height):
            for j in range(self.room_width):
                if self.room[i][j] == 0:
                    self.create_image(0, i, j)
                else:
                    self.create_image(1, i, j)
        for i in range(self.room_height):
            for j in range(self.room_width):
                self.create_image(self.room[i][j], i, j)
        self.create_image(9, self.room_height, 0)
        self.create_image(2, self.room_height + 1, 0)
        for i in range(self.room_width - 1):
            self.create_image(0.99, self.room_height, i + 1)
            self.create_image(0.99, self.room_height + 1, i + 1)

    def next_move(self, event):
        self.take_next_move()

    def take_next_move(self):
        action_tried = self.policy[str(self.current_auto_state.get_state_key())]
        action_index = self.ops.index(action_tried)
        # sample = np.random.uniform(0.000000001, 1.)
        # sum_prob = 0
        # for i in range(len(self.ops)):
        #     sum_prob += self.tran_prob_matrix[action_index][i]
        #     if sum_prob > sample:
        #         real_action_index = i
        #         break
        real_action_index = action_index
        if self.current_state.is_end():
            self.execute_action(self.ops[-1])
            print('end of maze.')
            return
        # elif CURRENT_STATE.legal_op(OPS[real_action_index]):
        elif self.current_state.new_legal_op(self.ops[real_action_index]):
            temp_new_state = self.current_state.next_state(self.ops[real_action_index])
            self.execute_action(self.ops[real_action_index])
            self.current_state = temp_new_state
            observation = self.current_state.get_observation()
            self.current_auto_state.next_state(self.ops[real_action_index], observation)
            print("tried to do: ", action_tried, ", action taken: ", self.ops[real_action_index])
            return
        else:
            observation = self.current_state.get_observation()
            self.current_auto_state.next_state(self.ops[real_action_index], observation)
            print("tried to do: ", action_tried)

    def play_episode(self, event):
        while True:
            self.canvas.update_idletasks()
            self.take_next_move()
            time.sleep(0.25)
            if self.current_state.hash in self.final_states:
                break

    def execute_action(self, action):
        if action in ["up", "down", "left", "right"]:
            self.move_robot(action, self.current_state.state_room[0][0], self.current_state.state_room[0][1])
        elif action in ["clean", "pick", "putInBasket"]:
            self.non_move_action(self.current_state.state_room[0][0], self.current_state.state_room[0][1], action)

    def move_robot(self, direction, row, col):
        self.create_image(self.object_in_robot_pos, row, col)
        self.room[row][col] = self.object_in_robot_pos
        if direction == "up":
            self.object_in_robot_pos = self.room[row - 1][col]
            self.room[row - 1][col] = 9
            self.create_image(9, row - 1, col)
        elif direction == "down":
            self.object_in_robot_pos = self.room[row + 1][col]
            self.room[row + 1][col] = 9
            self.create_image(9, row + 1, col)
        elif direction == "left":
            self.object_in_robot_pos = self.room[row][col - 1]
            self.room[row][col - 1] = 9
            self.create_image(9, row, col - 1)
        elif direction == "right":
            self.object_in_robot_pos = self.room[row][col + 1]
            self.room[row][col + 1] = 9
            self.create_image(9, row, col + 1)

    def non_move_action(self, row, col, action):
        if (action == "clean" and self.room[row][col] in [2, 3, 4, 5]) or (action == "pick" and self.room[row][col] == 8):
            return
        if action in ["clean", "pick"]:
            self.create_image(1, row, col)
            self.create_image(9, row, col)
        if action == "pick":
            self.num_of_picked_fruits += 1
            self.robot_bar.append(self.object_in_robot_pos)
            self.create_image(self.object_in_robot_pos, self.room_height, self.num_of_picked_fruits)
        self.object_in_robot_pos = 1
        if action == "putInBasket":
            self.object_in_robot_pos = 2
            num_of_objects = len(self.robot_bar)
            for object in range(num_of_objects):
                self.basket_bar.append(self.robot_bar[object])
            self.robot_bar = []
            self.num_of_picked_fruits = 0
            # erasing robot's bar
            self.canvas.create_rectangle(50, self.room_height * 50 + 1, self.room_width * 50, (self.room_height + 1) * 50,
                                         fill=self.color_dict[1], outline="white")
            for _object in range(len(self.basket_bar)):  # creating basket bar
                self.create_image(self.basket_bar[_object], self.room_height + 1, _object + 1)