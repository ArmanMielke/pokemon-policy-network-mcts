#include "simple_heuristic_policy.h"
#include "../showdown_simulator/player_data.h"

#include <array>
#include <string>
#include <unordered_map>

#include <torch/torch.h>

using torch::Tensor;
using torch::indexing::Slice;


float const SWITCH_LOGIT = 60;
Tensor const SWITCH_LOGITS = SWITCH_LOGIT * torch::ones(NUM_POKEMON - 1);
// all logits are multiplied with this number before being passed to the softmax in order to avoid the probability
// of the best action being almost one and the probability of all other actions being almost 0
float const LOGIT_FACTOR = 0.2;

// the order of the types is the same order that Pokémon Showdown uses (in types.json)
std::array<float, NUM_TYPES * NUM_TYPES> const TYPE_EFFECTIVENESS_CHART = {
    /*             Norm Fire Wate Gras Elec Ice  Figh Pois Grou Fly  Psyc Bug  Rock Ghos Dark Drag Stee Fairy */
    /*   Normal */ 1  , 1  , 1  , 1  , 1  , 1  , 1  , 1  , 1  , 1  , 1  , 1  , 0.5, 0  , 1  , 1  , 0.5, 1  ,
    /*     Fire */ 1  , 0.5, 0.5, 2  , 1  , 2  , 1  , 1  , 1  , 1  , 1  , 2  , 0.5, 1  , 1  , 0.5, 2  , 1  ,
    /*    Water */ 1  , 2  , 0.5, 0.5, 1  , 1  , 1  , 1  , 2  , 1  , 1  , 1  , 2  , 1  , 1  , 0.5, 1  , 1  ,
    /*    Grass */ 1  , 0.5, 2  , 0.5, 1  , 1  , 1  , 0.5, 2  , 0.5, 1  , 0.5, 2  , 1  , 1  , 0.5, 0.5, 1  ,
    /* Electric */ 1  , 1  , 2  , 0.5, 0.5, 1  , 1  , 1  , 0  , 2  , 1  , 1  , 1  , 1  , 1  , 0.5, 1  , 1  ,
    /*      Ice */ 1  , 0.5, 0.5, 2  , 1  , 0.5, 1  , 1  , 2  , 2  , 1  , 1  , 1  , 1  , 1  , 2  , 0.5, 1  ,
    /* Fighting */ 2  , 1  , 1  , 1  , 1  , 2  , 1  , 0.5, 1  , 0.5, 0.5, 0.5, 2  , 0  , 2  , 1  , 2  , 0.5,
    /*   Poison */ 1  , 1  , 1  , 2  , 1  , 1  , 1  , 0.5, 0.5, 1  , 1  , 1  , 0.5, 0.5, 1  , 1  , 0  , 2  ,
    /*   Ground */ 1  , 2  , 1  , 0.5, 2  , 1  , 1  , 2  , 1  , 0  , 1  , 0.5, 2  , 1  , 1  , 1  , 2  , 1  ,
    /*   Flying */ 1  , 1  , 1  , 2  , 0.5, 1  , 2  , 1  , 1  , 1  , 1  , 2  , 0.5, 1  , 1  , 1  , 0.5, 1  ,
    /*  Psychic */ 1  , 1  , 1  , 1  , 1  , 1  , 2  , 2  , 1  , 1  , 0.5, 1  , 1  , 1  , 0  , 1  , 0.5, 1  ,
    /*      Bug */ 1  , 0.5, 1  , 2  , 1  , 1  , 0.5, 0.5, 1  , 0.5, 2  , 1  , 1  , 0.5, 2  , 1  , 0.5, 0.5,
    /*     Rock */ 1  , 2  , 1  , 1  , 1  , 2  , 0.5, 1  , 0.5, 2  , 1  , 2  , 1  , 1  , 1  , 1  , 0.5, 1  ,
    /*    Ghost */ 0  , 1  , 1  , 1  , 1  , 1  , 1  , 1  , 1  , 1  , 2  , 1  , 1  , 2  , 0.5, 1  , 1  , 1  ,
    /*     Dark */ 1  , 1  , 1  , 1  , 1  , 1  , 0.5, 1  , 1  , 1  , 2  , 1  , 1  , 2  , 0.5, 1  , 1  , 0.5,
    /*   Dragon */ 1  , 1  , 1  , 1  , 1  , 1  , 1  , 1  , 1  , 1  , 1  , 1  , 1  , 1  , 1  , 2  , 0.5, 0  ,
    /*    Steel */ 1  , 0.5, 0.5, 1  , 0.5, 2  , 1  , 1  , 1  , 1  , 1  , 1  , 2  , 1  , 1  , 1  , 0.5, 2  ,
    /*    Fairy */ 1  , 0.5, 1  , 1  , 1  , 1  , 2  , 0.5, 1  , 1  , 1  , 1  , 1  , 1  , 2  , 2  , 0.5, 1  ,
};
Tensor const TYPE_EFFECTIVENESS_MATRIX = torch::from_blob((int*)TYPE_EFFECTIVENESS_CHART.data(), {NUM_TYPES, NUM_TYPES});


std::unordered_map<std::string, float> SimpleHeuristicPolicy::evaluate_policy(PlayerData const p1, PlayerData const p2) {
    // the logits for attacks are the move's base damage times the STAB bonus times the type effectiveness modifier
    // (assuming the opponent doesn't switch)
    Tensor const base_damages = torch::from_blob((int*)p1[0].move_damages.data(), NUM_MOVES);

    Tensor stab_bonus = torch::ones(NUM_MOVES);
    Tensor type_effectiveness_modifier = torch::ones(NUM_MOVES);
    Tensor const attacking_pokemon_type = torch::from_blob((int*)p1[0].types.data(), NUM_TYPES);
    Tensor const defending_pokemon_type = torch::from_blob((int*)p2[0].types.data(), NUM_TYPES);
    for (size_t move = 0; move < NUM_MOVES; move++) {
        // stab bonus
        Tensor const move_type = torch::from_blob((int*)p1[0].move_types[move].data(), NUM_TYPES);
        //                         TODO use matmul?
        int const has_stab_bonus = torch::sum(attacking_pokemon_type * move_type).item<int>();
        if (has_stab_bonus == 1) {
            stab_bonus[move] = 1.5;
        }

        // type effectiveness
        Tensor move_effectiveness = matmul(move_type, TYPE_EFFECTIVENESS_MATRIX);
        type_effectiveness_modifier[move] = matmul(move_effectiveness, defending_pokemon_type);
    }

    Tensor move_logits = base_damages * stab_bonus * type_effectiveness_modifier;
    // we're currently only using two moves => throw away the logits of the other two moves
    move_logits = move_logits.index({Slice(0, 2)});
    Tensor const logits = torch::cat({move_logits, SWITCH_LOGITS}, 0);
    Tensor const action_probabilities = torch::softmax(logits * LOGIT_FACTOR, 0);

    return {
        {"move 1", action_probabilities[0].item<float>()},
        {"move 2", action_probabilities[1].item<float>()},
        {"switch 2", action_probabilities[2].item<float>()},
        {"switch 3", action_probabilities[3].item<float>()}
    };
}
