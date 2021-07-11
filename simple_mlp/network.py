from torch import nn
import torch.nn.functional as F
from typing import Tuple
import torch

class SimpleMLP(nn.Module):
    def __init__(self, input_size : int, output_size : int, layers : int, neurons : int):
        super(SimpleMLP, self).__init__()

        self.layers = layers

        self.mlp_stack = nn.ModuleList([nn.Linear(input_size, neurons)])
        self.mlp_stack.extend([nn.Linear(neurons, neurons) for i in range(layers-2)])
        self.mlp_stack.append(nn.Linear(neurons, output_size))

    def forward(self, x):
        result = x
        for i in range(self.layers-1):
            result = F.relu(self.mlp_stack[i](result))
        # We don't need a activation here because
        # Softmax is included in CrossEntropyLoss
        # (needs to be changed if we switch the loss function)
        return self.mlp_stack[-1](result)

class PokemonEncoder(nn.Module):
    def __init__(self, input_size : int, output_size : int, layers : int, neurons : int):
        super(PokemonEncoder, self).__init__()

        self.layers = layers

        self.mlp_stack = nn.ModuleList([nn.Linear(input_size, neurons)])
        self.mlp_stack.extend([nn.Linear(neurons, neurons) for i in range(layers-2)])
        self.mlp_stack.append(nn.Linear(neurons, output_size))

    def forward(self, x):
        result = x
        for i in range(self.layers-1):
            result = F.relu(self.mlp_stack[i](result))
        
        return F.relu(self.mlp_stack[-1](result)) 


class PokemonAgent(nn.Module):
    def __init__(self, input_shape : Tuple, output_size : Tuple, layers : Tuple, neurons : Tuple):
        super(PokemonAgent, self).__init__()
        # self.num_pokemon = input_shape[0]
        self.pokemon_input_size = input_shape[0]
        self.input_size = input_shape[1]
        self.output_size = output_size
        self.pokemon_layer = layers[0]
        self.layers = layers[1]
        self.pokemon_neurons = neurons[0]
        self.neurons = neurons[1]
        self.pokemon_ouput_size = output_size[0]
        self.output_size = output_size[1]

        self.pokemon_encoder = PokemonEncoder(
            self.pokemon_input_size, self.pokemon_ouput_size,
            self.pokemon_layer, self.pokemon_neurons
        )

        self.mlp_stack = nn.ModuleList([nn.Linear(self.input_size, self.neurons)])
        self.mlp_stack.extend([nn.Linear(self.neurons, self.neurons) for i in range(self.layers-2)])
        self.mlp_stack.append(nn.Linear(self.neurons, self.output_size))

    def forward(self, p1, p2):
        pkmn_preds = []
        for i in range(p1.shape[1]):
            prediction = self.pokemon_encoder(p1[:,i])
            pkmn_preds.append(prediction)
        
        p2 = p2.flatten(start_dim=1)
        result = torch.cat((*pkmn_preds,p2), dim=1).float()
        for i in range(self.layers-1):
            result = F.relu(self.mlp_stack[i](result))

        # We don't need a activation here because
        # Softmax is included in CrossEntropyLoss
        # (needs to be changed if we switch the loss function)
        return self.mlp_stack[-1](result)