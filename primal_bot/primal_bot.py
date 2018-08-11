import sc2
from task.micro.entire_army import *
from task.macro.zerg_unit import *
from task.macro.zerg_building import *
from decider.random_decider import *
from decider.zerg_macro_decider import ZergMacroDecider

# steps before old task times out and new task is chosen
MACRO_TIMEOUT = 500

# number of skipped steps (ex 100 = skip 100 steps, perform 1 step)
# used to reduce lag
SKIPPED_MACRO_STEPS = 0
SKIPPED_MICRO_STEPS = 100
SKIPPED_DISTRIBUTE_STEPS = 0


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
        if iteration == 0:
            await self.chat_send("Hi I am PrimalBot")

        if iteration % (SKIPPED_MICRO_STEPS + 1) == 0:
            await self.micro()

        if iteration % (SKIPPED_MACRO_STEPS + 1) == 0:
            await self.macro()

        if iteration % (SKIPPED_DISTRIBUTE_STEPS + 1) == 0:
            await self.distribute_workers()

    async def micro(self):
        micro_task = self.micro_decider.choose(self.micro_options, self.state)
        print("Micro Perform: " + str(micro_task))
        await micro_task.perform()

    async def macro(self):
        self.macro_tick += 1
        if self.macro_task is None or self.macro_tick >= MACRO_TIMEOUT:
            if self.macro_tick >= MACRO_TIMEOUT:
                print("Macro TIMEOUT: " + str(self.macro_task))
            await self.choose_macro_task()

        if self.macro_task.is_ready():
            successful = await self.perform_macro()
            if successful:
                self.macro_task = None

    async def choose_macro_task(self):
        self.macro_task = self.macro_decider.choose(self.macro_options, self.state)
        self.macro_tick = 0
        print("Macro CHOOSE: " + str(self.macro_task))

    async def perform_macro(self):
        print("Macro PERFORM: " + str(self.macro_task))
        result = await self.macro_task.perform()
        successful = result is None
        return successful
