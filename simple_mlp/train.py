import argparse
import hashlib
import os
import time
from typing import Tuple

import torch
import numpy as np
from tensorboardX import SummaryWriter

from dataloader.dataloader import Dataloader
from network import SimpleMLP
from utils import copy_config_to_output_dir, save_model, save_figure, save_loss
from config import SimpleMLPConfig
from earlystopping import EarlyStopping
from lrscheduler import LRScheduler


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def generate_dir_name() -> str:
    """Create a unique hash for the filename"""
    hash = hashlib.sha1()
    hash.update(str(time.time()).encode('utf-8'))
    return str(hash.hexdigest())


def train(data_loader, model, loss_fn, optimizer, iterations: int) -> float:
    """Returns the training loss"""
    losses = []
    model.train()
    # play batch_size many games
    # until the end
    for _ in range(iterations):
        X, y = next(data_loader)
        X = torch.from_numpy(X).float().to(DEVICE)
        # CrossEntropyLoss does not like a one-hot vector but
        # a single integer indicating which class it belongs to
        label = torch.from_numpy(np.array([np.argmax(y[i]) for i in range(len(y))])) \
            .long().to(DEVICE)
        preds = model(X)
        loss = loss_fn(preds, label)
        losses.append(loss.item())
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    
    losses = np.array(losses)
    return np.mean(losses)


def validate(data_loader, model, loss_fn, iterations: int) -> Tuple[float, float]:
    """Returns validation loss and accuracy"""
    model.eval()
    losses = []
    accuracy = []
    with torch.no_grad():
        for _ in range(iterations):
            X, y = next(data_loader)
            X = torch.from_numpy(X).float().to(DEVICE)
            label = torch.from_numpy(np.array([np.argmax(y[i]) for i in range(len(y))])) \
                .long().to(DEVICE)
            preds = model(X)
            losses.append(loss_fn(preds, label).item())
            accuracy.append((preds.argmax(1) == label).type(torch.float).mean().item())

        losses = np.array(losses)
        accuracy = np.array(accuracy)
        return np.mean(losses), np.mean(accuracy)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str, default=generate_dir_name(),
                        help="the directory to store the data, e.g. model, plots etc.")
    parser.add_argument("--config", type=str)
    args = parser.parse_args()

    config = SimpleMLPConfig(args.config)

    # TODO: maybe merge training and validation data loader into one, which returns the corresponding generators
    train_loader = Dataloader(config.train_data_path, config.batch_size, config.features)
    val_loader = Dataloader(config.validation_data_path, config.batch_size, config.features)

    model = SimpleMLP(
        train_loader.input_size,
        train_loader.output_size,
        config.config["layers"],
        config.config["neurons"],
    )

    # trace the model to create a torch script instance
    # you need to provide a example input. This
    # can then be loaded with libtorch in C++
    script_model = torch.jit.trace(model, torch.rand(1, train_loader.input_size))

    model.to(DEVICE)
    loss_fn = torch.nn.CrossEntropyLoss()
    # TODO un-hard code weight decay
    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate, weight_decay=1e-5)

    if config.use_early_stopping:
        early_stopping = EarlyStopping(config.early_stopping_patience)
    if config.use_lr_scheduler:
        lr_scheduler = LRScheduler(optimizer, config.lr_scheduler_patience, config.lr_scheduler_min_lr)

    run_dir = os.path.join("runs", args.dir)

    writer = SummaryWriter(run_dir)
    copy_config_to_output_dir(run_dir, config.config)
    train_losses, val_losses = [], []

    epochs_used = 0
    for t in range(config.epochs):
        train_loss = train(train_loader, model, loss_fn, optimizer, config.iterations)
        val_loss, val_accuracy = validate(val_loader, model, loss_fn, config.iterations)
        print(f"Epoch {t}\n-----------------")
        print(f"loss: {train_loss:>7f}")
        print(f"val loss: {val_loss:>7f} (accuracy: {val_accuracy:>7f})")
        print(f"DEVICE {DEVICE}")
        writer.add_scalar('loss', train_loss, t)
        writer.add_scalar('val_loss', val_loss, t)
        writer.add_scalar('val_accuracy', val_accuracy, t)
        train_losses.append(train_loss)
        val_losses.append(val_loss)

        epochs_used += 1
        if config.use_lr_scheduler:
            lr_scheduler(val_loss)
        if config.use_early_stopping and epochs_used >= config.early_stopping_begin:
            early_stopping(val_loss)
            if early_stopping.early_stop:
                break

    save_figure(epochs_used, train_losses, val_losses, run_dir)
    save_model(model, script_model, run_dir)
    save_loss(train_losses, val_losses, run_dir)


if __name__ == "__main__":
    main()
