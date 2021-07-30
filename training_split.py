import argparse
import os
import random
import shutil

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str)
    parser.add_argument("--percentage", type=float, default=0.9, help="the percentage the training set should have")
    parser.add_argument("--dest", type=str, default="")
    args = parser.parse_args()

    dest = args.dest
    if dest == "":
        dest = args.data + "_split"

    files = [f for f in os.listdir(args.data) if os.path.isfile(os.path.join(args.data, f))]
    number_training_samples = int(args.percentage * len(files))
    training_files = random.sample(files, number_training_samples)
    validation_files = [f for f in files if f not in training_files]

    train_dir = os.path.join(dest, 'train')
    val_dir = os.path.join(dest, 'val')
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)

    for f in training_files:
        source = os.path.join(args.data, f)
        target = os.path.join(train_dir, f)
        shutil.copy(source, target)

    for f in validation_files:
        source = os.path.join(args.data, f)
        target = os.path.join(val_dir, f)
        shutil.copy(source, target)
