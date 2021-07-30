import re
import matplotlib.pyplot as plt
import numpy as np


LOG_FILE = ""
OUT_FILE = ""


with open(LOG_FILE, 'r') as f:
    lines = f.read().splitlines()

train_loss = []
train_acc = []
val_loss = []
val_acc = []

for i in range(0, len(lines)):
    result = re.search("Train loss ([\d\.]+), accuracy ([\d\.]+)", lines[i])
    if result:
        train_loss.append(float(result.group(1)))
        train_acc.append(float(result.group(2)))
        continue

    result = re.search("Val loss ([\d\.]+), accuracy ([\d\.]+)", lines[i])
    if result:
        val_loss.append(float(result.group(1)))
        val_acc.append(float(result.group(2)))
        continue

epochs = len(val_loss)

fig = plt.figure(figsize=(8, 8))
axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])
axes.plot(np.arange(0, epochs), train_loss, label="train loss")
axes.plot(np.arange(0, epochs), val_loss, label="validation loss")
# axes.plot(np.arange(0, epochs), val_acc, label="validation accuracy")
fig.legend()
axes.set_xlabel("epochs")
axes.set_ylabel("loss")
fig.savefig(OUT_FILE)
plt.close()
