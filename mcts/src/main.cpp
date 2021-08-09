#include "showdown_client/showdown_client.h"
#include "agents/mcts_agent.h"

#include <fstream>
#include <iostream>
#include <string>
#include <thread>
#include <chrono>


int const NUM_BATTLES = 100;
std::string const LOG_FILE = "log.txt";

std::string const user_to_challenge = std::getenv("USER_CHALLENGE");
std::string const game_format = std::getenv("GAME_FORMAT");

void log_result(bool const battle_won) {
    std::fstream file_stream;
    file_stream.open(LOG_FILE, std::ios::app);
    file_stream << battle_won << std::endl;
    file_stream.close();
}


int main() {
    std::chrono::seconds timespan(30);
    std::this_thread::sleep_for(timespan);
    ShowdownClient client{"dlinvcchallenge1", std::optional<std::string>{"JbNeAhqXqw35EEAR"}};
    //client.set_team("Arcanine|||RunAway|VineWhip,Surf|Adamant|252,164,,,,92|||||]Barraskewda|||RunAway|BranchPoke,Incinerate|Sassy|252,8,116,,132,||,,,,,0|||]Rillaboom|||RunAway|GrassPledge,Surf|Timid|172,,,252,,84||,0,,,,|||||,,");
    client.set_team("Rotom-Heat||HeavyDutyBoots|Levitate|VoltSwitch,Overheat,Thunderbolt,NastyPlot|Timid|,,,252,4,252||,0,,,,|||]Corviknight||Leftovers|Pressure|Roost,Uturn,Defog,BraveBird|Impish|252,,76,,180,|||||]Clefable||Leftovers|MagicGuard|ThunderWave,Moonblast,Wish,Protect|Calm|252,,160,,96,|||||]Seismitoad||Leftovers|WaterAbsorb|Earthquake,StealthRock,Toxic,Scald|Relaxed|252,4,252,,,|||||]Hydreigon||ChoiceScarf|Levitate|DracoMeteor,DarkPulse,FlashCannon,FireBlast|Timid|,,,252,4,252|||||]Gyarados||Leftovers|Moxie|DragonDance,Earthquake,Waterfall,PowerWhip|Adamant|,252,,,4,252|||||");

    for (int i = 0; i < NUM_BATTLES; i++) {
        std::string battle_room_name = client.challenge_user(user_to_challenge, game_format);
        bool const battle_won = start_mcts_agent(client, battle_room_name);
        log_result(battle_won);

        std::cout << "Battle result: " << battle_won << std::endl;
    }
}
