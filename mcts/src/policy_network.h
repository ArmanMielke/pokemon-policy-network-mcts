#ifndef POKEMON_MCTS_POLICY_NETWORK_H
#define POKEMON_MCTS_POLICY_NETWORK_H

#include <torch/torch.h>


const int NUM_ACTIONS = 2;


// corresponds to SwitchEquivariantAgent in the python code
class PolicyNetwork : protected torch::nn::Module {
public:
    /// @param p1_pokemon_size: Number of inputs per Pokémon of player 1
    /// @param p2_pokemon_size: Number of inputs per Pokémon of player 2
    /// @param num_pokemon: Maximum number of Pokémon per team
    PolicyNetwork(int const p1_pokemon_size, int const p2_pokemon_size, int const num_pokemon);
    /// @param p1: Team of player 1. Shape (batch_size, num_pokemon, p1_pokemon_size)
    /// @param p2: Team of player 2. Shape (batch_size, num_pokemon, p2_pokemon_size)
    torch::Tensor forward(torch::Tensor const p1, torch::Tensor const p2);

private:
    torch::nn::Sequential move_network;
    torch::nn::Sequential switch_network;
};


#endif //POKEMON_MCTS_POLICY_NETWORK_H
