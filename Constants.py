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
                           "n": "no_walls",
                           "f": "fruit",
                           "s": "stain",
                           "b": "basket",
                           "m": "end"}
value_letter_dictionary = {letter_value_dictionary[key]: key for key in letter_value_dictionary.keys()}

credits = {'pick': 5, 'clean': 10, 'putInBasket': 20}
OPS = ["up", "down", "left", "right", "clean", "pick", "putInBasket", "idle"]
OBS = ["right_wall", "left_wall", "upper_wall", "downer_wall", "left_up_wall", "left_down_wall", "right_up_wall",
       "right_down_wall", "no_walls", "fruit", "stain", "basket", "end"]

optimization_algorithm = 'q_learning'