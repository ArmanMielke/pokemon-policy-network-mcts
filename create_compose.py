import argparse
import os

SPACING = " "

def create_volumes_string(volumes):
    volumes_str = ""
    for volume in volumes:
        volumes_str += f"{SPACING}{SPACING}{SPACING}- {volume}\n"
    return volumes_str

def create_server(port, service_name, container_name):
    return f"{SPACING}{service_name}: \n" \
    f"{SPACING}{SPACING} build:\n" \
    f"{SPACING}{SPACING}{SPACING} context: showdown \n" \
    f"{SPACING}{SPACING}{SPACING} dockerfile: Dockerfile\n" \
    f"{SPACING}{SPACING} ports:\n"\
    f"{SPACING}{SPACING} - {port}:{port}\n" \
    f"{SPACING}{SPACING} container_name: {container_name}\n" \
    f"{SPACING}{SPACING} restart: always \n" \
    f"{SPACING}{SPACING} networks:\n" \
    f"{SPACING}{SPACING} - back \n" \
    f"{SPACING}{SPACING} mem_limit: 4GB"

def create_data_pair(server_service, service_name_challenge, service_name_accept, container_name_challenge,
        container_name_accept, port, volumes_challenge, volumes_accept, ip):

    volumes_accept_str = create_volumes_string(volumes_accept)
    volumes_challenge_str = create_volumes_string(volumes_challenge)
    return f"{SPACING}{service_name_accept}:\n"\
    f"{SPACING}{SPACING} depends_on:\n"\
    f"{SPACING}{SPACING} - {server_service}\n"\
    f"{SPACING}{SPACING} build:\n"\
    f"{SPACING}{SPACING}{SPACING} context: pmariglia\n"\
    f"{SPACING}{SPACING}{SPACING} dockerfile: Dockerfile\n"\
    f"{SPACING}{SPACING} expose:\n"\
    f"{SPACING}{SPACING} - {port}\n"\
    f"{SPACING}{SPACING} container_name: {container_name_accept}\n"\
    f"{SPACING}{SPACING} restart: always\n"\
    f"{SPACING}{SPACING} volumes:\n"\
    f"{volumes_accept_str}"\
    f"{SPACING}{SPACING} networks:\n"\
    f"{SPACING}{SPACING} - back\n"\
    f"{SPACING}{service_name_challenge}:\n"\
    f"{SPACING}{SPACING} depends_on:\n"\
    f"{SPACING}{SPACING} - {service_name_accept}\n"\
    f"{SPACING}{SPACING} - {server_service}\n"\
    f"{SPACING}{SPACING} build:\n"\
    f"{SPACING}{SPACING}{SPACING} context: pmariglia\n"\
    f"{SPACING}{SPACING}{SPACING} dockerfile: Dockerfile\n"\
    f"{SPACING}{SPACING} expose:\n"\
    f"{SPACING}{SPACING} - {port}\n"\
    f"{SPACING}{SPACING} container_name: {container_name_challenge}\n"\
    f"{SPACING}{SPACING} restart: always\n"\
    f"{SPACING}{SPACING} volumes:\n"\
    f"{volumes_challenge_str}"\
    f"{SPACING}{SPACING} networks:\n"\
    f"{SPACING}{SPACING}{SPACING} back:\n"\
    f"{SPACING}{SPACING}{SPACING}{SPACING} ipv4_address: {ip}\n"


def create_data_pipeline(args) -> str:
    result_string = ""
    for i in range(args.count):
        accepter_name = f"pmariglia-data-accept-{i+1}{args.postfix}"
        accepter_service = f"pmariglia_data_accept_{i+1}{args.postfix}"
        challenge_name = f"pmariglia-data-challenge-{i+1}{args.postfix}"
        challenge_service = f"pmariglia_data_challenge_{i+1}{args.postfix}"

        volumes_challenge = [
            f"./pmariglia/envs/challenge{i+1}:/showdown/.env",
            "./datasets/collector:/showdown/dataset",
            "./teams:/showdown/teams/teams"
        ]

        volumes_accept = [
            f"./pmariglia/envs/accept{i+1}:/showdown/.env",
            "./datasets/collector:/showdown/dataset",
            "./teams:/showdown/teams/teams"
        ]

        tmp = base_ip.split(".")[:-1]
        tmp.append (str(1) + str(0) + str(i+1) if i < 9 else str(1) + str(i+1))
        ip = ".".join(tmp)

        pair = create_data_pair(args.serverservice, challenge_service, accepter_service,
            challenge_name, accepter_name, args.port, volumes_challenge,
            volumes_accept,ip)

        result_string += pair
        result_string += "\n\n"
    return result_string

def create_mcts_pair(server_service, server_container, pmariglia_service_name, mcts_service_name, 
    pmariglia_container_name, mcts_container_name, port, ip, game_format,
    volumes_pmariglia, volumes_mcts, user_challenge, team_dir,
    num_battles, username, password):

    volumes_mcts_str = create_volumes_string(volumes_mcts)
    volumes_pmariglia_str = create_volumes_string(volumes_pmariglia)

    return f"{SPACING}{pmariglia_service_name}:\n" \
           f"{SPACING}{SPACING} depends_on: \n" \
           f"{SPACING}{SPACING} - {server_service}\n" \
           f"{SPACING}{SPACING} build:\n" \
           f"{SPACING}{SPACING}{SPACING} context: pmariglia\n" \
           f"{SPACING}{SPACING}{SPACING} dockerfile: Dockerfile\n" \
           f"{SPACING}{SPACING} expose:\n" \
           f"{SPACING}{SPACING} - {port} \n" \
           f"{SPACING}{SPACING} container_name: {pmariglia_container_name}\n" \
           f"{SPACING}{SPACING} restart: always\n" \
           f"{SPACING}{SPACING} volumes:\n" \
           f"{volumes_pmariglia_str}" \
           f"{SPACING}{SPACING} networks:\n" \
           f"{SPACING}{SPACING} - back\n" \
           f"{SPACING}{mcts_service_name}:\n" \
           f"{SPACING}{SPACING} depends_on:\n" \
           f"{SPACING}{SPACING} - {server_service}\n" \
           f"{SPACING}{SPACING} - {pmariglia_service_name}\n" \
           f"{SPACING}{SPACING} build:\n" \
           f"{SPACING}{SPACING}{SPACING} context: mcts \n" \
           f"{SPACING}{SPACING}{SPACING} dockerfile: Dockerfile \n" \
           f"{SPACING}{SPACING} expose:\n"\
           f"{SPACING}{SPACING} - {port}\n"\
           f"{SPACING}{SPACING} container_name: {mcts_container_name}\n"\
           f"{SPACING}{SPACING} restart: always\n"\
           f"{SPACING}{SPACING} volumes:\n" \
           f"{volumes_mcts_str}" \
           f"{SPACING}{SPACING} networks: \n" \
           f"{SPACING}{SPACING}{SPACING} back:\n" \
           f"{SPACING}{SPACING}{SPACING}{SPACING} ipv4_address: {ip}\n" \
           f"{SPACING}{SPACING} environment:\n"\
           f"{SPACING}{SPACING} - USER_CHALLENGE={user_challenge}\n" \
           f"{SPACING}{SPACING} - SHOWDOWN_HOST={server_container}\n" \
           f"{SPACING}{SPACING} - SHOWDOWN_PORT={port}\n" \
           f"{SPACING}{SPACING} - GAME_FORMAT={game_format}\n" \
           f"{SPACING}{SPACING} - SHOWDOWN_EXE=/showdown/pokemon-showdown\n"\
           f"{SPACING}{SPACING} - TEAM_DIR={team_dir}\n" \
           f"{SPACING}{SPACING} - NUM_BATTLES={num_battles}\n" \
           f"{SPACING}{SPACING} - USERNAME={username}\n"\
           f"{SPACING}{SPACING} - PASSWORD={password}\n"\

def create_mcts_pipeline(args):
    result = ""
    for i in range(args.count):
        pmariglia_container = f"pmariglia-mcts-accept-{i+1}{args.postfix}"
        pmariglia_service = f"pmariglia_mcts_accept_{i+1}{args.postfix}"
        mcts_container = f"mcts-challenge-{i+1}{args.postfix}"
        mcts_service = f"mcts_challenge_{i+1}{args.postfix}"

        volumes_pmariglia = [
            f"./pmariglia/envs/accept{i+1}:/showdown/.env",
            "./teams:/showdown/teams/teams"
        ]

        volumes_mcts = [
            "./teams:/mcts/teams",
            f"./tmp/log{i+1}.txt:/mcts/log.txt",
            f"./tmp/action{i+1}.txt:/mcts/action.txt"
        ]

        tmp = base_ip.split(".")[:-1]
        tmp.append (str(1) + str(0) + str(i+1) if i < 9 else str(1) + str(i+1))
        ip = ".".join(tmp)

        user_to_challenge = f"dlinvcaccept{i+1}"
        username = f"dlinvcchallenge{i+1}"
        password = "NbmjPcthUbzT4LGz"

        pair = create_mcts_pair(args.serverservice, args.servername, 
            pmariglia_service, mcts_service, pmariglia_container, 
            mcts_container, args.port, ip, args.gameformat,
            volumes_pmariglia, volumes_mcts, user_to_challenge, 
            args.teamdir, args.numbattles, username, password)

        result += pair
        result += "\n\n"
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, help="number of agent pairs", default=16)
    parser.add_argument("--port", type=str, default="8081")
    parser.add_argument("--baseip", type=str, default='172.25.0.0')
    parser.add_argument("--servername", type=str, default='showdown-server')
    parser.add_argument("--serverservice", type=str, default="showdown")
    parser.add_argument("--postfix", type=str, default="", help="this is sometimes needed to resolve naming conflicts")
    parser.add_argument("--kind", type=str, default="data", help="the kind of compose file, e.g. data or mcts")
    parser.add_argument("--dest", type=str, default="docker-compose.yml", help="file to store the compose setup")
    parser.add_argument("--gameformat", type=str, default="gen8randombattle")
    parser.add_argument("--teamdir", type=str, default="")
    parser.add_argument("--numbattles", type=int, default=10)
    args = parser.parse_args()

    with open(args.dest, 'w') as f:

        docker_compose_header = "version: \"3\"\nservices:\n"
        server = create_server(args.port, args.serverservice, args.servername)

        base_ip = args.baseip

        docker_compose_networks = f"networks:\n"\
        f"{SPACING} back:\n"\
        f"{SPACING}{SPACING} driver: bridge\n"\
        f"{SPACING}{SPACING} ipam:\n"\
        f"{SPACING}{SPACING}{SPACING} config:\n"\
        f"{SPACING}{SPACING}{SPACING} - subnet: {base_ip}/24"

        f.write(docker_compose_header)
        f.write(server)
        f.write("\n\n")


        result = create_data_pipeline(args) if args.kind == "data" else create_mcts_pipeline(args)
        f.write(result)
        
        f.write(docker_compose_networks)
        
