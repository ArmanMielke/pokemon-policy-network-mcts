# Deep Pokemon MCTS

## MCTS pipeline

The MCTS pipeline is a docker compose setup where
our MCTS agent plays against our baseline agent
pmariglia. <br>
To start the data collection process run
```
docker-compose -f mcts-docker-compose.yml build
docker-compose -f mcts-docker-compsoe.yml up
```
which will create a MCTS agent and one baseline
agent challenging each other on a local Pokemon
showdown server. <br>

To configure the pipeline have a look at `create-mcts-pipeline.sh`.


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
For more indepth information have a look at our [data documentation](./doc/data.md) <br><br>

The data for our 3 Pokemon, 2 Attack setting can be found [here](https://drive.google.com/file/d/1w-p0EcoAz1jilWVLY4zx-RAOws7qGUnd/view?usp=sharing). You need
to extract the zip and change the directories in `simple_mlp/configs/config.json`
accordingly.
