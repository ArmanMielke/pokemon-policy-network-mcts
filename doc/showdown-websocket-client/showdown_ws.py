import requests
from websocket import create_connection


###################################################
# IMPORTANT                                       #
#                                                 #
# This script is not meant to be run, but instead #
# serves as an illustration of how to connect to  #
# Pokémon Showdown using a WebSocket connection.  #
#                                                 #
# It assumes that Showdown has been started with  #
# ./pokemon-showdown start --no-security 8808     #
###################################################


LOGIN_URI = "https://play.pokemonshowdown.com/action.php"
USERNAME = "python-rtzaisdua"


# establish connection
ws = create_connection("ws://localhost:8808/showdown/websocket")
ws.recv()

# log in to Pokémon Showdown
challstr_message = ws.recv()
_, _, client_id, challstr = challstr_message.split('|')
login_request_data = {
    'act': 'getassertion',
    'userid': USERNAME,
    'challstr': '|'.join([client_id, challstr])
}
response = requests.post(LOGIN_URI, data=login_request_data)
ws.send(f"|/trn {USERNAME},0,{response.text}")
ws.recv()
ws.recv()

# join Lobby
ws.send("|/join Lobby")
ws.recv()

# challenge user
user_to_challenge = "dhasuizdhfuia"
battle_format = "gen8randombattle"
ws.send(f"|/challenge {user_to_challenge},{battle_format}")
ws.recv()
