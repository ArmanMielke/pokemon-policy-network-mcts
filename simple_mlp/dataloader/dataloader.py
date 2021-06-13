from .dataconverter import DataConverter

import json
import os

import numpy as np
import random

class Dataloader():
    def __init__(self, data_path, batch_size, features):
        self.data_path = data_path
        self.batch_size = batch_size
        self.data_converter = DataConverter()
        self.data = []
        self.turn = 0
        self.max_turns = 0
        self.features = [f.split("/") for f in features]
        self.selected_files = []
        self.current_batch = None
        self.current_label = None
        self.input_size = 0
        self.output_size = 0

    def __iter__(self):
        self.turn = 0
        return self

    def __next__(self):
        X, y = self.get_batch()
        self.turn += 1
        return X, y

    def load_json(self, path):
        with open(path, 'r') as f:
            return json.load(f)

    def load_data(self):
        # ignore all subdirectories
        # and only consider files in the self.data_path directory
        file_list = [
            os.path.join(self.data_path, f) 
            for f in os.listdir(self.data_path) 
            if os.path.isfile(os.path.join(self.data_path,f))
        ]
        if len(file_list) < self.batch_size:
            print(f"The number of files ({len(file_list)}) is smaller than \
                the batch size ({self.batch_size})")

        # randomly select self.batch_size many files
        # for the current run of the game
        indices = np.random.choice(len(file_list), self.batch_size)
        data = []
        for i in range(self.batch_size):
            file_path = file_list[indices[i]]
            raw_data = self.load_json(file_path)
            self.selected_files.append( file_path )
            # convert the data from json to a vector representation
            num_turns = len(raw_data['game'])
            sampled_turn = random.randint(0,num_turns-1)
            data.append( self.data_converter.convert_turn(raw_data['game'][sampled_turn]) )

        self.data = np.array(data)

    def reset(self):
        self.data = []
        self.selected_files = []
        self.turn = 0 
        self.max_turns = 0
        
    def augment_data(self):
        max_len = np.max([len(x) for x in self.data])
        self.max_turns = max_len
        for i in range(len(self.data)):
            if len(self.data[i]) < max_len:
                last_entry = self.data[i][-1]
                diff_to_max = max_len - len(self.data[i])
                for y in range(diff_to_max):
                    self.data[i].append(last_entry)

    def get_input_size(self):
        if self.input_size == 0:
            self.load_data()
            size = 0
            for _, feature in self.features:
                if "turn" == feature:
                    size += 1
                    continue
                size += self.data_converter.feature_size(feature)
            self.input_size = size
        return self.input_size

    def get_output_size(self):
        if self.output_size == 0:
            self.load_data()
            # TODO change this because get_batch also needs
            # the input size
            _, y = self.get_batch()
            self.output_size = y.shape[1]
        return self.output_size

    def shape(self):
        return self.get_input_size(), self.get_output_size()

    def get_batch(self):
        X = np.ndarray((self.batch_size, self.get_input_size()))
        y = np.ndarray((self.batch_size, self.data_converter.move_size))

        self.load_data()

        i = 0
        for sample in self.data:
            feature_list = []
            for player, feature in self.features:
                if "turn" == feature:
                    feature_list.append( np.array([self.turn]) )
                    continue
                feature_list.append( sample[player][feature])
            X[i] = np.concatenate(tuple(feature_list))
            y[i] = sample['p1']['chosenMove']
            i += 1
        self.current_batch, self.current_label = X, y
        return X, y

    def trace_back(self, prediction):
        with open('tmp/trace.txt', 'a') as f:
            f.write("-----------------------\n")
            f.write(f"turn: {self.turn}\n")
            for file in self.selected_files:
                f.write(f"{file}\n")

            f.write("Prediction          |      Ground Truth\n")
            for i in range(len(self.current_label)):
                f.write(f"{prediction[i]}          |      {self.current_label[i]}\n")
