#include "showdown_client/showdown_client.h"
#include "agents/mcts_agent.h"

#include <fstream>
#include <iostream>
#include <string>


int const NUM_BATTLES = 100;
std::string const LOG_FILE = "log.txt";

std::string const user_to_challenge = std::getenv("USER_CHALLENGE");

void log_result(bool const battle_won) {
    std::fstream file_stream;
    file_stream.open(LOG_FILE, std::ios::app);
    file_stream << battle_won << std::endl;
    file_stream.close();
}


int main() {
    ShowdownClient client{"dlinvcchallenge1", std::optional<std::string>{"JbNeAhqXqw35EEAR"}};
    client.set_team("<packed team>");

    for (int i = 0; i < NUM_BATTLES; i++) {
        std::cout << user_to_challenge << std::endl;
        std::string battle_room_name = client.challenge_user("dlinvcaccept1", "gen8randombattle");
        std::cout << "Got Battle room: " << battle_room_name << std::endl;
        bool const battle_won = start_mcts_agent(client, battle_room_name);
        log_result(battle_won);

        std::cout << "Battle result: " << battle_won << std::endl;
    }
}
