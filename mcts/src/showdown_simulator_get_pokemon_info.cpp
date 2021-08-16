#include "showdown_simulator.h"
#include "player_data.h"

#include <array>
#include <string>
#include <vector>

#include <boost/algorithm/string.hpp>


PlayerData ShowdownSimulator::get_player_info(Player const player) {
    std::array<PokemonData, NUM_POKEMON> player_data;
    for (int pokemon = 0; pokemon < NUM_POKEMON; pokemon++) {
        player_data[pokemon] = this->get_pokemon_info(player, pokemon);
    }
    return player_data;
}

PokemonData ShowdownSimulator::get_pokemon_info(Player const player, int const pokemon) {
    std::string const player_str = std::to_string(player);
    std::string const pokemon_str = std::to_string(pokemon);
    PokemonData pokemon_data;

    // is_active is 1 for the first pokemon, 0 otherwise
    pokemon_data.is_active = (pokemon == 0);

    // current hp
    pokemon_data.hp = std::stoi(this->eval("p" + player_str + ".pokemon[" + pokemon_str + "].hp"));

    // stats
    std::string stats_string = this->eval(
            "const s = p" + player_str + ".pokemon[" + pokemon_str + "].baseStoredStats; " +
            "[s['atk'], s['def'], s['spa'], s['spd'], s['spe'], s['hp']]"
    );
    // remove brackets [ ] at the start and end
    stats_string = stats_string.substr(1, stats_string.size() - 2);
    // split into separate strings
    std::vector<std::string> stats_split;
    boost::split(stats_split, stats_string, boost::is_any_of(","));
    // convert to number
    for (int stat_index = 0; stat_index < 6; stat_index++) {
        pokemon_data.stats[stat_index] = std::stoi(stats_split[stat_index]);
    }

    // types
    std::string types_string = this->eval("p" + player_str + ".pokemon[" + pokemon_str + "].types");
    // remove brackets [ ] at the start and end
    types_string = types_string.substr(1, types_string.size() - 2);
    // split into separate strings
    std::vector<std::string> types_split;
    boost::split(types_split, types_string, boost::is_any_of(","));
    // convert to one-hot (or two-hot) encoded array
    for (std::string type : types_split) {
        boost::trim(type);
        std::string const type_without_quotes = type.substr(1, type.size() - 2);
        size_t const type_index = int(this->types_json[type_without_quotes]) - 1;
        pokemon_data.types[type_index] = 1;
    }

    // move ids, types, damages and categories
    std::string move_names_string = this->eval("p" + player_str + ".pokemon[" + pokemon_str + "].set.moves");
    // remove brackets [ ] at the start and end
    move_names_string = move_names_string.substr(1, move_names_string.size() - 2);
    // split into separate strings
    std::vector<std::string> move_names_split;
    boost::split(move_names_split, move_names_string, boost::is_any_of(","));
    for (int i = 0; i < move_names_split.size(); i++) {
        std::string move_name = move_names_split[i];
        // remove spaces and hyphens
        move_name.erase(std::remove(move_name.begin(), move_name.end(), ' '), move_name.end());
        move_name.erase(std::remove(move_name.begin(), move_name.end(), '-'), move_name.end());
        // remove quotes at the start and end
        move_name = move_name.substr(1, move_name.size() - 2);
        boost::algorithm::to_lower(move_name);

        // move id
        pokemon_data.moves[i] = this->moves_json[move_name]["num"];
        // move type
        std::string const move_type = this->moves_json[move_name]["type"];
        int const move_type_index = int(this->types_json[move_type]) - 1;
        pokemon_data.move_types[i][move_type_index] = 1;
        // move damage
        pokemon_data.move_damages[i] = this->moves_json[move_name]["basePower"];
        // move category
        std::string const move_category = this->moves_json[move_name]["category"];
        if (move_category == "Special") {
            pokemon_data.move_categories[i] = 1;
        } else if (move_category == "Physical") {
            pokemon_data.move_categories[i] = 2;
        }
    }

    return pokemon_data;
}
