letter_value_dictionary = {"u": "up",
                           "d": "down",
                           "l": "left",
                           "r": "right",
                           "c": "clean",
                           "p": "pick",
                           "i": "idle",
                           "k": "putInBasket",
                           "w": "right_wall",
                           "q": "left_wall",
                           "e": "upper_wall",
                           "t": "downer_wall",
                           "x": "left_up_wall",
                           "y": "left_down_wall",
                           "z": "right_up_wall",
                           "a": "right_down_wall",
                           "v": "left_right_wall",
                           "j": "upper_downer_wall",
                           "n": "no_walls",
                           "f": "up_down_right_wall",
                           "s": "up_down_left_wall",
                           "b": "right_left_down_wall",
                           "m": "right_left_up_wall",
                           "g": "all_walls"}
value_letter_dictionary = {letter_value_dictionary[key]: key for key in letter_value_dictionary.keys()}

credits = {'pick': 5, 'clean': 10, 'putInBasket': 20}
OPS = ["up", "down", "left", "right", "clean", "pick", "putInBasket", "idle"]


# optimization_algorithm = 'policy_iteration'
optimization_algorithm = 'q_learning'