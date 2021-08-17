#include "showdown_client/showdown_client.h"
#include "agents/mcts_agent.h"
#include "policies/policy_network.h"

#include <fstream>
#include <iostream>
#include <string>
#include <thread>
#include <chrono>
#include <filesystem>
#include <vector>
#include <random>


std::string const LOG_FILE = "log.txt";

int const NUM_BATTLES = std::atoi(std::getenv("NUM_BATTLES"));
std::string const USER_TO_CHALLENGE = std::getenv("USER_CHALLENGE");
std::string const GAME_FORMAT = std::getenv("GAME_FORMAT");
std::string const TEAM_DIR = std::getenv("TEAM_DIR");
std::string const USERNAME = std::getenv("USERNAME");
std::string const PASSWORD = std::getenv("PASSWORD");
std::string const AGENT = std::getenv("AGENT");

void write_log(std::string const str) {
    std::fstream file_stream;
    file_stream.open(LOG_FILE, std::ios::app);
    file_stream << str << std::endl;
    file_stream.close();
}

void log_result(bool const battle_won) {
    std::fstream file_stream;
    file_stream.open(LOG_FILE, std::ios::app);
    file_stream << battle_won << std::endl;
    file_stream.close();
}

std::string get_team(std::string const team_dir) {
    std::vector<std::string> files;
    for (const auto& file : std::filesystem::directory_iterator(team_dir)) {
        files.push_back(file.path());
    }

    // sample a random file index
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> distrib(0, files.size() -1);
    int const file_index = distrib(gen);
    
    std::string line;
    std::fstream file;
    file.open(files[file_index], std::ios::in);
    if (file.is_open()) {
        std::getline(file, line);
    }
    file.close();
    return line;
}

int main() {
    // Let the other agent do it's setup
    sleep(30);

    ShowdownClient client{USERNAME, std::optional<std::string>{PASSWORD}};
    std::string const team_string = get_team(TEAM_DIR);
    client.set_team(team_string);
    int win_count = 0;
    PolicyNetwork policy_network{"models/three_pokemon_with_data_augmentation.torchscript"};
    for (int i = 0; i < NUM_BATTLES; i++) {
        std::string battle_room_name = client.challenge_user(USER_TO_CHALLENGE, GAME_FORMAT);
        bool const battle_won = start_mcts_agent(client, battle_room_name, policy_network);
        log_result(battle_won);
        win_count += (int)battle_won;
        std::cout << "Battle result: " << battle_won << std::endl;
    }
    write_log("Winrate: "+ std::to_string(win_count) + "/" + std::to_string(NUM_BATTLES));
}
