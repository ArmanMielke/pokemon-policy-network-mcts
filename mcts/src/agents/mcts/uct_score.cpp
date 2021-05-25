#include "uct_score.h"
#include "node.h"

#include <math.h>
#include <memory>


float const EXPLORATION_FACTOR = 1;

float uct_score(std::shared_ptr<Node> const parent, std::shared_ptr<Node> const child) {
    // TODO sanity check
    float const exploitation = child->win_rate();
    float const exploration = std::sqrt(std::log(parent->visit_count + 1) / (child->visit_count + 1));
    return exploitation + EXPLORATION_FACTOR * exploration;
}
