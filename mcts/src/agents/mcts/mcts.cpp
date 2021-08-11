#include "mcts.h"
#include "node.h"
#include "uct_score.h"
#include "../../showdown_simulator.h"

#include <array>
#include <iostream>
#include <memory>
#include <random>
#include <string>
#include <vector>


int const NUM_ROLLOUTS = 100;
int const MAX_ROLLOUT_LENGTH = 100;


/// Selects the action with the highest UCT score.
/// @return the selected action and the node that is reached with this action.
// TODO if node->visit_count is 0 then we haven't explored this node yet
//      Ideally, choose a random action in this case instead of the first action,
//      or sample from a distribution determined by the scores
std::pair<Action, std::shared_ptr<Node>> select_action(std::shared_ptr<Node> const node) {
    if (node->visit_count == 0) {
        // we haven't explored this node before => choose a random action
        std::random_device r;
        std::default_random_engine generator{r()};
        std::uniform_int_distribution<> action_distribution{0, node->children.size() - 1};
        int const action_index = action_distribution(generator);

        auto const pair = std::next(std::begin(node->children), action_index);
        return std::pair<Action, std::shared_ptr<Node>>{pair->first, pair->second};
    }

    std::pair<Action, std::shared_ptr<Node>> best_action;
    float best_score = - std::numeric_limits<float>::infinity();

    for (std::pair<Action, std::shared_ptr<Node>> const action_child_pair: node->children) {
        float score = uct_score(node, action_child_pair.second);
        if (score > best_score) {
            best_score = score;
            best_action = action_child_pair;
        }
    }

    return best_action;
}

void backpropagate(std::vector<std::shared_ptr<Node>> search_path, Player const winner) {
    for (std::shared_ptr<Node> node : search_path) {
        node->visit_count++;
        if (node->turn_player == winner) {
            node->number_of_wins += 1;
        }
    }
}

/// @return the action with the highest win rate.
// TODO consider sampling from a distribution determined by the win rates instead of choosing the highest win rate
Action select_final_action(std::shared_ptr<Node> const root) {
    Action best_action;
    float best_win_rate = - std::numeric_limits<float>::infinity();

    for (auto const [action, child]: root->children) {
        if (child->opponent_win_rate() > best_win_rate) {
            best_win_rate = child->opponent_win_rate();
            best_action = action;
        }
    }

    return best_action;
}

Action run_mcts(std::string const input_log) {
    std::shared_ptr<Node> root = std::make_shared<Node>(1);

    for (int i = 0; i < NUM_ROLLOUTS; i++) {
        ShowdownSimulator simulator;
        simulator.execute_commands(input_log);
        std::vector<std::shared_ptr<Node>> search_path = {root};
        std::shared_ptr<Node> current_node = root;

        for (int j = 0; j < MAX_ROLLOUT_LENGTH && !simulator.is_finished(); j++) {
            current_node->expand(simulator);
            auto const [action, node] = select_action(current_node);

            // apply action
            simulator.execute_commands(">p" + std::to_string(current_node->turn_player) + " " + action);

            current_node = node;
            search_path.push_back(node);
        }

        Player winner;
        if (simulator.is_finished() && simulator.get_winner().has_value()) {
            // game has ended => can use the actual result of the game
            winner = simulator.get_winner().value();
        } else if (!simulator.is_finished()) {
            // game has not yet ended => find out who has more Pokémon left and use that to approximate the result
            std::array<int, 2> num_remaining_pokemon = simulator.get_num_remaining_pokemon();
            if (num_remaining_pokemon[0] > num_remaining_pokemon[1]) {
                // Player 1 has more Pokémon left
                winner = 1;
            } else if (num_remaining_pokemon[0] < num_remaining_pokemon[1]) {
                // Player 2 has more Pokémon left
                winner = 2;
            } else {
                continue;
            }
        } else {
            continue;
        }
        // backpropagate the result of the game
        backpropagate(search_path, winner);
    }

    return select_final_action(root);
}
