from torch import nn
import torch.nn.functional as F

class SimpleMLP(nn.Module):
    def __init__(self, input_size, output_size, layers, neurons):
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
