import torch
from dataloader.dataset import PokemonDataset
from torch.utils.data import DataLoader
from network import PokemonAgent, SimpleMLP
from config import SimpleMLPConfig
import argparse
import numpy as np
import os

from captum.attr import IntegratedGradients

from train import transform_data


# while True:
#     tmp_input = input('some input:')
#     values = tmp_input.split(',')
#     x = torch.tensor([float(values[0]), float(values[1])], dtype=torch.float)
#     pred = model(x)
#     print(f"the prediction is {pred}")

def compute_integrated_gradients(model, input, target):
    ig = IntegratedGradients(model)
    return ig.attribute(input, target=target)
    
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--modeldir", type=str, help="the directory where the training data is located")
    parser.add_argument("--testdata", type=str, help="the directory where the test data is located")
    args = parser.parse_args()

    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

    config = SimpleMLPConfig(os.path.join(args.modeldir, 'config.json'))

    dataset = PokemonDataset(args.testdata, config.features, [])
    dataloader = DataLoader(dataset, batch_size=config.batch_size, shuffle=True)

    p1,p2,y = dataset[0]
    input_size, output_size = len(p1.flatten())+len(p2.flatten()), len(y)

    if config.config["use_simple_mlp"]:
        model = SimpleMLP(
            input_size,
            output_size,
            config.config["layers"],
            config.config["neurons"]
        ).to(DEVICE)
    else:
        num_pokemon = p1.shape[0]
        pkmn_input_size = p1.shape[1]
        pkmn_output_size = y.shape[0]
        p2_size = len(p2.flatten())
        agent_input_size = num_pokemon * pkmn_output_size + p2_size
        agent_output_size = y.shape[0]

        model = PokemonAgent(
            (pkmn_input_size, agent_input_size),
            (pkmn_output_size, agent_output_size),
            (config.config['pokemon_encoder']['layers'], config.config['pokemon_agent']['layers']),
            (config.config['pokemon_encoder']['neurons'], config.config['pokemon_agent']['neurons']),
        ).to(DEVICE)

    model.load_state_dict(torch.load(os.path.join(args.modeldir, "best_model.pth")))
    model.eval()

    num_evaluation_iterations = 5
    evaluation_acc = []
    for i in range(num_evaluation_iterations):
        with torch.no_grad():
            iteration_acc = []
            for p1, p2, y in dataloader:
                p1, p2, label = transform_data(p1, p2, y)
                preds = model(p1, p2)
                iteration_acc.append((preds.argmax(1) == label).type(torch.float).mean().item())
            evaluation_acc.append(np.mean(np.array(iteration_acc)))
    
    print(f"Accuracy is: {np.mean(np.array(evaluation_acc))}")
