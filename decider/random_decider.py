import random
from decider.abstract_decider import AbstractDecider


class RandomDecider(AbstractDecider):

    def choose(self, options, state):
        return random.choice(options)
