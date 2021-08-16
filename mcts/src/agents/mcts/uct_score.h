#ifndef POKEMON_MCTS_MCTS_AGENT_UCT_SCORE_H
#define POKEMON_MCTS_MCTS_AGENT_UCT_SCORE_H

#include "node.h"

#include <memory>


float uct_score(std::shared_ptr<Node> const parent, std::shared_ptr<Node> const child);

float uct_score_with_policy(
    std::shared_ptr<Node> const parent,
    std::shared_ptr<Node> const child,
    float const policy_action_probability
);


#endif //POKEMON_MCTS_MCTS_AGENT_UCT_SCORE_H
