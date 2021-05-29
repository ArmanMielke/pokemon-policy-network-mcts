import torch
from torch import nn
import torch.nn.functional as F
import numpy as np
import random
from tensorboardX import SummaryWriter
import argparse
import pickle
import matplotlib.pyplot as plt
from dataloader.dataloader import Dataloader


parser = argparse.ArgumentParser()
parser.add_argument("--eval", type=str, default="")
parser.add_argument("--name", type=str)
parser.add_argument("--epochs", type=int, default=10000)
parser.add_argument("--neurons", type=int, default=20)
parser.add_argument("--lr", type=float, default=1e-3)
parser.add_argument("--min", type=int, default=1)
parser.add_argument("--max", type=int, default=50)
parser.add_argument("--layers", type=int, default=3)
parser.add_argument("--batch", type=int, default=32)
parser.add_argument("--normalized", type=str, default="no")
args = parser.parse_args()

normalized = True if args.normalized == "yes" else False


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

class SimpleMLP(nn.Module):
    def __init__(self):
        super(SimpleMLP, self).__init__()

        self.mlp_stack = nn.ModuleList([nn.Linear(2, args.neurons)])
        self.mlp_stack.extend([nn.Linear(args.neurons, args.neurons) for i in range(args.layers-2)])
        self.mlp_stack.append(nn.Linear(args.neurons, 2))

    def forward(self, x):
        result = x
        for i in range(args.layers-1):
            result = F.relu(self.mlp_stack[i](result))
        # We don't need a activation here because
        # Softmax is included in CrossEntropyLoss
        # (needs to be changed if we switch the loss function)
        return self.mlp_stack[-1](result) 


class DataGenerator():
    def __init__(self):
        pass

    def generate(self, min, max, normalized):
        one, two = float(random.randint(min, max)), float(random.randint(min, max))
        total = one + two
        return torch.tensor([one, two], dtype=torch.float)

    def generate_choice(self, min, max, normalized):
        range = max - min
        diff = range / 5
        values = [min, min+diff, min+2*diff, min+3*diff, min+4*diff]
        return torch.tensor([np.random.choice(values), np.random.choice(values)], dtype=torch.float)

    def generate_without_doubles(self, min, max, normalized):
        one, two = float(random.randint(min, max)), float(random.randint(min, max))
        while one == two:
            two = float(random.randint(min, max))
        if normalized:
            total = one + two
            one, two = float(one/total), float(two/total)
        return torch.tensor([one, two], dtype=torch.float)
        

    def batch(self, batch_size, min, max):
        batch = torch.zeros((batch_size, 2), dtype=torch.float)
        labels = torch.zeros(batch_size, dtype=torch.long)
        for i in range(batch_size):
            batch[i] = self.generate(min, max, normalized)
            labels[i] = np.argmax(batch[i])
        return batch.to(DEVICE), labels.to(DEVICE)


def train(datagen, model, loss_fn, optimizer, batch_size):
    batch, labels = datagen.batch(batch_size, args.min, args.max)
    preds = torch.zeros((batch_size, 2)).to(DEVICE)
    preds = model(batch)
    loss = loss_fn(preds, labels)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    return loss.item()

def test(datagen, model, loss_fn, val_size):
    model.eval()
    test_loss, correct = 0, 0
    with torch.no_grad():
        preds = torch.zeros((val_size, 2), dtype=torch.float).to(DEVICE)
        batch, labels = datagen.batch(val_size, args.min + args.max, args.max * 2)
        preds = model(batch)
        test_loss = loss_fn(preds, labels).item()
        correct += (preds.argmax(1) == labels).type(torch.float).sum().item()

    return test_loss, correct

def dump_parameters():
    with open(f"runs/{args.name}/params.txt", "w") as f:
        f.write(f"Learning rate {args.lr}\n")
        f.write(f"Num Neurons {args.neurons}\n")
        f.write(f"Epochs {args.epochs}\n")
        f.write(f"Min Range {args.min}\n")
        f.write(f"Max Range {args.max}\n")
        f.write(f"Batch size {args.batch}\n")

def save_figure(train_loss, val_loss):
    fig = plt.figure()
    axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    axes.plot(np.arange(0, args.epochs), train_loss, label='train loss')
    axes.plot(np.arange(0, args.epochs), val_loss, label='validation loss')
    fig.legend()
    axes.set_xlabel("epochs")
    axes.set_ylabel("loss")
    fig.savefig(f"runs/{args.name}/graph.png")
    plt.close()


model = SimpleMLP()
# trace the model to create a torch script instance
# you need to provide a example input
script_model = torch.jit.trace(model, torch.rand(1,2))
model.to(DEVICE)
datagen = DataGenerator()
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

writer = SummaryWriter(f"runs/{args.name}")
dump_parameters()
train_loss, test_loss = [], []

if args.eval == "":

    dataloader = Dataloader("datasets/no_type_only_damage", 10)
    dataloader.load_data()
    for X, y, end in dataloader:
        #X, y = dataloader.get_batch()
        print(f"X: {X}\n\n")
        print(f"y: {y}")
        print(f"end: {end}\n")
        if end:
            dataloader.reset()
            dataloader.load_data()

    # for t in range(args.epochs):
    #     loss = train(datagen, model, loss_fn, optimizer, args.batch)
    #     tloss, correct = test(datagen, model, loss_fn, 100)
    #     print(f"Epoch {t}\n-----------------")
    #     print(f"loss: {loss:>7f}")
    #     print(f"val loss: {tloss:>7f}")
    #     print(f"DEVICE {DEVICE}")
    #     writer.add_scalar('loss', loss, t)
    #     writer.add_scalar('test_loss', tloss, t)
    #     writer.add_scalar('correct', 100*correct, t)
    #     train_loss.append(loss)
    #     test_loss.append(tloss)

    # torch.save(model.state_dict(), f"runs/{args.name}/model.pth")
    # script_model.save(f"runs/{args.name}/model_script.pt")
    # print(len(train_loss))
    # save_figure(train_loss, test_loss)
    # with open(f"runs/{args.name}/data.pkl", "wb") as f:
    #     pickle.dump({"train_loss": train_loss, "test_loss": test_loss}, f)
    # print(f"saved model to runs/{args.name}/model.pth")

else:
    model.load_state_dict(torch.load("model.pth"))
    while True:
        tmp_input = input('some input:')
        values = tmp_input.split(',')
        x = torch.tensor([float(values[0]), float(values[1])], dtype=torch.float)
        pred = model(x)
        print(f"the prediction is {pred}")