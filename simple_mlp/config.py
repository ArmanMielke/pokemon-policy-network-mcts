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

    def __getitem__(self, idx):
        return self._config[idx]

    @property
    def keys(self):
        return self._config.keys()

    def save_to(self, path):
        with open(os.path.join(path, 'config.json'), 'w') as f:
            f.write(json.dumps(self._config, indent=4, separators=(',', ': ')))
