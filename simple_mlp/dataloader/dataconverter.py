import os
import numpy as np
from typing import Dict, Tuple
import json
from pathlib import Path

class DataConverter():
    def __init__(self):

        # The values of all existing moves, items, abilities, etc.
        dirname = Path(__file__).parent.absolute()
        self.moves = self.load_json(os.path.join(dirname,'data', 'moves.json'))
        self.abilities = self.load_json(os.path.join(dirname,'data', 'abilities.json'))
        self.items = self.load_json(os.path.join(dirname,'data', 'items.json'))
        self.pokemon = self.load_json(os.path.join(dirname,'data', 'pokedex.json'))
        self.types = self.load_json(os.path.join(dirname, 'data', 'types.json'))

        self.MAX_TEAM_SIZE = 6
        self.MAX_MOVE_SIZE = 4

    def convert_game(self, data):
        num_turns = len(data['game'])
        converted_data = []
        for i in range(num_turns):
            converted_data.append( self.convert_turn(data['game'][i]))
        return converted_data

    def convert_turn(self, turn):
        return {
            'p1' : self.get_player_data(turn, 'p1'),
            'p2' : self.get_player_data(turn, 'p2')
        }

    def get_player_data(self, data, playerid):
        sides = data["sides"]
        my_side = sides[0] if sides[0]["id"] == playerid else sides[1]
        other_side = sides[1] if sides[0]["id"] == playerid else sides[0]
        my_pokemon = my_side['pokemon']
        my_active_pokemon = self.get_active_pokemon(my_pokemon)

        active_moves, active_moves_ids = self.get_moves(my_active_pokemon) # the moves of the active pokemon (as showdown ids)
        moves_damage = self.get_moves_damage(active_moves)          # the base damage for each move
        chosen_move = self.get_chosen_move(my_side)                 # the move pmariglia chose
        hp_active = self.get_hp(my_active_pokemon)                  # hp only of the active pokemon
        hp_all = self.get_hp_all(my_pokemon)                        # hp of the whole team
        stats_active = self.get_pokemon_stats(my_active_pokemon)    # atk, def, spa, spd, spe, hp of the active pokemon
        stats_all = self.get_team_pokemon_stats(my_pokemon)         # stats of all pokemon in the team
        type_active = self.get_pokemon_type(my_active_pokemon)      # type of active pokemon
        type_active_vector = self.get_pokemon_type_vector(my_active_pokemon)
        type_all = self.get_pokemon_type_all(my_pokemon)            # types of all pokemon
        move_type_active = self.get_pokemon_move_types(my_active_pokemon)   # the move types of my active
        move_types_all = self.get_team_pokemon_move_types(my_pokemon) # move types of the complete team
        move_category = self.get_move_category_active(active_moves)


        return {
            "active_moves" : active_moves_ids, "chosen_move" : chosen_move,
            "moves_damage" : moves_damage, "hp_active" : hp_active, "hp_all" : hp_all, 
            "stats_active" : stats_active, "stats_all" : stats_all, "type_active" : type_active,
            "type_all" : type_all, "move_type_active" : move_type_active, "move_type_all" : move_types_all,
            "type_active_vector" : type_active_vector, "move_category" : move_category
        }

    def get_move_category_active(self, moves) -> np.ndarray:
        result = np.zeros(self.MAX_MOVE_SIZE)
        for i, move in enumerate(moves):
            cat = self.moves[move]["category"].lower()
            if cat == "special":
                result[i] = 1
            elif cat == "physical":
                result[i] = 2
        return result

    def get_active_pokemon(self, pokemon) -> Dict:
        """
        Return all values for the active pokemon
        """
        for p in pokemon:
            if p['isActive']:
                return p
        
        # TODO: if no pokemon is active anymore
        # choose the an abitrary pokemon. needs to be fixed
        return pokemon[0]

    def get_moves(self, pokemon) -> Tuple[np.ndarray, np.ndarray]:
        """
        Return the move ids (based on the id by showdown) and move names in a numpy array
        for the given pokemon
        """
        move_num = np.zeros(self.MAX_MOVE_SIZE)
        moves = []
        move_slots = pokemon['moveSlots']
        for i, move in enumerate(move_slots):
            move_name = move['id']

            # the real id for hidden power 
            # depends on the hidden type
            if move_name == "hiddenpower":
                pokemon_set_moves = pokemon["set"]["moves"]
                for i, m in enumerate(pokemon_set_moves):
                    m_tmp = m.replace(" ", "").lower()
                    if "hiddenpower" in m_tmp:
                        move_name = m_tmp
                        break

            moves.append(move_name)
            move_num[i] = self.moves[move_name]['num']
        return np.array(moves), move_num

    def get_chosen_move(self, side) -> np.ndarray:
        """
        Get the chosen move by pmariglia for the given side
        """
        action = side['action'][0].split(" ")
        chosen_move = np.zeros(self.MAX_MOVE_SIZE + 1) # 4 for the attacks and 1 for the switch action
        if action[0] == "/switch":
            chosen_move[-1] = 1
        else:
            move = action[-1]
            move_pos = self.get_move_position(move, side)
            if move_pos == None:
                print(f"found unknown move {move}")
                raise ValueError(f"Unknown move ({move}) in data.")
            else:
                chosen_move[move_pos] = 1
        return chosen_move

    def get_move_position(self, move, side) -> int:
        """
        Get the position of a move in the move slots
        """
        # in the move slots only "hiddepower"
        # is used as a id, not "hiddenpowerfire", "hiddenpowerwater", etc.
        if "hiddenpower" in move:
            move = "hiddenpower"
        for pokemon in side["pokemon"]:
            if pokemon["isActive"]:
                move_slots = pokemon["moveSlots"]
                for i in range(len(move_slots)):
                    if move_slots[i]["id"] == move:
                        return i

    def get_hp(self, pokemon) -> np.ndarray:
        """
        Get the HP for one pokemon
        """
        return np.array([pokemon['hp']])

    def get_hp_all(self, team) -> np.ndarray:
        """
        Get the hp for all pokemon in a team
        """
        hps = np.zeros(self.MAX_TEAM_SIZE)
        for i, pokemon in enumerate(team):
            hps[i] = self.get_hp(pokemon)
        return hps

    def get_pokemon_stats(self, pokemon) -> np.ndarray:
        """
        Return attack, defense, etc. for one pokemon
        """
        stats = pokemon['baseStoredStats']
        return np.array([
            stats['atk'], stats['def'], stats['spa'],
            stats['spd'], stats['spe'], stats['hp']
        ])

    def get_team_pokemon_stats(self, team) -> np.ndarray:
        """
        Return attack, defense, etc. for all pokemon in a team
        """
        statsize = 6
        stats = np.zeros(statsize * self.MAX_TEAM_SIZE)
        for i, pokemon in enumerate(team):
            # stats.append( self.get_pokemon_stats(pokemon) )
            s = self.get_pokemon_stats(pokemon)
            stats[i*self.MAX_TEAM_SIZE] = s[0]
            stats[i*self.MAX_TEAM_SIZE + 1] = s[1]
            stats[i*self.MAX_TEAM_SIZE + 2] = s[2]
            stats[i*self.MAX_TEAM_SIZE + 3] = s[3]
            stats[i*self.MAX_TEAM_SIZE + 4] = s[4]
            stats[i*self.MAX_TEAM_SIZE + 5] = s[5]
        return stats

    def get_moves_damage(self, moves) -> np.ndarray:
        """
        Return the base damage for the given moves
        """
        damage = np.zeros(self.MAX_MOVE_SIZE)
        for i, move in enumerate(moves):
            damage[i] = self.moves[move]['basePower']
        return damage

    def get_pokemon_type(self, pokemon) -> np.ndarray:
        """
        Returns the type of the given pokemon
        """
        types = pokemon['types']
        if len(types) > 1:
            return np.array([self.handle_multi_type(types)])
        else:
            return np.array([self.types[types[0]]])

    def get_pokemon_type_vector(self, pokemon) -> np.ndarray:
        types = pokemon['types']
        result = np.zeros(len(self.types))
        for t in types:
            index = self.types[t] - 1
            result[index] = 1
        return result

    def handle_multi_type(self, types) -> int:
        """
        Concatenate both types to get a new type.
        Rule: append the smaller number to the bigger one
        """
        type_1, type_2 = self.types[types[0]], self.types[types[1]]
        first, second = max(type_1, type_2), min(type_1, type_2)
        return int(f"{first}{second}")

    def get_pokemon_type_all(self, team) -> np.ndarray:
        types = np.zeros(self.MAX_TEAM_SIZE)
        for i, pokemon in enumerate(team):
            t = self.get_pokemon_type(pokemon)
            types[i] = t
        return types

    def get_hidden_power_string(self, pokemon) -> str:
        pokemon_set_moves = pokemon["set"]["moves"]
        for i, m in enumerate(pokemon_set_moves):
            m_tmp = m.replace(" ", "").lower()
            if "hiddenpower" in m_tmp:
                return m_tmp

    def get_pokemon_move_types(self, pokemon) -> np.ndarray:
        """
        Returns the move types of given pokemon
        """
        move_slots = pokemon["moveSlots"]
        types = np.zeros(self.MAX_MOVE_SIZE)
        for i, move in enumerate(move_slots):
            move_id = move['id']
            if "hiddenpower" in move_id:
                move_id = self.get_hidden_power_string(pokemon)
            t = self.moves[move_id]
            types[i] = self.types[t['type']]
        return types

    def get_team_pokemon_move_types(self, team) -> np.ndarray:
        types = np.zeros(self.MAX_MOVE_SIZE * self.MAX_TEAM_SIZE)
        for i, pokemon in enumerate(team):
            t = self.get_pokemon_move_types(pokemon)
            types[i*self.MAX_MOVE_SIZE] = t[0] 
            types[i*self.MAX_MOVE_SIZE + 1] = t[1] 
            types[i*self.MAX_MOVE_SIZE + 2] = t[2] 
            types[i*self.MAX_MOVE_SIZE + 3] = t[3]
        return types

    def one_hot_encode(self, category, num_categories) -> np.ndarray:
        """
        Create a one hot representation of a category
        """
        vector = np.zeros(num_categories)
        vector[category] = 1
        return vector

    def load_json(self, path):
        with open(path, 'r') as f:
            return json.load(f)
