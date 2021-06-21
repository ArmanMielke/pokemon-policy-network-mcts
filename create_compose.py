import argparse
import os

def create_volumes_string(volumes):
    spacing = " "
    volumes_str = ""
    for volume in volumes:
        volumes_str += f"{spacing}{spacing}{spacing}- {volume}\n"
    return volumes_str

def create_server(port, service_name, container_name, volumes):
    volumes_str = create_volumes_string(volumes)
    spacing = " "

    return f"{spacing}{service_name}: \n" \
    f"{spacing}{spacing} build:\n" \
    f"{spacing}{spacing}{spacing} context: showdown \n" \
    f"{spacing}{spacing}{spacing} dockerfile: Dockerfile\n" \
    f"{spacing}{spacing} ports:\n"\
    f"{spacing}{spacing} - {port}:{port}\n" \
    f"{spacing}{spacing} container_name: {container_name}\n" \
    f"{spacing}{spacing} restart: always \n" \
    f"{spacing}{spacing} volumes:\n" \
    f"{volumes_str}" \
    f"{spacing}{spacing} networks:\n" \
    f"{spacing}{spacing} - back"

def create_pair(server_service, service_name_challenge, service_name_accept, container_name_challenge,
        container_name_accept, port, volumes_challenge, volumes_accept, ip):

    volumes_accept_str = create_volumes_string(volumes_accept)
    volumes_challenge_str = create_volumes_string(volumes_challenge)
    spacing = " "

    return f"{spacing}{service_name_accept}:\n"\
    f"{spacing}{spacing} depends_on:\n"\
    f"{spacing}{spacing} - {server_service}\n"\
    f"{spacing}{spacing} build:\n"\
    f"{spacing}{spacing}{spacing} context: pmariglia\n"\
    f"{spacing}{spacing}{spacing} dockerfile: Dockerfile\n"\
    f"{spacing}{spacing} expose:\n"\
    f"{spacing}{spacing} - {port}\n"\
    f"{spacing}{spacing} container_name: {container_name_accept}\n"\
    f"{spacing}{spacing} restart: always\n"\
    f"{spacing}{spacing} volumes:\n"\
    f"{volumes_accept_str}"\
    f"{spacing}{spacing} networks:\n"\
    f"{spacing}{spacing} - back\n"\
    f"{spacing}{service_name_challenge}:\n"\
    f"{spacing}{spacing} depends_on:\n"\
    f"{spacing}{spacing} - {service_name_accept}\n"\
    f"{spacing}{spacing} - {server_service}\n"\
    f"{spacing}{spacing} build:\n"\
    f"{spacing}{spacing}{spacing} context: pmariglia\n"\
    f"{spacing}{spacing}{spacing} dockerfile: Dockerfile\n"\
    f"{spacing}{spacing} expose:\n"\
    f"{spacing}{spacing} - {port}\n"\
    f"{spacing}{spacing} container_name: {container_name_challenge}\n"\
    f"{spacing}{spacing} restart: always\n"\
    f"{spacing}{spacing} volumes:\n"\
    f"{volumes_challenge_str}"\
    f"{spacing}{spacing} networks:\n"\
    f"{spacing}{spacing}{spacing} back:\n"\
    f"{spacing}{spacing}{spacing}{spacing} ipv4_address: {ip}\n"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, help="number of agent pairs")
    parser.add_argument("--port", type=str)
    parser.add_argument("--baseip", type=str, default='172.25.0.0')
    parser.add_argument("--servername", type=str, default='showdown-server')
    parser.add_argument("--serverservice", type=str, default="showdown")
    args = parser.parse_args()
    spacing = " "

    with open('docker-compose.yml', 'w') as f:

        docker_compose_header = "version: \"3\"\nservices:\n"
        server = create_server(args.port, args.serverservice, args.servername,
        ["./showdown/config.js:/pokemon-showdown/config/config.js", 
        "./showdown/usergroups.csv:/pokemon-showdown/config/usergroups.csv"])

        base_ip = args.baseip

        docker_compose_networks = f"networks:\n"\
        f"{spacing} back:\n"\
        f"{spacing}{spacing} driver: bridge\n"\
        f"{spacing}{spacing} ipam:\n"\
        f"{spacing}{spacing}{spacing} config:\n"\
        f"{spacing}{spacing}{spacing} - subnet: {base_ip}/24"

        f.write(docker_compose_header)
        f.write(server)
        f.write("\n\n")


        for i in range(args.count):
            accepter_name = f"pmariglia-accept-{i+1}"
            accepter_service = f"pmariglia_accept_{i+1}"
            challenge_name = f"pmariglia-challenge-{i+1}"
            challenge_service = f"pmariglia_challenge_{i+1}"

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

            pair = create_pair(args.serverservice, challenge_service, accepter_service,
                challenge_name, accepter_name, args.port, volumes_challenge,
                volumes_accept,ip)

            f.write(pair)
            f.write("\n\n")
        
        f.write(docker_compose_networks)
        
