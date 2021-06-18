from .dataconverter import DataConverter
from typing import Tuple

import os
import numpy as np
import pickle
import torch
from torch.utils.data import Dataset

class PokemonDataset(Dataset):
    def __init__(self, root_dir, features, transform=None):
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
        y = sample['p1']['chosenMove']
        if self.transform:
            X = self.transform(X)

        return X, y

    def _get_input_features(self, sample) -> np.ndarray:
        feature_list = []
        for player, feature in self.features:
            feature_list.append(sample[player][feature])
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
        def create_filename(string, file_extension):
            hash = hashlib.sha1()
            hash.update((str(time.time()) + string).encode('utf-8'))
            return str(hash.hexdigest()) + file_extension

        def _load_json(path):
            with open(path, 'r') as f:
                return json.load(f)

        os.makedirs(self.converted_path)

        dataconverter = DataConverter()

        raw_file_list = [ 
            os.path.join(self.root_dir, f) 
            for f in os.listdir(self.root_dir) 
            if os.path.isfile(os.path.join(self.root_dir, f))
        ]

        # iterate over each game and each turn
        # and save the turns in pickle format
        for file in raw_file_list:
            raw_data = _load_json(file)
            num_turns = len(raw_data['game'])
            for i in range(num_turns):
                path = os.path.join(self.converted_path, 
                    create_filename(str(i), self.converted_file_ext))
                self._save_pickle(path, 
                    dataconverter.convert_turn(raw_data['game'][i]))


    def _save_pickle(self, path, content):
        with open(path, 'wb') as f:
            pickle.dump(content, f)

    def _load_pickle(self, path):
        with open(path, 'rb') as f:
             return pickle.load(f)

# class Dataloader():
#     def __init__(self, data_path, batch_size, features, load_full_dataset=False):
#         self.data_path = data_path
#         self.batch_size = batch_size
#         self.data_converter = DataConverter()
#         self.data = []
#         self.turn = 0
#         self.features = [f.split("/") for f in features]
#         self.file_list = []
#         self.data_file_list = [
#             os.path.join(self.data_path, f) 
#             for f in os.listdir(self.data_path) 
#             if os.path.isfile(os.path.join(self.data_path,f))
#         ]
#         self.input_size = 0
#         self.output_size = 0
#         self.load_full_dataset = load_full_dataset
#         self.compute_input_output_size()

#         if self.load_full_dataset:
#             self.load_full_data()

#     def __iter__(self):
#         self.turn = 0
#         return self

#     def __next__(self):
#         X, y = self.get_batch()
#         self.turn += 1
#         return X, y

#     def load_pickle(self, path):
#         with open(path, 'rb') as f:
#             return pickle.load(f)

#     def load_samples(self, files):
#         samples = []
#         for file in files:
#             if self.load_full_dataset:
#                 samples.append( self.data[file] )
#             else:
#                 samples.append( self.load_pickle(file) )
#         return samples

#     def load_full_data(self):
#         print('loading full dataset')
#         self.data = {}
#         for file in self.data_file_list:
#             self.data.update({file : self.load_pickle(file) })

#     def _get_input_size(self, data):
#         size = 0
#         for player, feature in self.features:
#             if "turn" == feature:
#                 size += 1
#                 continue
#             size += len(data[player][feature])
#         return size

#     def _get_output_size(self, data):
#         return len(data['p1']['chosenMove'])

#     def compute_input_output_size(self):
#         data = self.load_pickle(self.data_file_list[0])
#         self.input_size = self._get_input_size(data)
#         self.output_size = self._get_output_size(data)

#     def get_batch(self):
#         X = np.ndarray((self.batch_size, self.input_size))
#         y = np.ndarray((self.batch_size, self.output_size))

#         i = 0
#         samples = self.load_samples(np.random.choice(self.data_file_list, self.batch_size, replace=False))
#         for sample in samples:
#             feature_list = []
#             for player, feature in self.features:
#                 if "turn" == feature:
#                     feature_list.append(np.array([self.turn]))
#                     continue
#                 feature_list.append(sample[player][feature])
#             X[i] = np.concatenate(tuple(feature_list))
#             y[i] = sample['p1']['chosenMove']
#             i += 1
#         return X, y
