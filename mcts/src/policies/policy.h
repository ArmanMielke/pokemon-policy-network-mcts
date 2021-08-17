#ifndef POKEMON_MCTS_POLICY_H
#define POKEMON_MCTS_POLICY_H

#include "../showdown_simulator/player_data.h"

#include <array>


class Policy {
public:
    virtual std::array<float, 4> evaluate_policy(PlayerData const p1, PlayerData const p2) = 0;
};


#endif //POKEMON_MCTS_POLICY_H
