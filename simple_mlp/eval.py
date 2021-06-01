import torch
from dataloader.dataloader import Dataloader
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
    parser.add_argument("--dir", type=str, help="the directory where the training data is located")
    args = parser.parse_args()

    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

    config = SimpleMLPConfig(os.path.join(args.dir, 'config.json'))

    val_dataloader = Dataloader(config.validation_data_path, config.batch_size,
        ['p1/hp', 'p2/hp', 'p1/last_move', 'p2/last_move', 'turn']
    )
    val_dataloader.load_data()

    model = SimpleMLP(
        val_dataloader.get_input_size(),
        val_dataloader.get_output_size(),
        config.config["layers"],
        config.config["neurons"]
    ).to(DEVICE)

    model.load_state_dict(torch.load(os.path.join(args.dir,"model.pth")))
    model.eval()
    np.random.seed(123)
    torch.manual_seed(123)
    input, y, _ = next(val_dataloader)
    input = torch.from_numpy(input).float().to(DEVICE)

    attribution_t0 = compute_integrated_gradients(model, input, 0)
    attribution_t1 = compute_integrated_gradients(model, input, 1)
    attribution_t2 = compute_integrated_gradients(model, input, 2)
    attribution_t3 = compute_integrated_gradients(model, input, 3)

    print({
        "t0" : [attribution_t0.mean(axis=0), attribution_t0.std(axis=0)],
        "t1" : [attribution_t1.mean(axis=0), attribution_t1.std(axis=0)],
        "t2" : [attribution_t2.mean(axis=0), attribution_t2.std(axis=0)],
        "t3" : [attribution_t3.mean(axis=0), attribution_t3.std(axis=0)]
    })
    