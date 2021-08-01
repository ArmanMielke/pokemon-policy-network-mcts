# Deep Pokemon MCTS

## Data collection pipeline

In ```pmariglia/envs``` you can find the configuration
files for the challenger and challenge accepter agent. 
For the challenger you need to use a registered user account
with password to get the admin rights. You also need to
add this username to ```showdown/usergroups.csv```. <br><br>
The team configurations are located in ```teams``` where
for the simple setting currently ```only_damage_two_pokemon```
is used. For now the teams are randomily selected at startup.

### With Docker and Docker compose

First we need to create the configuration files for the agents. In
the project root directory run:
```
python3 pmariglia/envs/create_envs.py --teamdir physical_special --dest pmariglia/envs
```
(NOTE: you can change `--teamdir` to any of the folder names in the folder `teams`)

Next we need to setup the docker-compose file. Run in the root dir of the project:
```
python3 create_compose.py
```
This will create a correctly configured `docker-compose.yml`. Finally the 
collection process can be started with:
```
docker-compose up --build
```
This will build the showdown server and 32 agents 
challenging each other.

## Dataloader

### Current supported features

 * `is_active`  Is the Pokemon the active Pokemon
 * `hp` The health points of the Pokemon
 * `stats` The attack, defense etc. of the Pokemon 
 * `type` The element type (e.g. Water, Fire ...) of the Pokemon
 * `move` The move ids of the Pokemon
 * `move_type` The move elements of the Pokemon
 * `move_damage` The move damages of the Pokemon
 * `move_category` The move categories (physical or special) 
