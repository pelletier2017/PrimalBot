from abc import ABC, abstractmethod


class AbstractDecider(ABC):

    def __init__(self, sc2_bot):
        self.bot = sc2_bot

    @abstractmethod
    def choose(self, options, state):
        pass
