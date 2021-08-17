#ifndef POKEMON_MCTS_SIMPLE_HEURISTIC_POLICY_H
#define POKEMON_MCTS_SIMPLE_HEURISTIC_POLICY_H

#include "policy.h"
#include "../showdown_simulator/player_data.h"

#include <array>


/// Estimates action probabilities based on a simple, hand-crafted heuristic.
class SimpleHeuristicPolicy : public Policy {
public:
    std::array<float, 4> evaluate_policy(PlayerData const p1, PlayerData const p2) override;
};


#endif //POKEMON_MCTS_SIMPLE_HEURISTIC_POLICY_H
