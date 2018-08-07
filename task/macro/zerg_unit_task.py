from task.game_task import GameTask
from sc2.constants import LARVA, ZERGLING, DRONE, OVERLORD, SPAWNINGPOOL
from abc import ABC, abstractmethod


class ZergUnitTask(GameTask, ABC):

    def __init__(self, sc2_bot):
        super().__init__(sc2_bot)

    def is_ready(self):
        return self._larvae.exists and self.bot.can_afford(self.unit()) \
               and self.has_tech() and self._has_supply()

    async def perform(self):
        await self.bot.do(self._larvae.random.train(self.unit()))

    @property
    def _larvae(self):
        return self.bot.units(LARVA)

    @abstractmethod
    def unit(self):
        pass

    @abstractmethod
    def has_tech(self):
        pass

    @abstractmethod
    def supply_cost(self):
        pass

    def _has_supply(self):
        return self.bot.supply_left >= self.supply_cost()


class TrainZergling(ZergUnitTask):

    def __init__(self, sc2_bot):
        super().__init__(sc2_bot)

    def unit(self):
        return ZERGLING

    def has_tech(self):
        return self.bot.units(SPAWNINGPOOL).ready.exists

    def supply_cost(self):
        return 1


class TrainDrone(ZergUnitTask):

    def __init__(self, sc2_bot):
        super().__init__(sc2_bot)

    def unit(self):
        return DRONE

    def has_tech(self):
        return True

    def supply_cost(self):
        return 1


class TrainOverlord(ZergUnitTask):

    def __init__(self, sc2_bot):
        super().__init__(sc2_bot)

    def unit(self):
        return OVERLORD

    def has_tech(self):
        return True

    def supply_cost(self):
        return 0
