#ifndef POKEMON_MCTS_LOAD_MODEL_H
#define POKEMON_MCTS_LOAD_MODEL_H


#include <string>

#include <torch/torch.h>


class PolicyNetwork {
public:
    /// Loads the model from the given path.
    PolicyNetwork(std::string const model_path);
    /// @param p1: Team of player 1. Shape (batch_size, num_pokemon, p1_pokemon_size)
    /// @param p2: Team of player 2. Shape (batch_size, num_pokemon, p2_pokemon_size)
    torch::Tensor forward(torch::Tensor const p1, torch::Tensor const p2);

private:
    torch::jit::script::Module model;
};



#endif //POKEMON_MCTS_LOAD_MODEL_H
