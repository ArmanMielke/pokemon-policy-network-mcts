#ifndef POKEMON_MCTS_PLAYER_DATA_H
#define POKEMON_MCTS_PLAYER_DATA_H


#include <array>


int const NUM_POKEMON = 3;
int const NUM_STATS = 6;
int const NUM_TYPES = 18;
int const NUM_MOVES = 4;


/// Information describing one Pokémon.
struct PokemonData {
public:
    /// 1 if the Pokémon is active, 0 otherwise.
    float is_active;
    /// The current HP of the Pokémon.
    float hp;
    /// The Pokémon's stats in the order attack, defense, special attack, special defense, speed, maximum HP.
    std::array<float, NUM_STATS> stats = { 0 };
    /// An array representing the Pokémon's types.
    /// The types that the Pokémon has are 1, all other types are 0.
    std::array<float, NUM_TYPES> types = { 0 };
    /// The IDs of each of the Pokémon's moves.
    std::array<float, NUM_MOVES> moves = { 0 };
    /// For each move, the one-hot encoded type.
    std::array<std::array<float, NUM_TYPES>, NUM_MOVES> move_types = { 0 };
    /// The base power of each move.
    std::array<float, NUM_MOVES> move_damages = { 0 };
    /// The category of each move.
    /// 0 for status, 1 for special, 2 for physical.
    std::array<float, NUM_MOVES> move_categories = { 0 };
};


/// Information describing the Pokémon of one player.
typedef std::array<PokemonData, NUM_POKEMON> PlayerData;


#endif //POKEMON_MCTS_PLAYER_DATA_H
