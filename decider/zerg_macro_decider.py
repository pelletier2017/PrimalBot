from decider.abstract_decider import AbstractDecider
from task.macro.zerg_unit_task import *
from task.macro.zerg_building_task import *
from sc2.constants import HATCHERY, SPAWNINGPOOL, OVERLORD, DRONE


class ZergMacroDecider(AbstractDecider):

    def __init__(self, bot):
        super().__init__(bot)
        self.tasks = Tasks(bot)

    def choose(self, options, state):

        # break out into methods similar to GreenBot
        # make queens
        # spawn larva
        # gas
        # ling speed
        # +1 attack

        num_hatchery = len(self.bot.units(HATCHERY))
        if self.bot.supply_left < 4 * num_hatchery and not self.bot.already_pending(OVERLORD):
            return self.tasks.overlord

        if self.bot.supply_used >= 16 and not self.bot.units(SPAWNINGPOOL).exists:
            return self.tasks.spawning_pool

        if (self.bot.supply_used >= 15 and not self.bot.already_pending(HATCHERY)) or self.bot.minerals >= 400:
            return self.tasks.expand

        if len(self.bot.units(DRONE)) <= num_hatchery * 10 and len(self.bot.units(DRONE)) <= 30:
            return self.tasks.drone

        if self.bot.units(SPAWNINGPOOL).ready.exists:
            return self.tasks.zergling

        return self.tasks.drone


class Tasks:
    def __init__(self, bot):
        self.drone = TrainDrone(bot)
        self.zergling = TrainZergling(bot)
        self.overlord = TrainOverlord(bot)
        self.expand = Expand(bot)
        self.spawning_pool = BuildSpawningPool(bot)
        self.roach_warren = BuildRoachWarren(bot)
