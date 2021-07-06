import torch
from dataloader.dataset import PokemonDataset
from torch.utils.data import DataLoader
from network import SimpleMLP
from config import SimpleMLPConfig
import argparse
import numpy as np
import os

from captum.attr import IntegratedGradients


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

    model = SimpleMLP(
        input_size,
        output_size,
        config.config["layers"],
        config.config["neurons"]
    ).to(DEVICE)

    model.load_state_dict(torch.load(os.path.join(args.modeldir,"model.pth")))
    model.eval()

    num_evaluation_iterations = 5
    evaluation_acc = []
    for i in range(num_evaluation_iterations):
        with torch.no_grad():
            iteration_acc = []
            for p1, p2, y in dataloader:
                p1 = p1.flatten(start_dim=1)
                p2 = p2.flatten(start_dim=1)
                input = torch.cat((p1,p2), dim=1).float().to(DEVICE)
                label = y.argmax(dim=1).long().to(DEVICE)
                preds = model(input)
                iteration_acc.append((preds.argmax(1) == label).type(torch.float).mean().item())
            evaluation_acc.append(np.mean(np.array(iteration_acc)))
    
    print(f"Accuracy is: {np.mean(np.array(evaluation_acc))}")