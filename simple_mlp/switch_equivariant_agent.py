import torch
from torch import nn


NUM_ACTIONS = 4


class SwitchEquivariantAgent(nn.Module):
    move_network: nn.Sequential

    def __init__(self, p1_pokemon_size: int, p2_size: int):
        super().__init__()

        self.move_network = nn.Sequential(
            nn.Linear(p1_pokemon_size + p2_size, 128),
            nn.ReLU(inplace=True),
            nn.Linear(128, 128),
            nn.ReLU(inplace=True),
            nn.Linear(128, 128),
            nn.ReLU(inplace=True),
            nn.Linear(128, NUM_ACTIONS),
        )

        self.switch_network = nn.Sequential(
            nn.Linear(p1_pokemon_size + p2_size, 128),
            nn.ReLU(inplace=True),
            nn.Linear(128, 128),
            nn.ReLU(inplace=True),
            nn.Linear(128, 128),
            nn.ReLU(inplace=True),
            nn.Linear(128, 1),
        )

    def forward(self, p1: torch.Tensor, p2: torch.Tensor) -> torch.Tensor:
        p2 = p2.flatten(start_dim=1)

        # attacking moves
        active_pokemon_and_opponent = torch.cat([p1[:, 0, :], p2], dim=1)
        move_logits = self.move_network(active_pokemon_and_opponent)

        # switch actions
        second_pokemon_and_opponent = torch.cat([p1[:, 1, :], p2], dim=1)
        switch_2_logit = self.switch_network(second_pokemon_and_opponent)
        third_pokemon_and_opponent = torch.cat([p1[:, 1, :], p2], dim=1)
        switch_3_logit = self.switch_network(third_pokemon_and_opponent)
        # at the moment switching to any pokemon is seen as one action by the data set, so we combine the two logits
        switch_logit = torch.maximum(switch_2_logit, switch_3_logit)

        return torch.cat([move_logits, switch_logit], dim=1)
