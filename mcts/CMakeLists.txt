cmake_minimum_required(VERSION 3.16)
project(pokemon_mcts)
set(CMAKE_CXX_STANDARD 20)

# Linking fails without -pthread
# https://stackoverflow.com/questions/56092464/linking-errors-for-boost-for-visual-studio-linux-project
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread")

add_executable(pokemon_mcts
    src/main.cpp

    src/showdown_simulator.cpp
    src/showdown_simulator.h

    src/showdown_client/showdown_client.cpp
    src/showdown_client/showdown_client.h
    src/showdown_client/showdown_login_request.cpp
    src/showdown_client/showdown_login_request.h
    src/showdown_client/websocket.cpp
    src/showdown_client/websocket.h

    src/agents/default_action_agent.cpp
    src/agents/default_action_agent.h
    src/agents/mcts_agent.cpp
    src/agents/mcts_agent.h
    src/agents/random_agent.cpp
    src/agents/random_agent.h

    src/agents/mcts/mcts.cpp
    src/agents/mcts/mcts.h
    src/agents/mcts/node.cpp
    src/agents/mcts/node.h
    src/agents/mcts/uct_score.cpp
    src/agents/mcts/uct_score.h
)
