import pickle
import matplotlib.pyplot as plt
import torch
import os
import numpy as np
import json
import pandas as pd
import math
import logging
import hashlib
import time
from tensorboardX import SummaryWriter


global tensorboard_writer
global logger

def generate_dir_name() -> str:
    """Create a unique hash for the filename"""
    hash = hashlib.sha1()
    hash.update(str(time.time()).encode('utf-8'))
    return str(hash.hexdigest())


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
    logger.info(f"saved model to {path}")


def save_loss(train_loss, validation_loss, accuracy, path):
    with open(os.path.join(path, "data.pkl"), "wb") as f:
        pickle.dump({"train_loss": train_loss, "validation_loss": validation_loss, "accuracy": accuracy}, f)

def setup_logger(log_dir, log_level=logging.DEBUG):
    """
    creates a console and file logger and
    a tensorboard logger
    """
    global tensorboard_writer, logger
    tensorboard_writer = SummaryWriter(log_dir)

    logger = logging.getLogger("TRAIN_LOGGER")
    logger.setLevel(log_level)

    # console logger
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler_format = '%(message)s'
    console_handler.setFormatter(logging.Formatter(console_handler_format))
    logger.addHandler(console_handler)

    # file logger
    file_handler = logging.FileHandler(os.path.join(log_dir, 'log.txt'))
    file_handler.setLevel(log_level)
    file_handler_format = '%(message)s'
    file_handler.setFormatter(logging.Formatter(file_handler_format))
    logger.addHandler(file_handler)

    return logger

def log_stats(epoch, train, validation):
    """
    log the training stats to tensorboard, console and
    a log file
    """
    global tensorboard_writer, logger
    train_loss, train_acc = train
    val_loss, val_acc = validation
    msg = f"-------------------------------------\n"\
    f"Epoch {epoch}\n"\
    f"Train loss {train_loss:>7f}, accuracy {train_acc:>7f}\n"\
    f"Val loss {val_loss:>7f}, accuracy {val_acc:>7f}\n"\
    "-------------------------------------\n"

    logger.info(msg)


    tensorboard_writer.add_scalar('train/loss', train_loss, epoch)
    tensorboard_writer.add_scalar('train/accuracy', train_acc, epoch)
    tensorboard_writer.add_scalar('val/loss', val_loss, epoch)
    tensorboard_writer.add_scalar('val/accuracy', val_acc, epoch)