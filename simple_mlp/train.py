import torch
import numpy as np
import os
from tensorboardX import SummaryWriter
import argparse

from dataloader.dataloader import Dataloader
from network import SimpleMLP
from utils import dump_parameters, save_model, save_figure, save_loss


parser = argparse.ArgumentParser()
parser.add_argument("--eval", type=str, default="")
parser.add_argument("--name", type=str)
parser.add_argument("--epochs", type=int, default=10000)
parser.add_argument("--neurons", type=int, default=20)
parser.add_argument("--lr", type=float, default=1e-3)
parser.add_argument("--layers", type=int, default=3)
parser.add_argument("--batch", type=int, default=32)
parser.add_argument("--normalized", type=str, default="no")
args = parser.parse_args()

normalized = True if args.normalized == "yes" else False


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
dataloader = Dataloader("datasets/no_type_only_damage", args.batch,
    # TODO: implement functionality to easily pick the features you
    # want in your batch
    ['p1/hp', 'p2/hp', 'p1/last_move', 'p2/last_move', 'turn']
)
dataloader.load_data()

val_dataloader = Dataloader("datasets/no_type_only_damage_1000_runs", args.batch,
    ['p1/hp', 'p2/hp', 'p1/last_move', 'p2/last_move', 'turn']
)
val_dataloader.load_data()

model = SimpleMLP(
    dataloader.get_input_size(),
    dataloader.get_output_size(),
    args.layers,
    args.neurons
)

# trace the model to create a torch script instance
# you need to provide a example input. This
# can then be loaded with libtorch in C++
script_model = torch.jit.trace(model, torch.rand(1,dataloader.get_input_size()))


model.to(DEVICE)
loss_fn = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

RUN_DIR = os.path.join("runs", args.name)

writer = SummaryWriter(RUN_DIR)
dump_parameters(args, RUN_DIR)
train_loss, test_loss = [], []

if args.eval == "":


    for t in range(args.epochs):
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

    
    save_figure(args.epochs, train_loss, test_loss, RUN_DIR)
    save_model(model, script_model, RUN_DIR)
    save_loss(train_loss, test_loss, RUN_DIR)
    

else:
    model.load_state_dict(torch.load("model.pth"))
    while True:
        tmp_input = input('some input:')
        values = tmp_input.split(',')
        x = torch.tensor([float(values[0]), float(values[1])], dtype=torch.float)
        pred = model(x)
        print(f"the prediction is {pred}")