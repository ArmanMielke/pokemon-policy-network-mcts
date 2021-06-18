import argparse
import hashlib
import os
import time
from typing import Tuple

import torch
import numpy as np
from tensorboardX import SummaryWriter
from torch.utils.data import DataLoader
from tqdm import tqdm

from dataloader.dataset import PokemonDataset
from network import SimpleMLP
from utils import copy_config_to_output_dir, save_model, save_figure, save_loss
from config import SimpleMLPConfig
from earlystopping import EarlyStopping
from lrscheduler import LRScheduler
from transforms import StatTransform


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def generate_dir_name() -> str:
    """Create a unique hash for the filename"""
    hash = hashlib.sha1()
    hash.update(str(time.time()).encode('utf-8'))
    return str(hash.hexdigest())


def train(data_loader, model, loss_fn, optimizer) -> float:
    """Returns the training loss"""
    losses = []
    model.train()
    
    progress_bar = tqdm(total=len(data_loader))

    for X, y in data_loader:
        X = X.float().to(DEVICE)
        # CrossEntropyLoss does not like a one-hot vector but
        # a single integer indicating which class it belongs to
        label = y.argmax(dim=1).long().to(DEVICE)
        preds = model(X)
        loss = loss_fn(preds, label)
        losses.append(loss.item())
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        progress_bar.set_description("Training ...")
        progress_bar.update(1)
    
    losses = np.array(losses)
    progress_bar.close()
    return np.mean(losses)


def validate(data_loader, model, loss_fn) -> Tuple[float, float]:
    """Returns validation loss and accuracy"""
    model.eval()
    losses = []
    accuracy = []
    progress_bar = tqdm(total=len(data_loader))
    with torch.no_grad():
        for X, y in data_loader:
            X = X.float().to(DEVICE)
            label = y.argmax(dim=1).long().to(DEVICE)
            preds = model(X)
            losses.append(loss_fn(preds, label).item())
            accuracy.append((preds.argmax(1) == label).type(torch.float).mean().item())
            progress_bar.set_description("Validating ...")
            progress_bar.update(1)


        losses = np.array(losses)
        accuracy = np.array(accuracy)
        progress_bar.close()
        return np.mean(losses), np.mean(accuracy)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str, default=generate_dir_name(),
                        help="the directory to store the data, e.g. model, plots etc.")
    parser.add_argument("--config", type=str)
    args = parser.parse_args()

    config = SimpleMLPConfig(args.config)

    train_dataset = PokemonDataset(config.train_data_path, config.features, StatTransform())
    val_dataset = PokemonDataset(config.validation_data_path, config.features)
    train_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=config.batch_size, shuffle=True)

    X,y = train_dataset[0]
    input_size, output_size = len(X), len(y)

    model = SimpleMLP(
        input_size,
        output_size,
        config.config["layers"],
        config.config["neurons"],
    )

    # trace the model to create a torch script instance
    # you need to provide a example input. This
    # can then be loaded with libtorch in C++
    script_model = torch.jit.trace(model, torch.rand(1, input_size))

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
        train_loss = train(train_loader, model, loss_fn, optimizer)
        val_loss, val_accuracy = validate(val_loader, model, loss_fn)
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
