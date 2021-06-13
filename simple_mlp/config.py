import os
import json

class SimpleMLPConfig():
    def __init__(self, path):
        self.config_path = path
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            print(f"The config file {self.config_path} does not exist")

        with open(self.config_path, 'r') as f:
            self._config = json.load(f)

    @property
    def config(self):
        return self._config

    @property
    def validation_data_path(self):
        return self._config["val_data_path"]

    @property
    def train_data_path(self):
        return self._config["train_data_path"]

    @property
    def batch_size(self):
        return self._config["batch_size"]

    @property
    def learning_rate(self):
        return self._config["learning_rate"]

    @property
    def epochs(self):
        return self._config["epochs"]

    @property
    def features(self):
        return self._config["features"]

    @property
    def iterations(self):
        return self._config['iterations']

    @property
    def early_stopping_patience(self):
        return self._config['earlyStoppingPatience']

    @property
    def lr_scheduler_patience(self):
        return self._config['lrSchedulerPatience']
