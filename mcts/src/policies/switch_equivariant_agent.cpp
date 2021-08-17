#include "switch_equivariant_agent.h"

#include <iostream>

using torch::Tensor;
using torch::indexing::Slice;


SwitchEquivariantAgentImpl::SwitchEquivariantAgentImpl(
    int const p1_pokemon_size,
    int const p2_pokemon_size,
    int const num_pokemon
) : move_network(register_module("move_network", torch::nn::Sequential(
        torch::nn::Linear(p1_pokemon_size + num_pokemon * p2_pokemon_size, 128),
        torch::nn::ReLU(true),
        torch::nn::Linear(128, 128),
        torch::nn::ReLU(true),
        torch::nn::Linear(128, 128),
        torch::nn::ReLU(true),
        torch::nn::Linear(128, NUM_ACTIONS)
    ))),
    switch_network(register_module("switch_network", torch::nn::Sequential(
        torch::nn::Linear(p1_pokemon_size + num_pokemon * p2_pokemon_size, 128),
        torch::nn::ReLU(true),
        torch::nn::Linear(128, 128),
        torch::nn::ReLU(true),
        torch::nn::Linear(128, 128),
        torch::nn::ReLU(true),
        torch::nn::Linear(128, 1)
    ))) {}

Tensor SwitchEquivariantAgentImpl::forward(Tensor const p1, Tensor const p2) {
    Tensor const p2_flat = p2.flatten(1);

    // attacking moves
    Tensor const p1_active_pokemon = p1.index({Slice(), 0, Slice()});  // p1[:, 0, :]
    Tensor const active_pokemon_and_opponent = torch::cat({p1_active_pokemon, p2_flat}, 1);
    Tensor move_logits = this->move_network->forward(active_pokemon_and_opponent);
    // pad the logits with zeros for the missing actions
    move_logits = torch::cat({move_logits, torch::zeros(move_logits.sizes())}, 1);

    // switch actions for the second pokemon
    Tensor const p1_second_pokemon = p1.index({Slice(), 1, Slice()});  // p1[:, 1, :]
    Tensor const second_pokemon_and_opponent = torch::cat({p1_second_pokemon, p2_flat}, 1);
    Tensor const switch_2_logit = this->switch_network->forward(second_pokemon_and_opponent);

    // switch actions for the third pokemon
    Tensor const p1_third_pokemon = p1.index({Slice(), 2, Slice()});  // p1[:, 2, :]
    Tensor const third_pokemon_and_opponent = torch::cat({p1_third_pokemon, p2_flat}, 1);
    Tensor const switch_3_logit = this->switch_network->forward(third_pokemon_and_opponent);

    // combined logits
    return torch::cat({move_logits, switch_2_logit, switch_3_logit}, 1);
}
