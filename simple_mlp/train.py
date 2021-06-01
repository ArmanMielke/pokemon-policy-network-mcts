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

from captum.attr import IntegratedGradients

def generate_dir_name():    
    """Create a unique hash for the filename"""
    hash = hashlib.sha1()
    hash.update(str(time.time()).encode('utf-8'))
    return str(hash.hexdigest())

parser = argparse.ArgumentParser()
parser.add_argument("--eval", type=str, default="")
parser.add_argument("--dir", type=str, default=generate_dir_name(), 
    help="the directory to store the data, e.g. model, plots etc.")
parser.add_argument("--config", type=str)
args = parser.parse_args()

config = SimpleMLPConfig(args.config)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def train(dataloader, model, loss_fn, optimizer):
    losses = []

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
                print(losses)
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

if args.eval == "":


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
    

else:
    model.load_state_dict(torch.load(os.path.join(args.eval,"model.pth")))
    model.eval()
    np.random.seed(123)
    torch.manual_seed(123)
    input, y, _ = next(val_dataloader)
    label = torch.from_numpy(np.array([np.argmax(y[i]) for i in range(len(y))])) \
                .long().to(DEVICE)
    ig = IntegratedGradients(model)
    attribution_t0 = ig.attribute(torch.from_numpy(input).float().to(DEVICE), 
        target=0)
    attribution_t1 = ig.attribute(torch.from_numpy(input).float().to(DEVICE), 
        target=1)
    attribution_t2 = ig.attribute(torch.from_numpy(input).float().to(DEVICE), 
        target=2)
    attribution_t3 = ig.attribute(torch.from_numpy(input).float().to(DEVICE), 
        target=3)
    print({
        "t0" : [attribution_t0.mean(axis=0), attribution_t0.std(axis=0)],
        "t1" : [attribution_t1.mean(axis=0), attribution_t1.std(axis=0)],
        "t2" : [attribution_t2.mean(axis=0), attribution_t2.std(axis=0)],
        "t3" : [attribution_t3.mean(axis=0), attribution_t3.std(axis=0)]
    })
    # while True:
    #     tmp_input = input('some input:')
    #     values = tmp_input.split(',')
    #     x = torch.tensor([float(values[0]), float(values[1])], dtype=torch.float)
    #     pred = model(x)
    #     print(f"the prediction is {pred}")