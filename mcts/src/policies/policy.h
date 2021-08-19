#ifndef POKEMON_MCTS_POLICY_H
#define POKEMON_MCTS_POLICY_H

#include "../showdown_simulator/player_data.h"

#include <string>
#include <unordered_map>


class Policy {
public:
    /// Estimates which action should be taken given some information about the game state.
    /// @param p1: Information about the player taking the action
    /// @param p2: Information about the opponent
    /// @return: Action probabilities. The keys are the actions "move 1", "move 2", "switch 2", and "switch 3".
    virtual std::unordered_map<std::string, float> evaluate_policy(PlayerData const p1, PlayerData const p2) = 0;
};


#endif //POKEMON_MCTS_POLICY_H
