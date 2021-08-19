#include "mcts.h"
#include "node.h"
#include "uct_score.h"
#include "../../policies/policy.h"
#include "../../showdown_simulator/showdown_simulator.h"

#include <array>
#include <iostream>
#include <memory>
#include <optional>
#include <random>
#include <string>
#include <unordered_map>
#include <vector>

#include <boost/optional.hpp>


int const NUM_ROLLOUTS = 100;
int const MAX_ROLLOUT_LENGTH = 100;


/// Selects the action with the highest UCT score.
/// @return the selected action and the node that is reached with this action.
// TODO policy_action_probabilities should be optional
std::pair<Action, std::shared_ptr<Node>> select_action(
    std::shared_ptr<Node> const node,
    std::optional<std::unordered_map<Action, float>> policy_action_probabilities
) {
    if (policy_action_probabilities.has_value()) {
        // insert a dummy value for noop. it doesn't matter which value is inserted, because this action can only
        // be taken if there is no other action available
        policy_action_probabilities->insert({"noop", 1});
    }

    if (node->visit_count == 0) {
        // we haven't explored this node before => choose a random action
        // TODO use policy_action_probabilities
        std::random_device r;
        std::default_random_engine generator{r()};
        std::uniform_int_distribution<> action_distribution{0, node->children.size() - 1};
        int const action_index = action_distribution(generator);

        auto const pair = std::next(std::begin(node->children), action_index);
        return {pair->first, pair->second};
    }

    std::pair<Action, std::shared_ptr<Node>> best_action;
    float best_score = - std::numeric_limits<float>::infinity();

    for (auto const [action, child]: node->children) {
        float score;
        if (policy_action_probabilities.has_value()) {
            score = uct_score_with_policy(node, child, policy_action_probabilities->at(action));
        } else {
            score = uct_score(node, child);
        }

        if (score > best_score) {
            best_score = score;
            best_action = {action, child};
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

Action run_mcts(std::string const input_log, boost::optional<Policy&> policy) {
    std::shared_ptr<Node> root = std::make_shared<Node>(1);

    for (int i = 0; i < NUM_ROLLOUTS; i++) {
        ShowdownSimulator simulator;
        simulator.execute_commands(input_log);
        std::vector<std::shared_ptr<Node>> search_path = {root};
        std::shared_ptr<Node> current_node = root;

        for (int j = 0; j < MAX_ROLLOUT_LENGTH && !simulator.is_finished(); j++) {
            current_node->expand(simulator);

            // evaluate policy (if there is one)
            std::optional<std::unordered_map<Action, float>> policy_action_probabilities = std::nullopt;
            if (policy.has_value()) {
                PlayerData const p1 = simulator.get_player_info(1);
                PlayerData const p2 = simulator.get_player_info(2);
                policy_action_probabilities = (*policy).evaluate_policy(p1, p2);
            }

            auto const [action, node] = select_action(current_node, policy_action_probabilities);

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
