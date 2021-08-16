#ifndef POKEMON_MCTS_SIMPLE_HEURISTIC_POLICY_H
#define POKEMON_MCTS_SIMPLE_HEURISTIC_POLICY_H

#include "../showdown_simulator/player_data.h"


/// Estimates action probabilities based on a simple, hand-crafted heuristic.
class SimpleHeuristicPolicy {
public:
    /// Estimates which action should be taken given some information about the game state.
    /// @param p1: Information about the player taking the action
    /// @param p2: Information about the opponent
    /// @return: Action probabilities
    std::array<float, 4> evaluate_policy(PlayerData const p1, PlayerData const p2);
};


#endif //POKEMON_MCTS_SIMPLE_HEURISTIC_POLICY_H
