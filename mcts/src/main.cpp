#include "showdown_client/showdown_client.h"
#include "agents/mcts_agent.h"
#include "policies/policy_network.h"

#include <fstream>
#include <iostream>
#include <string>


int const NUM_BATTLES = 100;
std::string const LOG_FILE = "log.txt";


void log_result(bool const battle_won) {
    std::fstream file_stream;
    file_stream.open(LOG_FILE, std::ios::app);
    file_stream << battle_won << std::endl;
    file_stream.close();
}


int main() {
    ShowdownClient client{"cpp-djcoaisjdcoai", std::optional<std::string>{"<password>"}};
    client.set_team("<packed team>");

    PolicyNetwork policy_network{"models/three_pokemon_with_data_augmentation.torchscript"};
    for (int i = 0; i < NUM_BATTLES; i++) {
        std::string battle_room_name = client.challenge_user("pmariglia-sidudhc", "gen8customgame@@@Dynamax Clause");
        bool const battle_won = start_mcts_agent(client, battle_room_name, policy_network);
        log_result(battle_won);

        std::cout << "Battle result: " << battle_won << std::endl;
    }
}
