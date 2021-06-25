from .dataconverter import DataConverter
from typing import Tuple

import os
import numpy as np
import pickle
import torch
from torch.utils.data import Dataset

class PokemonDataset(Dataset):
    def __init__(self, root_dir, features, transform=[]):
        self.root_dir = root_dir
        self.transform = transform
        self.features = [f.split("/") for f in features]
        self.converted_path = os.path.join(self.root_dir, 'converted')
        self.converted_file_ext = '.pkl'
        self._convert_data()
        self.file_list = [
            f for f in os.listdir(self.converted_path)
            if os.path.isfile(os.path.join(self.converted_path, f))
        ]

    def __len__(self) -> int:
        return len(self.file_list)

    def __getitem__(self, index) -> Tuple[np.ndarray, np.ndarray]:
        if torch.is_tensor(index):
            index = index.tolist()

        path = os.path.join(self.converted_path, self.file_list[index])
        sample = self._load_pickle(path)
        X = self._get_input_features(sample)
        y = sample['p1']['chosen_move']

        return X, y

    def get_stat_start_position(self) -> int:
        pass

    def _get_input_features(self, sample) -> np.ndarray:
        feature_list = []
        for player, feature in self.features:
            data = sample[player][feature]
            for transform in self.transform:
                data = transform(data, feature)
            feature_list.append(data)
            
        return np.concatenate(tuple(feature_list))

    def _convert_data(self):
        """
        Convert the data into a vector representation
        and save it, to reduce overhead at next startup
        """

        # check if data is already converted
        # then we save us the trouble
        if (os.path.exists(self.converted_path) 
            and len(os.listdir(self.converted_path)) != 0):
            return

        import hashlib
        import time
        import json
        from tqdm import tqdm

        def create_filename(string, file_extension):
            hash = hashlib.sha1()
            hash.update((str(time.time()) + string).encode('utf-8'))
            return str(hash.hexdigest()) + file_extension

        def _load_json(path):
            with open(path, 'r') as f:
                try:
                    return json.load(f)
                except Exception:
                    print(f"could not decode file {path}")
                    return {}

        def load_data(file):
            file_extension = file.split('.')[-1]
            if file_extension == "json":
                return _load_json(file)
            elif file_extension == "pkl":
                return self._load_pickle(file)
            else:
                print(f"The file extension {file_extension} is not supported")

        os.makedirs(self.converted_path)

        dataconverter = DataConverter()

        raw_file_list = [ 
            os.path.join(self.root_dir, f) 
            for f in os.listdir(self.root_dir) 
            if os.path.isfile(os.path.join(self.root_dir, f))
        ]

        # iterate over each game and each turn
        # and save the turns in pickle format
        progress_bar = tqdm(total=len(raw_file_list))
        for file in raw_file_list:

            raw_data = load_data(file)#_load_json(file)
            # sometimes the files are empty
            # we just ignore them
            if not raw_data:
                continue
            num_turns = len(raw_data['game'])
            for i in range(num_turns):
                path = os.path.join(self.converted_path, 
                    create_filename(str(i), self.converted_file_ext))
                self._save_pickle(path, 
                    dataconverter.convert_turn(raw_data['game'][i]))
            progress_bar.set_description("converting ...")
            progress_bar.update(1)
        progress_bar.close()


    def _save_pickle(self, path, content):
        with open(path, 'wb') as f:
            pickle.dump(content, f)

    def _load_pickle(self, path):
        with open(path, 'rb') as f:
             return pickle.load(f)
