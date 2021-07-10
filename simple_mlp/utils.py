import pickle
import matplotlib.pyplot as plt
import torch
import os
import numpy as np
import json
import pandas as pd
import math


def copy_config_to_output_dir(output_path, config):
    with open(os.path.join(output_path, "config.json"), "w") as f:
        f.write(json.dumps(config, indent=4, separators=(',', ': ')))

def save_figure(epochs, train_loss, val_loss, accuracy, path):
    fig = plt.figure(figsize=(10, 10))
    axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    axes.plot(np.arange(0, epochs), train_loss, label='train loss')
    axes.plot(np.arange(0, epochs), val_loss, label='validation loss')
    fig.legend()
    axes.set_xlabel("epochs")
    axes.set_ylabel("loss")
    fig.savefig(os.path.join(path, "graph.png"))
    plt.close()

    fig = plt.figure()
    axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    neighborhood = math.floor(0.1 * len(train_loss))
    df = pd.DataFrame(train_loss)
    df2 = pd.DataFrame(val_loss)
    axes.plot(df[0], 'tab:blue',alpha=0.5)
    axes.plot(df2[0],'tab:orange', alpha=0.5)
    axes.plot(df[0].rolling(neighborhood).mean(), 'tab:blue', label='train loss')
    axes.plot(df2[0].rolling(neighborhood).mean(), 'tab:orange', label='validation loss')
    fig.legend()
    axes.set_xlabel("epochs")
    axes.set_ylabel("loss")
    fig.savefig(os.path.join(path, "graph2.png"))
    plt.close()

    fig = plt.figure()
    axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    axes.plot(np.arange(0, epochs), accuracy, label='accuracy')
    axes.set_xlabel("epochs")
    axes.set_ylabel("accuracy")
    fig.savefig(os.path.join(path, "accuracy.png"))
    plt.close()

def save_model(model, path):
    torch.save(model.state_dict(), path)
    # script_model.save(os.path.join(path, "model_script.pt"))
    print(f"saved model to {path}")


def save_loss(train_loss, validation_loss, accuracy, path):
    with open(os.path.join(path, "data.pkl"), "wb") as f:
        pickle.dump({"train_loss": train_loss, "validation_loss": validation_loss, "accuracy": accuracy}, f)
