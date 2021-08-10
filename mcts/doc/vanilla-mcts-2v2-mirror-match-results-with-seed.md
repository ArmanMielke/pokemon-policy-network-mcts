# Evaluation of Vanilla MCTS on a 2v2 mirror match setting (using the battle's seed)

## Team

```
Venusaur|||Chlorophyll|Venoshock,GrassPledge|Modest|4,,,252,,252||,0,,,,|||]Pikachu|||LightningRod|Double-Edge,RisingVoltage|Hasty|4,,,252,,252||,0,,,,|||
```

## How Many times did MCTS win against the baseline agent

- search-depth-100-num-rollouts-100-vs-pmariglia
    - 15/21
- search-depth-100-num-rollouts-50-vs-pmariglia
    - 11/21
    - 8/20
- search-depth-100-num-rollouts-75-vs-pmariglia
    - 3/8
    - 3/6
    - 10/14
- search-depth-10-num-rollouts-100-vs-pmariglia
    - 7/15
    - 9/21
- search-depth-10-num-rollouts-50-vs-pmariglia
    - 5/13
    - 11/21
- search-depth-10-num-rollouts-75-vs-pmariglia
    - 7/15
    - 8/29
- search-depth-100-num-rollouts-100-vs-most-damage
    - 7/10
    - 7/10
    - 3/6

