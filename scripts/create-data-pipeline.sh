#! /bin/bash
SCRIPT_DIR=`dirname "$0"`
BASE_DIR=$SCRIPT_DIR/..

#--------------------------------
# Important to change
WEBSOCKET="showdown-server"
PORT=8081
#GAME_MODE="gen8randombattle"
#GAME_MODE="gen8randombattle3@@@Dynamax Clause"
GAME_MODE="gen8customgame@@@Dynamax Clause"
TEAM_DIR="switch_three_pokemon"
#--------------------------------

#-------------------------------
# Not that important to change
BATTLE_BOT="most_damage"
ENV_DEST="pmariglia/envs"
COUNT=1
RUN_COUNT=10
BASE_IP="172.25.0.0"
SERVER_SERVICE="showdown"
POSTFIX="-1"
COMPOSE_TYPE="data"
FILE_DEST="$BASE_DIR/docker-compose.yml"
DATA_DIR="dataset"
#-------------------------------


# Create the pmariglia environment files
python3 $BASE_DIR/pmariglia/envs/create_envs.py --websocket "'$WEBSOCKET:$PORT'" \
    --count $COUNT --runcount $RUN_COUNT --gamemode "$GAME_MODE" \
    --datadir $DATA_DIR --teamdir $TEAM_DIR --battlebot $BATTLE_BOT \
    --dest $ENV_DEST

# create the docker compose file
python3 $SCRIPT_DIR/create_compose.py --count $COUNT --port $PORT --baseip $BASE_IP \
    --servername $WEBSOCKET --serverservice $SERVER_SERVICE \
    --postfix $POSTFIX --kind $COMPOSE_TYPE --dest $FILE_DEST