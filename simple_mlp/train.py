import torch
from torch import nn
import numpy as np
import random
from tensorboardX import SummaryWriter

class SimpleMLP(nn.Module):
    def __init__(self):
        super(SimpleMLP, self).__init__()
        self.mlp_stack = nn.Sequential(
            nn.Linear(2, 5),
            nn.ReLU(),
            nn.Linear(5, 5),
            nn.ReLU(),
            nn.Linear(5, 5),
            nn.ReLU(),
            nn.Linear(5, 2),
            nn.Softmax()
        )

    def forward(self, x):
        return self.mlp_stack(x)

class DataGenerator():
    def __init__(self):
        pass

    def generate(self, min, max):
        one, two = float(random.randint(min, max)), float(random.randint(min, max))
        total = one + two
        one_n, two_n = float(one / total), float(two / total)
        return torch.tensor([one, two], dtype=torch.float32)

    def batch(self, batch_size, min, max):
        batch = torch.zeros((batch_size, 2), dtype=torch.float)
        labels = torch.zeros(batch_size, dtype=torch.long)
        for i in range(batch_size):
            batch[i] = self.generate(min, max)
            labels[i] = np.argmax(batch[i])
        return batch, labels


def train(datagen, model, loss_fn, optimizer, batch_size):
    #data = datagen.generate()
    batch, labels = datagen.batch(batch_size, 10, 100)
    preds = torch.zeros((batch_size, 2))
    for i in range(batch_size):
        preds[i] = model(batch[i])
    loss = loss_fn(preds, labels)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    print(f"loss: {loss.item():>7f}")
    return loss.item()

def test(datagen, model, loss_fn, val_size):
    model.eval()
    test_loss, correct = 0, 0
    with torch.no_grad():
        preds = torch.zeros((val_size, 2), dtype=torch.float)
        batch, labels = datagen.batch(val_size, 110, 200)
        for i in range(val_size):
            preds[i] = model(batch[i])
        test_loss = loss_fn(preds, labels).item()
        correct += (preds.argmax(1) == labels).type(torch.float).sum().item()
    # test_loss /= val_size
    # correct /= val_size
    print(f"val loss: {test_loss:>7f}")

    return test_loss, correct

model = SimpleMLP()
datagen = DataGenerator()
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=1e-3)

writer = SummaryWriter()



for t in range(10000000):
    print(f"Epoch {t}\n-----------------")
    loss = train(datagen, model, loss_fn, optimizer, 32)
    test_loss, correct = test(datagen, model, loss_fn, 100)
    writer.add_scalar('loss', loss, t)
    writer.add_scalar('test_loss', test_loss, t)
    writer.add_scalar('correct', 100*correct, t)

