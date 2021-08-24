# Deep Pokemon MCTS

We propose an agent for the game of Pokemon based
on Monte Carlo tree search with a policy network,
pre-trained on a three Pokemon, two move dataset (available [here](https://drive.google.com/file/d/1w-p0EcoAz1jilWVLY4zx-RAOws7qGUnd/view?usp=sharing)).

## MCTS pipeline

The MCTS pipeline is a docker compose setup where
our MCTS agent plays against our baseline agent
[pmariglia](https://github.com/pmariglia/showdown). <br>
To start the data collection process run
```
docker-compose -f mcts-docker-compose.yml build
docker-compose -f mcts-docker-compose.yml up
```
which will create a MCTS agent and one baseline
agent challenging each other on a local [Pokemon
showdown server](https://github.com/smogon/pokemon-showdown). <br>

To configure the pipeline have a look at `scripts/create-mcts-pipeline.sh`.


## Data collection pipeline

For data collection we use Docker and docker-compose
to create multiple [pmariglia](https://github.com/pmariglia/showdown) agents playing against
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
options for this pipeline have a look into `scripts/create-data-pipeline.sh`
which creates all important configuration files.
For more indepth information have a look at our [data documentation](./doc/data.md) <br><br>

The data for our 3 Pokemon, 2 Attack setting can be found [here](https://drive.google.com/file/d/1w-p0EcoAz1jilWVLY4zx-RAOws7qGUnd/view?usp=sharing). You need
to extract the zip and change the directories in `policynet/configs/config.json`
accordingly.
