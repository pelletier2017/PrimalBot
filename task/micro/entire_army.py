from sc2.constants import PROBE, LARVA, OVERLORD, EGG, QUEEN
import random

from task.abstract_task import AbstractTask
from abc import ABC


class MicroTask(AbstractTask, ABC):

    bot = None

    def __init__(self, sc2_bot):
        super().__init__(sc2_bot)

    async def is_ready(self):
        return True

    async def _attack_one_of(self, targets, attacker=None):
        if attacker is None:
            attacker = self._army()

        if targets is not None and len(targets) > 0:
            point = random.choice(targets).position
            await self._attack_point_with(point, attacker)

    async def _attack_point_with(self, point, attackers):
        actions = []
        for unit in attackers:
            actions.append(unit.attack(point.position, queue=False))
        await self.bot.do_actions(actions)

    def _army(self):
        workers = self.bot.workers

        larvae = self.bot.units(LARVA)
        eggs = self.bot.units(EGG)
        overlords = self.bot.units(OVERLORD)
        queens = self.bot.units(QUEEN)
        harmless_zerg = larvae + eggs + overlords + queens

        return self.bot.units().not_structure - workers - harmless_zerg

    def _workers(self):
        return self.bot.units(PROBE)


class AttackEnemies(MicroTask):
    def __init__(self, sc2_bot):
        super().__init__(sc2_bot)

    async def perform(self):
        await self._attack_one_of(self.bot.known_enemy_units)


class AttackBuildings(MicroTask):
    def __init__(self, sc2_bot):
        super().__init__(sc2_bot)

    async def perform(self):
        await self._attack_one_of(self.bot.known_enemy_structures)


class AttackStartingLocation(MicroTask):
    def __init__(self, sc2_bot):
        super().__init__(sc2_bot)

    async def perform(self):
        await self._attack_one_of(self.bot.enemy_start_locations)


class DefendWithWorkers(MicroTask):
    def __init__(self, sc2_bot):
        super().__init__(sc2_bot)

    async def perform(self):
        await self._attack_one_of(self.bot.known_enemy_units, attacker=self._workers())


class DoNothing(MicroTask):
    def __init__(self, sc2_bot):
        super().__init__(sc2_bot)

    async def perform(self):
        return
