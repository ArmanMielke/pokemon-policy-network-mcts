cmake_minimum_required(VERSION 3.20)
project(pokemon_mcts)

set(CMAKE_CXX_STANDARD 20)

# Linking fails without -pthread
# https://stackoverflow.com/questions/56092464/linking-errors-for-boost-for-visual-studio-linux-project
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread")

add_executable(pokemon_mcts
    src/main.cpp

    src/showdown_client.cpp
    src/showdown_client.h
    src/showdown_login_request.cpp
    src/showdown_login_request.h
    src/websocket.cpp
    src/websocket.h

    src/agents/default_action_agent.cpp
    src/agents/default_action_agent.h
)
