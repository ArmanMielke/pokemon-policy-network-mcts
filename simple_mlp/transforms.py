import numpy as np

class FeatureTransform():
    def __init__(self, player, feature, value):
        self.feature_of_interest = feature
        self.player_of_interest = player
        self.value = value

    @staticmethod
    def from_config(config):
        f = config #config['FeatureTransform']
        k = f.keys() 
        players = []
        if 'players' not in k:
            players = ['p1', 'p2']
        else:
            players = f['players']
            
        feature = ""
        if 'feature' not in k:
            raise ValueError("Transform feature not specified")
        else:
            feature = f['feature']

        value = None
        if 'value' not in k:
            raise ValueError("Transform value not specified")
        else:
            value = f['value']

        return FeatureTransform(players, feature, value)


    def __call__(self, sample, player): 
        if player in self.player_of_interest and self.feature_of_interest in sample.dtype.names:
            modifier = np.random.choice(np.arange(start=-self.value, stop=self.value, step=1), sample[self.feature_of_interest].shape)
            sample[self.feature_of_interest] = sample[self.feature_of_interest] + modifier
            return sample
        else:
            return sample
