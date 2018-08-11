from task.abstract_task import AbstractTask
from sc2.constants import DRONE, SPAWNINGPOOL, EXTRACTOR, ROACHWARREN, HATCHERY
from abc import ABC, abstractmethod


class Expand(AbstractTask):

    building = HATCHERY

    def __init__(self, sc2_bot):
        super().__init__(sc2_bot)

    def is_ready(self):
        return self.bot.can_afford(HATCHERY) and self.bot.units(DRONE).ready.exists

    async def perform(self):
        await self.bot.expand_now()


class ZergBuildingTask(AbstractTask, ABC):

    def __init__(self, sc2_bot):
        super().__init__(sc2_bot)

    def is_ready(self):
        return self.drones.exists and self.bot.can_afford(self.building) \
               and self.has_tech() and self.main_hatchery is not None

    async def perform(self):
        return await self.bot.build(self.building, near=self.main_hatchery)

    @property
    def drones(self):
        return self.bot.units(DRONE)

    @property
    def main_hatchery(self):
        hatches = self.bot.units(HATCHERY)
        if hatches:
            return hatches.first
        else:
            return None

    @abstractmethod
    def has_tech(self):
        pass


class BuildSpawningPool(ZergBuildingTask):
    building = SPAWNINGPOOL

    def has_tech(self):
        return True


class BuildExtractor(ZergBuildingTask):
    building = EXTRACTOR

    # TODO make it choose better geyser, think about no more geysers on the map and allow to build near pending hatch
    async def perform(self):
        drone = self.bot.workers.random
        target = self.bot.state.vespene_geyser.closest_to(drone.position)
        return await self.bot.do(drone.build(self.building, target))

    def has_tech(self):
        return True


class BuildRoachWarren(ZergBuildingTask):
    building = ROACHWARREN

    def has_tech(self):
        return self.bot.units(SPAWNINGPOOL).ready.exists
