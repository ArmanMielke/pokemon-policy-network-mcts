#!/usr/bin/bash

count=16
dest="pmariglia/envs"
websocket="showdown-server"
service="showdown"
port=8081
baseip="172.25.0.0"
gamemode="gen8custombattle"

python3 pmariglia/envs/create_envs.py --websocket "$websocket:$port" --count $count --runcount 10 --gamemode "$gamemode@@@Dynamax Clause" --datadir dataset --battlebot most_damage --dest $dest 

python3 create_compose.py --count $count --port $port --servername $websocket --serverservice $service 

