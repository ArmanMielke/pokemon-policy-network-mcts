import requests
from websocket import create_connection, WebSocket


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
USERNAME = "aisufaisudfh"


def establish_connection() -> WebSocket:
    ws = create_connection("ws://localhost:8808/showdown/websocket")
    print(ws.recv())
    return ws


def log_in_without_password(ws: WebSocket, username: str):
    challstr_message = ws.recv()
    _, _, client_id, challstr = challstr_message.split('|')
    login_request_data = {
        'act': 'getassertion',
        'userid': username,
        'challstr': '|'.join([client_id, challstr])
    }
    response = requests.post(LOGIN_URI, data=login_request_data)
    ws.send(f"|/trn {username},0,{response.text}")
    print(ws.recv())
    print(ws.recv())


def join_lobby(ws: WebSocket):
    ws.send("|/join Lobby")
    print(ws.recv())


def challenge_user(user_to_challenge: str = "dhasuizdhfuia", battle_format: str = "gen8randombattle"):
    ws.send(f"|/challenge {user_to_challenge},{battle_format}")
    print(ws.recv())


if __name__ == "__main__":
    ws = establish_connection()
    log_in_without_password(ws, USERNAME)
    join_lobby(ws)
    challenge_user()
