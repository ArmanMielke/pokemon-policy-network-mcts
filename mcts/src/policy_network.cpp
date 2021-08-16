#include "policy_network.h"
#include "player_data.h"

#include <string>

#include <torch/torch.h>
#include <torch/script.h>

using torch::Tensor;


// see https://pytorch.org/tutorials/advanced/cpp_export.html#step-3-loading-your-script-module-in-c
PolicyNetwork::PolicyNetwork(std::string const model_path)
    : model(torch::jit::load(model_path)) {}

Tensor convert_p1_pokemon_to_tensor(PokemonData const pokemon) {
    return torch::cat({
        torch::from_blob((int*)&pokemon.is_active, 1),
        torch::from_blob((int*)&pokemon.hp, 1),
        torch::from_blob((int*)pokemon.stats.data(), NUM_STATS),
        torch::from_blob((int*)pokemon.types.data(), NUM_TYPES),
        torch::from_blob((int*)pokemon.moves.data(), NUM_MOVES),
        torch::from_blob((int*)pokemon.move_types[0].data(), NUM_TYPES),
        torch::from_blob((int*)pokemon.move_types[1].data(), NUM_TYPES),
        torch::from_blob((int*)pokemon.move_types[2].data(), NUM_TYPES),
        torch::from_blob((int*)pokemon.move_types[3].data(), NUM_TYPES),
        torch::from_blob((int*)pokemon.move_damages.data(), NUM_MOVES),
        torch::from_blob((int*)pokemon.move_categories.data(), NUM_MOVES)
    });
}

Tensor convert_p2_pokemon_to_tensor(PokemonData const pokemon) {
    return torch::cat({
        torch::from_blob((int*)&pokemon.is_active, 1),
        torch::from_blob((int*)&pokemon.hp, 1),
        torch::from_blob((int*)pokemon.stats.data(), NUM_STATS),
        torch::from_blob((int*)pokemon.types.data(), NUM_TYPES),
        torch::from_blob((int*)pokemon.move_types[0].data(), NUM_TYPES),
        torch::from_blob((int*)pokemon.move_types[1].data(), NUM_TYPES),
        torch::from_blob((int*)pokemon.move_types[2].data(), NUM_TYPES),
        torch::from_blob((int*)pokemon.move_types[3].data(), NUM_TYPES)
    });
}

std::array<float, 4> PolicyNetwork::evaluate_policy(PlayerData const p1, PlayerData const p2) {
    // TODO make the number of Pokémon flexible
    Tensor p1_tensor = torch::stack({
        convert_p1_pokemon_to_tensor(p1[0]),
        convert_p1_pokemon_to_tensor(p1[1]),
        convert_p1_pokemon_to_tensor(p1[2]),
    }, 0);
    p1_tensor = torch::unsqueeze(p1_tensor, 0);
    Tensor p2_tensor = torch::stack({
        convert_p2_pokemon_to_tensor(p2[0]),
        convert_p2_pokemon_to_tensor(p2[1]),
        convert_p2_pokemon_to_tensor(p2[2]),
    }, 0);
    p2_tensor = torch::unsqueeze(p2_tensor, 0);

    Tensor action_probabilities = this->model_forward(p1_tensor, p2_tensor);
    action_probabilities = torch::squeeze(action_probabilities, 0);
    return {
        action_probabilities[0].item<float>(),
        action_probabilities[1].item<float>(),
        action_probabilities[4].item<float>(),
        action_probabilities[5].item<float>()
    };
}

// see https://pytorch.org/tutorials/advanced/cpp_export.html#step-4-executing-the-script-module-in-c
Tensor PolicyNetwork::model_forward(Tensor const p1, Tensor const p2) {
    // create a vector of inputs
    std::vector<torch::jit::IValue> inputs = {p1, p2};
    // execute the model and turn its output into a tensor
    return model.forward(inputs).toTensor();
}
