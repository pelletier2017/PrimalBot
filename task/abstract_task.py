from abc import ABC, abstractmethod
import sc2


class AbstractTask(ABC):

    bot = None

    def __init__(self, sc2_bot):
        self.bot = sc2_bot

    @abstractmethod
    async def is_ready(self):
        pass

    @abstractmethod
    async def perform(self):
        pass

    def __str__(self):
        return self.__class__.__name__
