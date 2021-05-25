#include "node.h"
#include "../../showdown_simulator.h"

#include <vector>


Node::Node(Player const turn_player) {
    this->turn_player = turn_player;
}

void Node::expand(ShowdownSimulator &simulator) {
    if (this->is_expanded()) { return; }

    std::vector<Action> actions = simulator.get_actions(this->turn_player);

    if (actions.empty()) {
        // this is an unrecognised action and therefore does nothing
        actions.push_back("noop");
    }

    for (Action action : actions) {
        this->children[action] = std::make_shared<Node>(this->next_player());
    }
}

bool Node::is_expanded() const {
    return !this->children.empty();
}

float Node::win_rate() const {
    if (this->visit_count == 0) {
        return 0;
    } else {
        return static_cast<float>(this->number_of_wins) / this->visit_count;
    }
}

Player Node::next_player() const {
    return (this->turn_player % 2) + 1;
}
