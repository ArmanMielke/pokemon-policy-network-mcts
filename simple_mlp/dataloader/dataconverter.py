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
        p1_data = self.get_player_data(turn, 'p1')
        p2_data = self.get_player_data(turn, 'p2')

        if p1_data == None or p2_data == None:
            return None
        p1_active = {'p1' : p1_data, 'p2': p2_data}
        p2_active = {'p1' : p2_data, 'p2' : p1_data}
        return p1_active, p2_active 

    def get_player_data(self, data, playerid):
        sides = data["sides"]
        my_side = sides[0] if sides[0]["id"] == playerid else sides[1]
        other_side = sides[1] if sides[0]["id"] == playerid else sides[0]
        my_pokemon = my_side['pokemon']

        pokemon_entries = [self.get_pokemon_entries(pokemon,i) for i,pokemon in enumerate(my_pokemon)] 

        # The active pokemon is always the first in the list
        # this is automatically done by showdown
        chosen_move = self.get_chosen_move(my_side)                 # the move pmariglia chose
        chosen_move_2 = self.get_chosen_move_2(my_side)

        pokemon_structured_array = np.array(pokemon_entries,
            dtype=[('is_active', np.float64, (1,)), ('hp', np.float64, (1,)), ('stats', np.float64, (6,)),
            ('type', np.float64, (len(self.types),)), ('move', np.float64, (self.MAX_MOVE_SIZE,)),
            ('move_type', np.float64, (self.MAX_MOVE_SIZE*len(self.types),)), ('move_damage', np.float64, (self.MAX_MOVE_SIZE,)),
            ('move_category', np.float64, (self.MAX_MOVE_SIZE,))])

        return {
                "chosen_move": chosen_move, "chosen_move_2": chosen_move_2,
                "pokemon" : pokemon_structured_array
        }

    def get_pokemon_entries(self, pokemon, position) -> np.ndarray:
        # is active, moves, move elements, move category
        # element, stats, hp
        is_active = np.array([1]) if position == 0 else np.array([0])               
        hp = self.get_hp(pokemon)                       
        stats = self.get_pokemon_stats(pokemon)         
        type = self.get_pokemon_type_vector(pokemon)

        moves, moves_ids = self.get_moves(pokemon) 
        move_type = self.get_pokemon_move_type_vector(pokemon)
        move_damage = self.get_moves_damage(moves)
        move_category = self.get_move_category(moves)

        return (is_active, hp, stats, type, moves_ids, move_type, move_damage, move_category)
        
    def get_move_category(self, moves) -> np.ndarray:
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
        if side['action'] == "None":
            raise ValueError(f"no action chosen")
        action = side['action'][0].split(" ")
        chosen_move = np.zeros(self.MAX_MOVE_SIZE + 1) # 4 for the attacks and 1 for the switch action
        if action[0] == "/switch":
            chosen_move[-1] = 1
        else:
            move = action[-1]
            move_pos = self.get_move_position(move, side)
            if move_pos == None:
                print(f"found unknown move {move}")
                raise ValueError(f"Unknown move ({move}) in data")
            else:
                chosen_move[move_pos] = 1
        return chosen_move

    def get_chosen_move_2(self, side) -> np.ndarray:
        """
        Get the chosen move by pmariglia for the given side.
        The switch action is split for every pokemon on the bench
        """
        if side['action'] == "None":
            raise ValueError("no action chosen")
        action = side['action'][0].split(" ")
        chosen_move = np.zeros(self.MAX_MOVE_SIZE + self.MAX_TEAM_SIZE - 1)
        if action[0] == "/switch":
            # pmariglia uses 1 for active 2 for first on bench etc. 
            idx = int(action[1]) - 2
            chosen_move[self.MAX_MOVE_SIZE + idx] = 1
        else:
            move = action[-1]
            move_pos = self.get_move_position(move, side)
            if move_pos == None:
                print(f"found unknown move {move}")
                raise ValueError(f"Unknown move ({move}) in data")
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
        # for pokemon in side["pokemon"]:
        #     if pokemon["isActive"]:
        #         move_slots = pokemon["moveSlots"]
        #         for i in range(len(move_slots)):
        #             if move_slots[i]["id"] == move:
        #                 return i
        #         raise ValueError(f"The active pokemon {pokemon['species']} does not have the move {move}")
        active_pokemon = side['pokemon'][0]
        move_slots = active_pokemon['moveSlots']
        position = -1
        for i, m in enumerate(move_slots):
            if m['id'] == move:
                position = i

        if position == -1:
            raise ValueError(f"The active pokemon {active_pokemon['species']} does not have the move {move}")
        
        return position


    def get_hp(self, pokemon) -> np.ndarray:
        """
        Get the HP for one pokemon
        """
        return np.array([pokemon['hp']])

    def get_pokemon_stats(self, pokemon) -> np.ndarray:
        """
        Return attack, defense, etc. for one pokemon
        """
        stats = pokemon['baseStoredStats']
        return np.array([
            stats['atk'], stats['def'], stats['spa'],
            stats['spd'], stats['spe'], stats['hp']
        ])

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

    def get_pokemon_move_type_vector(self, pokemon) -> np.ndarray:
        """
        Get the move types of given pokemon as
        an indicator vector
        """
        move_slots = pokemon["moveSlots"]
        types = np.zeros(len(self.types) * self.MAX_MOVE_SIZE)
        for i, move in enumerate(move_slots):
            move_id = move['id']
            if "hiddenpower" in move_id:
                move_id = self.get_hidden_power_string(pokemon)
            t = self.moves[move_id]
            index = self.types[t['type']] - 1
            types[i*self.MAX_MOVE_SIZE + index] = 1
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
