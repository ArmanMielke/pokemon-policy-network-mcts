import numpy as np

class DataConverter():
    def __init__(self):
        pass

    def convert(self, data):
        num_turns = len(data['game'])
        converted_data = []
        for i in range(num_turns):
            turn = data['game'][i]
            converted_data.append( {
                "p1" : self.get_player_data(turn, "p1"),
                "p2" : self.get_player_data(turn, "p2")
            })
        return converted_data

    def get_player_data(self, data, playerid):
        sides = data["sides"]
        my_side = sides[0] if sides[0]["id"] == playerid else sides[1]
        converted_data = {
            "moves": self.get_active_moves(my_side["pokemon"]),
            "chosenMove": self.get_chosen_move(my_side)
        }
        return converted_data

    def get_active_moves(self, my_pokemon):
        for pokemon in my_pokemon:
            if pokemon["isActive"]:
                moves = []
                move_slots = pokemon["moveSlots"]
                move_lookup = {
                    "tackle" : 1,
                    "slash"  : 2,
                    "scratch": 3
                }
                for move in move_slots:
                    moves.append(
                        move_lookup[move["id"]]
                    )
                return np.array(moves)

    def get_chosen_move(self, my_side):
        move = my_side["action"][0].split(" ")[-1]
        move_pos = self.get_move_position(move, my_side)
        if move_pos == 0:
            return np.array([1, 0, 0, 0])
        elif move_pos == 1:
            return np.array([0, 1, 0, 0])
        elif move_pos == 2:
            return np.array([0, 0, 1, 0])
        else:
            return np.array([0, 0, 0, 1])

    def get_move_position(self, move, my_side):
        for pokemon in my_side["pokemon"]:
            if pokemon["isActive"]:
                move_slots = pokemon["moveSlots"]
                for i in range(len(move_slots)):
                    if move_slots[i]["id"] == move:
                        return i