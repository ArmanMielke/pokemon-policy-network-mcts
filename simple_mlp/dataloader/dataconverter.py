import numpy as np

class DataConverter():
    def __init__(self):

        self.move_lookup = {
            "tackle" : 0,
            "slash"  : 1,
            "scratch": 2,
            "pound"  : 3,
            "extremespeed": 4,
            "stomp" : 5,
            "chipaway" : 6,
            "headbutt" : 7
        }

        self.move_size = 4 + 2 # +1 for switch, +1 for slack (if attack not found)
        self.last_move = self.current_move = np.zeros(self.move_size)

        self.damage_lookup = {
            0 : 40,     # tackle
            1 : 70,     # slash
            2 : 40,     # scratch
            3 : 40,     # pound
            4 : 80,     # extremespeed
            5 : 65,     # stomp
            6 : 70,     # chipaway
            7 : 70      # headbutt
        }

        self._feature_sizes = {}

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
            "moves_damage": self.get_active_moves_damage(my_side["pokemon"]),
            "chosenMove": self.get_chosen_move(my_side),
            "hp": self.get_hp(my_side["pokemon"]),
            "enemy_hp": self.get_hp(other_side["pokemon"]),
            "last_move": self.get_last_move()
        }
        for key, value in converted_data.items():
            self._feature_sizes.update({key : len(value)})
        return converted_data

    def get_active_moves(self, my_pokemon):
        moves = []
        for pokemon in my_pokemon:
            if pokemon["isActive"]:
                move_slots = pokemon["moveSlots"]
                for move in move_slots:
                    moves.append(
                        self.move_lookup[move["id"]]
                    )
                return np.array(moves)
        
        # TODO: if both pokemon are dead we need to find
        # a better solution to handle this
        move_slots = my_pokemon[0]["moveSlots"]
        for move in move_slots:
            moves.append(
                self.move_lookup[move["id"]]
            )
        return np.array(moves)

    def get_active_moves_damage(self, my_pokemon):
        active_moves = self.get_active_moves(my_pokemon)
        
        damage = []
        #print(active_moves)
        for move in active_moves:
            damage.append(self.damage_lookup[move])
        return np.array(damage)

    def get_chosen_move(self, my_side):
        action = my_side["action"][0].split(" ")
        self.last_move = self.current_move
        if action[0] == "/switch":
            self.current_move = np.zeros(self.move_size)
            self.current_move[-2] = 1
        else:
            move = action[-1]
            move_pos = self.get_move_position(move, my_side)

            self.current_move = np.zeros(self.move_size)
            if move_pos == None:
                self.current_move[-1] = 1
            else:
                self.current_move[move_pos] = 1
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

    def feature_size(self, feature):
        return self._feature_sizes[feature]