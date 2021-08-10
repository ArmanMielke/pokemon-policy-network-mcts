#include "showdown_client/showdown_client.h"
#include "agents/mcts_agent.h"

#include <fstream>
#include <iostream>
#include <string>
#include <thread>
#include <chrono>
#include <filesystem>
#include <vector>


std::string const LOG_FILE = "log.txt";

int const NUM_BATTLES = std::atoi(std::getenv("NUM_BATTLES"));
std::string const USER_TO_CHALLENGE = std::getenv("USER_CHALLENGE");
std::string const GAME_FORMAT = std::getenv("GAME_FORMAT");
std::string const TEAM_DIR = std::getenv("TEAM_DIR");
std::string const USERNAME = std::getenv("USERNAME");
std::string const PASSWORD = std::getenv("PASSWORD");

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
    int const file_index = std::rand() % files.size();
    
    std::string line;
    std::fstream file;
    file.open(files[file_index], std::ios::in);
    if (file.is_open()) {
        std::getline(file, line);
    }
    return line;
}

int main() {
    std::chrono::seconds timespan(30);
    std::this_thread::sleep_for(timespan);
    ShowdownClient client{USERNAME, std::optional<std::string>{PASSWORD}};
    std::string const team_string = get_team(TEAM_DIR);
    client.set_team(team_string);
    write_log("++++++\nStarting a new Battle\n+++++++++\n Using team " + team_string);

    int win_count = 0;
    for (int i = 0; i < NUM_BATTLES; i++) {
        std::string battle_room_name = client.challenge_user(USER_TO_CHALLENGE, GAME_FORMAT);
        bool const battle_won = start_mcts_agent(client, battle_room_name);
        log_result(battle_won);
        win_count += (int)battle_won;

        std::cout << "Battle result: " << battle_won << std::endl;
    }

    write_log("Winrate: "+ std::to_string(win_count) + "/" + std::to_string(NUM_BATTLES));
    write_log("\n++++++++ End of game ++++++++++++++++\n");
}
