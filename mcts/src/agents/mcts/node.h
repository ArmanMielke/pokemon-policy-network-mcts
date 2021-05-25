#ifndef POKEMON_MCTS_MCTS_AGENT_NODE_H
#define POKEMON_MCTS_MCTS_AGENT_NODE_H

#include "../../showdown_simulator.h"

#include <memory>
#include <string>


typedef std::string Action;

class Node {
public:
    /// The player whose turn it is at this node.
    Player turn_player;
    int visit_count = 0;
    int number_of_wins = 0;
    std::map<Action, std::shared_ptr<Node>> children;

    explicit Node(Player const turn_player);

    /// @param simulator: A simulator set up with the same state that this node represents.
    void expand(ShowdownSimulator& simulator);
    /// @return `true`, iff expand() has been called before.
    bool is_expanded() const;
    /// @return number_of_wins / visit_count.
    ///         Returns 0 if visit_count is 0.
    float win_rate() const;
    /// @return 2 if turn_player is 1, or 1 if turn_player is 2.
    Player next_player() const;
};


#endif //POKEMON_MCTS_MCTS_AGENT_NODE_H
