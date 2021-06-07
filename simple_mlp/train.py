import torch
import numpy as np
import os
from tensorboardX import SummaryWriter
import argparse
import hashlib
import time

from dataloader.dataloader import Dataloader
from network import SimpleMLP
from utils import copy_config_to_output_dir, save_model, save_figure, save_loss
from config import SimpleMLPConfig

def generate_dir_name():    
    """Create a unique hash for the filename"""
    hash = hashlib.sha1()
    hash.update(str(time.time()).encode('utf-8'))
    return str(hash.hexdigest())

parser = argparse.ArgumentParser()
parser.add_argument("--dir", type=str, default=generate_dir_name(), 
    help="the directory to store the data, e.g. model, plots etc.")
parser.add_argument("--config", type=str)
args = parser.parse_args()

config = SimpleMLPConfig(args.config)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def train(dataloader, model, loss_fn, optimizer):
    losses = []
    last_loss = 0
    # play batch_size many games
    # until the end
    for X, y, end in dataloader:
        X = torch.from_numpy(X).float().to(DEVICE)
        # CrossEntropyLoss does not like a one-hot vector but
        # a sigle integer indicating which class it belongs to
        label = torch.from_numpy(np.array([np.argmax(y[i]) for i in range(len(y))])) \
                .long().to(DEVICE)
        preds = model(X)
        loss = loss_fn(preds, label)
        diff = abs(loss - last_loss)
        if diff > 5:
            dataloader.trace_back(preds)
        last_loss = loss
        losses.append(loss.item())
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if end:
            return np.mean(losses)


def validate(dataloader, model, loss_fn):
    model.eval()
    losses = []
    with torch.no_grad():
        for X, y, end in dataloader:

            X = torch.from_numpy(X).float().to(DEVICE)
            label = torch.from_numpy(np.array([np.argmax(y[i]) for i in range(len(y))]))\
                .long().to(DEVICE)
            preds = model(X)
            losses.append( loss_fn(preds, label).item() )
            if end:
                return np.mean(losses)

# TODO: maybe merge training and validation dataloader into
# one single loader, whichs returns the corresponding generators
dataloader = Dataloader(config.train_data_path, config.batch_size,
    # TODO: implement functionality to easily pick the features you
    # want in your batch
    ['p1/hp', 'p2/hp', 'p1/last_move', 'p2/last_move', 'turn']
)
dataloader.load_data()

val_dataloader = Dataloader(config.validation_data_path, config.batch_size,
    ['p1/hp', 'p2/hp', 'p1/last_move', 'p2/last_move', 'turn']
)
val_dataloader.load_data()

model = SimpleMLP(
    dataloader.get_input_size(),
    dataloader.get_output_size(),
    config.config["layers"],
    config.config["neurons"]
)

# trace the model to create a torch script instance
# you need to provide a example input. This
# can then be loaded with libtorch in C++
script_model = torch.jit.trace(model, torch.rand(1,dataloader.get_input_size()))


model.to(DEVICE)
loss_fn = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)

RUN_DIR = os.path.join("runs", args.dir)

writer = SummaryWriter(RUN_DIR)
copy_config_to_output_dir(RUN_DIR, config.config)
train_loss, test_loss = [], []

if __name__ == "__main__":

    for t in range(config.epochs):
        loss = train(dataloader, model, loss_fn, optimizer)
        tloss = validate(val_dataloader, model, loss_fn)
        print(f"Epoch {t}\n-----------------")
        print(f"loss: {loss:>7f}")
        print(f"val loss: {tloss:>7f}")
        print(f"DEVICE {DEVICE}")
        writer.add_scalar('loss', loss, t)
        writer.add_scalar('test_loss', tloss, t)
        train_loss.append(loss)
        test_loss.append(tloss)

        # for each epoch we want
        # a new set of games
        dataloader.reset()
        dataloader.load_data()

    
    save_figure(config.epochs, train_loss, test_loss, RUN_DIR)
    save_model(model, script_model, RUN_DIR)
    save_loss(train_loss, test_loss, RUN_DIR)