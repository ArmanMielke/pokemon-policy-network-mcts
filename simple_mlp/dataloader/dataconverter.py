import numpy as np

class DataConverter():
    def __init__(self):
        self.last_move = np.array([0,0,0,1,0])
        self.current_move = np.array([0,0,0,1,0])

        self.move_lookup = {
            "tackle" : 1,
            "slash"  : 2,
            "scratch": 3
        }

        self.damage_lookup = {
            2 : 70,
            3 : 40
        }

    def convert(self, data):
        num_turns = len(data['game'])
        converted_data = []
        # remove the first 2 turns because there are 
        # wrong moves
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
        other_side = sides[1] if sides[0]["id"] == playerid else sides[0]
        converted_data = {
            "moves": self.get_active_moves(my_side["pokemon"]),
            #"moves_damage": self.get_active_moves_damage(my_side["pokemon"]),
            "chosenMove": self.get_chosen_move(my_side),
            "hp": self.get_hp(my_side["pokemon"]),
            "enemy_hp": self.get_hp(other_side["pokemon"]),
            "last_move": self.get_last_move()
        }
        return converted_data

    def get_active_moves(self, my_pokemon):
        for pokemon in my_pokemon:
            if pokemon["isActive"]:
                moves = []
                move_slots = pokemon["moveSlots"]
                for move in move_slots:
                    moves.append(
                        self.move_lookup[move["id"]]
                    )
                return np.array(moves)

    def get_active_moves_damage(self, my_pokemon):
        active_moves = self.get_active_moves(my_pokemon)
        
        damage = []
        for move in active_moves:
            damage.append(self.damage_lookup[move])
        return np.array(damage)

    def get_chosen_move(self, my_side):
        action = my_side["action"][0].split(" ")
        self.last_move = self.current_move
        if action[0] == "/switch":
            self.current_move = np.array([0, 0, 0, 0, 1])
        else:
            move = action[-1]
            move_pos = self.get_move_position(move, my_side)
        
            if move_pos == 0:
                self.current_move = np.array([1, 0, 0, 0, 0])
            elif move_pos == 1:
                self.current_move = np.array([0, 1, 0, 0, 0])
            elif move_pos == 2:
                self.current_move = np.array([0, 0, 1, 0, 0])
            else:
                self.current_move = np.array([0, 0, 0, 1, 0])
        return self.current_move

    def get_move_position(self, move, my_side):
        for pokemon in my_side["pokemon"]:
            if pokemon["isActive"]:
                move_slots = pokemon["moveSlots"]
                for i in range(len(move_slots)):
                    if move_slots[i]["id"] == move:
                        return i

    def get_hp(self, enemy_side):
        hps = []
        for pokemon in enemy_side:
            hps.append( pokemon["hp"] )
        return np.array(hps)

    def get_last_move(self):
        return self.last_move

    def get_move_name(self, move):
        moveid = np.argmax(move)
        for name, id in self.move_lookup.items():
            if id == moveid:
                return name