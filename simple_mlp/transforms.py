import numpy as np

class StatTransform():
    def __init__(self):
        self.feature_of_interest = "stats_active"

    def __call__(self, sample, feature):
        if feature != self.feature_of_interest:
            return sample
        else:
            modifier = np.random.choice(np.arange(start=-5, stop=5, step=1), len(sample))
            new_sample = sample + modifier
            return new_sample