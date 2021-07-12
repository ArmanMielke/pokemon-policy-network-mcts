import argparse
import os
from typing import Tuple

import torch
import numpy as np
from torch.utils.data import DataLoader
from tqdm import tqdm

from dataloader.dataset import PokemonDataset
from network import PokemonAgent, SimpleMLP
from utils import *
from config import SimpleMLPConfig
from earlystopping import EarlyStopping
from lrscheduler import LRScheduler
from transforms import StatTransform, HealthTransform, FeatureTransform


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def transform_data(p1, p2, y):
    """
    transforms the label and input data
    into the correct format for the network.
    This is not the same as transforms for data augmentation.
    """
    # p1 = p1.flatten(start_dim=1)
    # p2 = p2.flatten(start_dim=1)
    # input = torch.cat((p1,p2), dim=1).float().to(DEVICE)
    p1 = p1.float().to(DEVICE)
    p2 = p2.float().to(DEVICE)

    # CrossEntropyLoss does not like a one-hot vector but
    # a single integer indicating which class it belongs to
    label = y.argmax(dim=1).long().to(DEVICE)

    return p1,p2, label

def train(data_loader, model, loss_fn, optimizer) -> float:
    """Returns the training loss"""
    losses = []
    accuracy = []
    model.train()
    
    progress_bar = tqdm(total=len(data_loader))

    for p1,p2, y in data_loader:
        p1,p2, label = transform_data(p1, p2, y)
        preds = model(p1,p2)
        loss = loss_fn(preds, label)
        losses.append(loss.item())
        accuracy.append((preds.argmax(1) == label).type(torch.float).mean().item())
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        progress_bar.set_description("Training ...")
        progress_bar.update(1)
    
    losses = np.array(losses)
    progress_bar.close()
    return np.mean(losses), np.mean(accuracy)


def validate(data_loader, model, loss_fn) -> Tuple[float, float]:
    """Returns validation loss and accuracy"""
    model.eval()
    losses = []
    accuracy = []
    progress_bar = tqdm(total=len(data_loader))
    with torch.no_grad():
        for p1,p2, y in data_loader:
            p1,p2, label = transform_data(p1, p2, y)
            preds = model(p1,p2)
            losses.append(loss_fn(preds, label).item())
            accuracy.append((preds.argmax(1) == label).type(torch.float).mean().item())
            progress_bar.set_description("Validating ...")
            progress_bar.update(1)


        losses = np.array(losses)
        accuracy = np.array(accuracy)
        progress_bar.close()
        return np.mean(losses), np.mean(accuracy)

def test(data_loader, current_model, best_model) -> float:
    """ 
    Evaluates the model on the test set
    """
    current_model.eval()
    best_model.eval()
    accuracy_current, accuracy_best = [], []
    progress_bar = tqdm(total=len(data_loader))
    with torch.no_grad():
        for p1, p2, y in data_loader:
            p1,p2, label = transform_data(p1, p2, y)
            current_preds = current_model(p1,p2)
            best_preds = best_model(p1,p2)

            accuracy_current.append((current_preds.argmax(1) == label).type(torch.float).mean().item())
            accuracy_best.append((best_preds.argmax(1) == label).type(torch.float).mean().item())
            progress_bar.set_description("Testing ...")
            progress_bar.update(1)
    progress_bar.close()
    return np.mean( np.array(accuracy_current) ), np.mean( np.array(accuracy_best) )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=str, default=generate_dir_name(),
                        help="the directory to store the data, e.g. model, plots etc.")
    parser.add_argument("--config", type=str)
    args = parser.parse_args()

    config = SimpleMLPConfig(args.config)

    # initialize the training and validation dataset
    transforms = [FeatureTransform(["p1","p2"], "stats", 50), FeatureTransform(["p1","p2"],"hp", 400)]
    train_dataset = PokemonDataset(config.train_data_path, config.features, transforms)
    val_dataset = PokemonDataset(config.validation_data_path, config.features, [])
    train_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=config.batch_size, shuffle=True)

    p1,p2,y = train_dataset[0]

    num_pokemon = p1.shape[0]
    pkmn_input_size = p1.shape[1]
    pkmn_output_size = y.shape[0]
    p2_size = len(p2.flatten())
    agent_input_size = num_pokemon * pkmn_output_size + p2_size
    agent_output_size = y.shape[0]


    # model = PokemonAgent(
    #     (pkmn_input_size, agent_input_size),
    #     (pkmn_output_size, agent_output_size),
    #     (config.config['pokemon_encoder']['layers'], config.config['pokemon_agent']['layers']),
    #     (config.config['pokemon_encoder']['neurons'], config.config['pokemon_agent']['neurons'])
    # )

    model = SimpleMLP(
        pkmn_input_size*num_pokemon + p2_size,
        agent_output_size,
        config.config['pokemon_encoder']['layers'],
        config.config['pokemon_encoder']['neurons']
    )

    # trace the model to create a torch script instance
    # you need to provide a example input. This
    # can then be loaded with libtorch in C++
    # script_model = torch.jit.trace(model, torch.rand(1, input_size))

    model.to(DEVICE)
    loss_fn = torch.nn.CrossEntropyLoss()

    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)

    if config.use_early_stopping:
        early_stopping = EarlyStopping(config.early_stopping_patience)
    if config.use_lr_scheduler:
        lr_scheduler = LRScheduler(optimizer, config.lr_scheduler_patience, config.lr_scheduler_min_lr)

    run_dir = os.path.join("runs", args.dir)
    logger = setup_logger(run_dir)

    copy_config_to_output_dir(run_dir, config.config)
    train_losses, val_losses, val_accuracies = [], [], []
    train_accuracies = []

    epochs_used = 0
    min_val_loss = float('inf')
    for t in range(config.epochs):

        train_loss, train_accuracy = train(train_loader, model, loss_fn, optimizer)
        val_loss, val_accuracy = validate(val_loader, model, loss_fn)

        epochs_used += 1
        if config.use_lr_scheduler:
            lr_scheduler(val_loss)
        if config.use_early_stopping and epochs_used >= config.early_stopping_begin:
            early_stopping(val_loss)
            if early_stopping.early_stop:
                break

        log_stats(t, (train_loss, train_accuracy), (val_loss, val_accuracy))

        # some book keeping
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        val_accuracies.append(val_accuracy)
        train_accuracies.append(train_accuracy)

        if val_loss < min_val_loss:
            save_model(model, os.path.join(run_dir, "best_model.pth"))
            min_val_loss = val_loss

    # evaluate on the test set if one is given
    if config.test_data_path != "":
        test_dataset = PokemonDataset(config.test_data_path, config.features, [])
        test_loader = DataLoader(test_dataset, batch_size=config.batch_size, shuffle=True)

        best_model = PokemonAgent(
            (pkmn_input_size, agent_input_size),
            (pkmn_output_size, agent_output_size),
            (config.config['pokemon_encoder']['layers'], config.config['pokemon_agent']['layers']),
            (config.config['pokemon_encoder']['neurons'], config.config['pokemon_agent']['neurons'])
        ).to(DEVICE)
        best_model.load_state_dict(torch.load(os.path.join(run_dir, "best_model.pth")))

        current_acc, best_acc = test(test_loader, model, best_model)
        logger.info(f"Accuracy on test set: current/last model {current_acc:>7f}, best model {best_acc:>7f}")

    # some final logging
    save_figure(epochs_used, train_losses, val_losses, val_accuracies, run_dir)
    save_model(model, os.path.join(run_dir, "last_model.pth"))
    save_loss(train_losses, val_losses, val_accuracies, run_dir)


if __name__ == "__main__":
    main()
