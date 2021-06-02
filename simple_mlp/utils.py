import pickle
import matplotlib.pyplot as plt
import torch
import os
import numpy as np
import json


def copy_config_to_output_dir(output_path, config):
    with open(os.path.join(output_path, "config.json"), "w") as f:
        f.write(json.dumps(config, indent=4, separators=(',', ': ')))

def save_figure(epochs, train_loss, val_loss, path):
    fig = plt.figure()
    axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    axes.plot(np.arange(0, epochs), train_loss, label='train loss')
    axes.plot(np.arange(0, epochs), val_loss, label='validation loss')
    fig.legend()
    axes.set_xlabel("epochs")
    axes.set_ylabel("loss")
    fig.savefig(os.path.join(path, "graph.png"))
    plt.close()

def save_model(model, script_model, path):
    torch.save(model.state_dict(), os.path.join(path, "model.pth"))
    script_model.save(os.path.join(path, "model_script.pt"))
    print(f"saved model to {path}")


def save_loss(train_loss, test_loss, path):
    with open(os.path.join(path, "data.pkl"), "wb") as f:
        pickle.dump({"train_loss": train_loss, "test_loss": test_loss}, f)