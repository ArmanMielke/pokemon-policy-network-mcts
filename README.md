# Deep Pokemon MCTS

## Data collection pipeline

For data collection we use Docker and docker-compose
to create multiple pmariglia agents playing against
each other. <br><br>

To start the data collection process run
```
docker-compose build
docker-compose up
```
which will create by default one pair of agents
playing against each other and saving the game states
to `datasets/collector`. <br><br>

To change the amount of agents or other configuration
options for this pipeline have a look into `create-data-pipeline.sh`
which creates all important configuration files.
For more indepth information have a look at our [data documentation](./doc/data.md)

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
