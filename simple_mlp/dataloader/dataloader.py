from .dataconverter import DataConverter

import os
import numpy as np
import pickle

class Dataloader():
    def __init__(self, data_path, batch_size, features, load_full_dataset=False):
        self.data_path = data_path
        self.batch_size = batch_size
        self.data_converter = DataConverter()
        self.data = []
        self.turn = 0
        self.features = [f.split("/") for f in features]
        self.file_list = []
        self.data_file_list = [
            os.path.join(self.data_path, f) 
            for f in os.listdir(self.data_path) 
            if os.path.isfile(os.path.join(self.data_path,f))
        ]
        self.input_size = 0
        self.output_size = 0
        self.load_full_dataset = load_full_dataset
        self.compute_input_output_size()

        if self.load_full_dataset:
            self.load_full_data()

    def __iter__(self):
        self.turn = 0
        return self

    def __next__(self):
        X, y = self.get_batch()
        self.turn += 1
        return X, y

    def load_pickle(self, path):
        with open(path, 'rb') as f:
            return pickle.load(f)

    def load_samples(self, files):
        samples = []
        for file in files:
            if self.load_full_dataset:
                samples.append( self.data[file] )
            else:
                samples.append( self.load_pickle(file) )
        return samples

    def load_full_data(self):
        print('loading full dataset')
        self.data = {}
        for file in self.data_file_list:
            self.data.update({file : self.load_pickle(file) })

    def _get_input_size(self, data):
        size = 0
        for player, feature in self.features:
            if "turn" == feature:
                size += 1
                continue
            size += len(data[player][feature])
        return size

    def _get_output_size(self, data):
        return len(data['p1']['chosenMove'])

    def compute_input_output_size(self):
        data = self.load_pickle(self.data_file_list[0])
        self.input_size = self._get_input_size(data)
        self.output_size = self._get_output_size(data)

    def get_batch(self):
        X = np.ndarray((self.batch_size, self.input_size))
        y = np.ndarray((self.batch_size, self.output_size))

        i = 0
        samples = self.load_samples(np.random.choice(self.data_file_list, self.batch_size, replace=False))
        for sample in samples:
            feature_list = []
            for player, feature in self.features:
                if "turn" == feature:
                    feature_list.append( np.array([self.turn]) )
                    continue
                feature_list.append( sample[player][feature])
            X[i] = np.concatenate(tuple(feature_list))
            y[i] = sample['p1']['chosenMove']
            i += 1
        return X, y