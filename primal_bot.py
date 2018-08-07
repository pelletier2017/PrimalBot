import sc2
from task.micro import *
from task.macro.zerg_unit_task import *
from task.macro.zerg_building_task import *
from decider.random_decider import *
from decider.zerg_macro_decider import ZergMacroDecider

MACRO_TIMEOUT = 500

IGNORE_MACRO_STEPS = 0
IGNORE_MICRO_STEPS = 100
IGNORE_DISTRIBUTE_STEPS = 0


class PrimalBot(sc2.BotAI):

    macro_task = None
    macro_tick = 0

    def _prepare_first_step(self):
        super()._prepare_first_step()

        self.macro_decider = ZergMacroDecider(self)
        self.micro_decider = RandomDecider(self)

        self.micro_options = [
            AttackEnemies(self),
            AttackBuildings(self),
            AttackStartingLocation(self),
            DoNothing(self)
        ]

        self.macro_options = [
            TrainZergling(self),
            TrainDrone(self),
            TrainOverlord(self),
            BuildExtractor(self),
            BuildSpawningPool(self),
            BuildRoachWarren(self),
            Expand(self)
        ]

    async def on_step(self, iteration):

        if iteration % (IGNORE_MICRO_STEPS + 1) == 0:
            await self.micro()

        if iteration % (IGNORE_MACRO_STEPS + 1) == 0:
            await self.macro()

        if iteration % (IGNORE_DISTRIBUTE_STEPS + 1) == 0:
            await self.distribute_workers()

    async def micro(self):
        micro_task = self.micro_decider.choose(self.micro_options, self.state)
        print("Micro: " + str(micro_task))
        await micro_task.perform()

    async def macro(self):
        self.macro_tick += 1
        if self.macro_task is None or self.macro_tick >= MACRO_TIMEOUT:

            if self.macro_tick >= MACRO_TIMEOUT:
                print("Macro TIMEOUT: " + str(self.macro_task))

            self.macro_task = self.macro_decider.choose(self.macro_options, self.state)
            print("Macro CHOOSE: " + str(self.macro_task))
            self.macro_tick = 0

        if self.macro_task.is_ready():
            print("Macro PERFORM: " + str(self.macro_task))
            result = await self.macro_task.perform()
            successful = result is None
            if successful:
                self.macro_task = None
