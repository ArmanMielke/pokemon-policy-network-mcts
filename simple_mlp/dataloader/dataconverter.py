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

        return {
            "active_moves" : active_moves_ids, "chosen_move" : chosen_move,
            "moves_damage" : moves_damage, "hp_active" : hp_active, "hp_all" : hp_all, 
            "stats_active" : stats_active, "stats_all" : stats_all
        }


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
        move_num = []
        moves = []
        move_slots = pokemon['moveSlots']
        for move in move_slots:
            move_name = move['id']
            moves.append(move_name)
            move_num.append(self.moves[move_name]['num'])
        return np.array(moves), np.array(move_num)

    def get_chosen_move(self, side) -> np.ndarray:
        """
        Get the chosen move by pmariglia for the given side
        """
        action = side['action'][0].split(" ")
        chosen_move = np.zeros(6) # 4 for the attacks and 1 for the switch action +1 slack (if move not found)
        if action[0] == "/switch":
            chosen_move[-2] = 1
        else:
            move = action[-1]
            move_pos = self.get_move_position(move, side)
            if move_pos == None:
                chosen_move[-1] = 1
            else:
                chosen_move[move_pos] = 1
        return chosen_move

    def get_move_position(self, move, side) -> int:
        """
        Get the position of a move in the move slots
        """
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

    def get_hp_all(self, pokemon) -> np.ndarray:
        """
        Get the hp for all pokemon in a team
        """
        hps = []
        for p in pokemon:
            hps.append(self.get_hp(p))
        return np.concatenate(tuple(hps))

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
        stats = []
        for pokemon in team:
            stats.append( self.get_pokemon_stats(pokemon) )
        return np.concatenate(tuple(stats))

    def get_moves_damage(self, moves) -> np.ndarray:
        """
        Return the base damage for the given moves
        """
        damage = np.zeros(len(moves))
        for i, move in enumerate(moves):
            damage[i] = self.moves[move]['basePower']
        return damage

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
