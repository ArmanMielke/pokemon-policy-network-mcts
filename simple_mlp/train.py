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
from earlystopping import EarlyStopping
from lrscheduler import LRScheduler

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

def train(dataloader, model, loss_fn, optimizer, iterations):
    losses = []
    last_loss = 0
    model.train()
    # play batch_size many games
    # until the end
    for _ in range(iterations):
        X, y = next(dataloader)
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
    
    losses = np.array(losses)
    return np.mean(losses)


def validate(dataloader, model, loss_fn, iterations):
    model.eval()
    losses = []
    correct = []
    with torch.no_grad():
        for _ in range(iterations):
            X,y = next(dataloader)
            X = torch.from_numpy(X).float().to(DEVICE)
            label = torch.from_numpy(np.array([np.argmax(y[i]) for i in range(len(y))]))\
                .long().to(DEVICE)
            preds = model(X)
            losses.append( loss_fn(preds, label).item() )
            correct.append( (preds.argmax(1) == label).type(torch.float).sum().item() )

        losses = np.array(losses)
        correct = np.array(correct)
        return np.mean(losses), np.mean(correct)

# TODO: maybe merge training and validation dataloader into
# one single loader, whichs returns the corresponding generators 
dataloader = Dataloader(config.train_data_path, config.batch_size,config.features, config.load_full_datset)
val_dataloader = Dataloader(config.validation_data_path, config.batch_size, config.features, config.load_full_datset)

model = SimpleMLP(
    dataloader.input_size,
    dataloader.output_size,
    config.config["layers"],
    config.config["neurons"]
)

# trace the model to create a torch script instance
# you need to provide a example input. This
# can then be loaded with libtorch in C++
#script_model = torch.jit.trace(model, torch.rand(1,dataloader.input_size))

model.to(DEVICE)
loss_fn = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)

if config.use_early_stopping:
    earlyStopping = EarlyStopping(config.early_stopping_patience)
if config.use_lr_scheduler:
    lrscheduler = LRScheduler(optimizer, config.lr_scheduler_patience, config.lr_scheduler_min_lr)

RUN_DIR = os.path.join("runs", args.dir)

writer = SummaryWriter(RUN_DIR)
copy_config_to_output_dir(RUN_DIR, config.config)
train_loss, test_loss = [], []

if __name__ == "__main__":

    epochsUsed = 0
    for t in range(config.epochs):
        loss = train(dataloader, model, loss_fn, optimizer, config.iterations)
        vloss, correct = validate(val_dataloader, model, loss_fn, config.iterations)
        print(f"Epoch {t}\n-----------------")
        print(f"loss: {loss:>7f}")
        print(f"val loss: {vloss:>7f}")
        print(f"DEVICE {DEVICE}")
        writer.add_scalar('loss', loss, t)
        writer.add_scalar('val_loss', vloss, t)
        writer.add_scalar('correct', correct, t)
        train_loss.append(loss)
        test_loss.append(vloss)

        
        epochsUsed += 1
        if config.use_lr_scheduler:
            lrscheduler(vloss)
        if config.use_early_stopping and epochsUsed >= config.early_stopping_begin:
            earlyStopping(vloss)
            if earlyStopping.early_stop:
               break

    
    save_figure(epochsUsed, train_loss, test_loss, RUN_DIR)
    #save_model(model, script_model, RUN_DIR)
    save_loss(train_loss, test_loss, RUN_DIR)