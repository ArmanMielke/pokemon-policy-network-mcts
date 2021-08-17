#ifndef POKEMON_MCTS_LOAD_MODEL_H
#define POKEMON_MCTS_LOAD_MODEL_H

#include "policy.h"
#include "../showdown_simulator/player_data.h"

#include <array>
#include <string>

#include <torch/torch.h>


class PolicyNetwork : Policy {
public:
    /// Loads the model from the given path.
    explicit PolicyNetwork(std::string const model_path);
    /// Estimates which action should be taken given some information about the game state.
    /// @param p1: Information about the player taking the action
    /// @param p2: Information about the opponent
    /// @return: Action probabilities
    std::array<float, 4> evaluate_policy(PlayerData const p1, PlayerData const p2) override;

private:
    torch::jit::script::Module model;

    /// @param p1: Team of player 1. Shape (batch_size, num_pokemon, p1_pokemon_size)
    /// @param p2: Team of player 2. Shape (batch_size, num_pokemon, p2_pokemon_size)
    torch::Tensor model_forward(torch::Tensor const p1, torch::Tensor const p2);
};


#endif //POKEMON_MCTS_LOAD_MODEL_H
