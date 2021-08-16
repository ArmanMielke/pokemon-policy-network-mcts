#! /bin/bash

#--------------------------------
# Important to change
WEBSOCKET="showdown-mcts-server"
PORT=8081
#AME_MODE="gen8randombattle"
#GAME_MODE="gen8randombattle3@@@Dynamax Clause"
GAME_MODE="gen8customgame@@@Dynamax Clause"
TEAM_DIR="switch_three_pokemon"
TEAM_DIR_MCTS="/mcts/teams/switch_three_pokemon_packed"
#--------------------------------

#-------------------------------
# Not that important to change
BATTLE_BOT="most_damage"
ENV_DEST="pmariglia/envs"
COUNT=10
RUN_COUNT=2
BASE_IP="172.25.0.0"
SERVER_SERVICE="showdown-mcts"
POSTFIX="-1"
COMPOSE_TYPE="mcts"
FILE_DEST="mcts-docker-compose.yml"
DATA_DIR="dataset"
TIMER="False"
ROLLOUTS=200
ROLLOUT_LENGTH=100
#-------------------------------

python3 pmariglia/envs/create_envs.py --websocket "$WEBSOCKET:$PORT" \
    --count $COUNT --runcount $RUN_COUNT --gamemode "$GAME_MODE" \
    --datadir $DATA_DIR --teamdir $TEAM_DIR --battlebot $BATTLE_BOT \
    --dest $ENV_DEST --timer $TIMER

python3 create_compose.py --count $COUNT --port $PORT \
    --baseip $BASE_IP --servername $WEBSOCKET --serverservice $SERVER_SERVICE \
    --postfix $POSTFIX --kind $COMPOSE_TYPE --dest $FILE_DEST \
    --gameformat "$GAME_MODE" --teamdir $TEAM_DIR_MCTS --numbattles $RUN_COUNT \
    --rollouts $ROLLOUTS --rollout-length $ROLLOUT_LENGTH

mkdir tmp
seq $COUNT | xargs -I {} bash -c "touch tmp/accept{}.txt; touch tmp/log{}.txt"