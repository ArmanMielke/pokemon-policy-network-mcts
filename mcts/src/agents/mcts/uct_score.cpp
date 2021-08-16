#include "uct_score.h"
#include "node.h"

#include <math.h>
#include <memory>


float const EXPLORATION_FACTOR = 5;

// the opponent of the child's turn player is the parent's turn player, so child->opponent_win_rate() gives the
// win rate of the parent's turn player when choosing the action that leads to that child
// TODO sanity check everything

float uct_score(std::shared_ptr<Node> const parent, std::shared_ptr<Node> const child) {
    float const exploitation = child->opponent_win_rate();
    float const exploration = std::sqrt(std::log(parent->visit_count + 1) / (child->visit_count + 1));
    return exploitation + EXPLORATION_FACTOR * exploration;
}

float uct_score_with_policy(
    std::shared_ptr<Node> const parent,
    std::shared_ptr<Node> const child,
    float const policy_action_probability
) {
    float const exploitation = child->opponent_win_rate();
    float const exploration = std::sqrt(parent->visit_count) / (child->visit_count + 1);
    return exploitation + EXPLORATION_FACTOR * policy_action_probability * exploration;
}
