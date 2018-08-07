import sc2
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, STALKER, \
CYBERNETICSCORE, STARGATE, VOIDRAY, MINERALFIELD, RESEARCH_PROTOSSAIRWEAPONS, FLEETBEACON, \
    FORGE, PHOTONCANNON
from sc2.ids.buff_id import BuffId
from sc2.constants import AbilityId
import random

VERSION_NUMBER = "0.0.2"

# Just used as reference

class GreenBot(sc2.BotAI):

    MAX_WORKERS = 67
    DEFEND_DISTANCE = 5

    seen_enemy_start = False
    air_upgrade = 0

    nexuses = None
    gateways = None
    stargates = None
    probes = None

    cyber = None
    pylon = None

    async def on_step(self, iteration):
        if iteration == 50:
            await self.chat_send("GreenBot Version " + VERSION_NUMBER)

        if self.can_skip_iteration(iteration):
            return

        self.nexuses = self.units(NEXUS).ready
        self.gateways = self.units(GATEWAY).ready.noqueue
        self.stargates = self.units(STARGATE).ready.noqueue
        self.probes = self.units(PROBE)

        if self.units(PYLON).ready.exists:
            self.pylon = self.units(PYLON).ready.random

        if not self.can_skip_distribute_workers(iteration):
            await self.distribute_workers()

        await self.chronoboost()
        await self.build_workers()
        await self.build_pylons()
        await self.build_gas()
        await self.build_tech()
        await self.expand()
        await self.build_offensive_buildings()
        await self.build_army()
        await self.build_cannons()
        await self.attack()

        # TODO prevent building in mineral line

    def can_skip_iteration(self, iteration):
        if self.supply_used <= 100:
            return False

        if self.supply_used <= 125:
            return iteration % 2 != 0

        if self.supply_used <= 150:
            return iteration % 4 != 0

        if self.supply_used <= 175:
            return iteration % 8 != 0

        return iteration % 16 != 0

    def can_skip_distribute_workers(self, iteration):
        if self.supply_used <= 25:
            return False

        if self.supply_used <= 50:
            return iteration % 4 != 0

        if self.supply_used <= 75:
            return iteration % 8 != 0

        if self.supply_used <= 125:
            return iteration % 32 != 0

        if self.supply_used <= 150:
            return iteration % 128 != 0

        return True

    async def chronoboost(self):
        if self.units(CYBERNETICSCORE).ready.exists:
            if not self.units(CYBERNETICSCORE).first.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                for nexus in self.nexuses:
                    abilities = await self.get_available_abilities(nexus)
                    cyber = self.units(CYBERNETICSCORE).ready.random
                    if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities:
                        await self.do(
                            nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, cyber))
        else:
            for nexus in self.nexuses:
                abilities = await self.get_available_abilities(nexus)
                if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities:
                    await self.do(
                        nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus))

    async def build_workers(self):
        for nexus in self.nexuses.noqueue:
            if self.can_afford(PROBE) and self.supply_left >= 1:
                if self.probes.amount < self.MAX_WORKERS:
                    await self.do(nexus.train(PROBE))

    async def build_pylons(self):
        num_nexus = self.units(NEXUS).amount
        if self.supply_left < 4 * num_nexus and not self.already_pending(PYLON) >= num_nexus:
            if self.nexuses.exists and self.can_afford(PYLON):
                await self.build(PYLON, near=self.nexuses.random)

    async def build_gas(self):
        if self.units(PROBE).amount < 16:
            return

        for nexus in self.units(NEXUS).ready:
            vaspenes = self.state.vespene_geyser.closer_than(10, nexus)
            for vaspene in vaspenes:
                worker = self.select_build_worker(vaspene.position)

                already_has_gas = self.units(ASSIMILATOR).closer_than(1.0, vaspene).exists
                if worker and self.can_afford(ASSIMILATOR) and not already_has_gas:
                    await self.do(worker.build(ASSIMILATOR, vaspene))

    async def expand(self):
        if self.enough_probes_to_expand():
            if self.can_afford(NEXUS) and not self.already_pending(NEXUS):
                await self.expand_now()

    def enough_probes_to_expand(self):
        num_probes = self.probes.amount
        num_nexus = self.nexuses.amount
        return num_probes >= num_nexus * 15

    async def build_tech(self):
        if not self.units(PYLON).ready.exists:
            return

        pylon = self.units(PYLON).ready.random

        if self.can_afford(GATEWAY):
            if not self.units(GATEWAY).exists and not self.already_pending(GATEWAY):
                await self.build(GATEWAY, near=pylon)
                return

        if self.units(GATEWAY).ready and self.can_afford(CYBERNETICSCORE):
            if not self.units(CYBERNETICSCORE).exists and not self.already_pending(CYBERNETICSCORE):
                await self.build(CYBERNETICSCORE, near=pylon)
                return

        if self.units(CYBERNETICSCORE).ready and self.can_afford(STARGATE):
            if not self.units(STARGATE).exists and not self.already_pending(STARGATE):
                await self.build(STARGATE, near=pylon)
                return

        if self.air_upgrade > 1:
            if not self.units(FLEETBEACON).exists and not self.already_pending(FLEETBEACON):
                if self.can_afford(FLEETBEACON):
                    await self.build(FLEETBEACON, near=pylon)
                    return

        if self.units(VOIDRAY).amount > 0 and self.units(CYBERNETICSCORE).idle.exists:
            if self.air_upgrade == 0 or self.units(FLEETBEACON).ready.exists:
                if self.can_afford_air_upgrade():
                    cyber = self.units(CYBERNETICSCORE).ready.first
                    self.air_upgrade += 1
                    await self.do(cyber(RESEARCH_PROTOSSAIRWEAPONS))

    def can_afford_air_upgrade(self):
        if self.air_upgrade == 0:
            return self.minerals >= 100 and self.vespene >= 100
        elif self.air_upgrade == 1:
            return self.minerals >= 175 and self.vespene >= 175
        elif self.air_upgrade == 2:
            return self.minerals >= 250 and self.vespene >= 250
        else:
            return False

    async def build_offensive_buildings(self):
        await self.build_stargates()

    async def build_stargates(self):
        if self.units(STARGATE).amount < self.nexuses.amount \
                or (self.already_pending(FLEETBEACON) and (self.units(STARGATE).amount < 1.5 * self.nexuses.amount)):
            if self.can_afford(STARGATE) and not self.already_pending(STARGATE):
                pylon = self.units(PYLON).random
                if pylon:
                    await self.build(STARGATE, near=pylon)

    async def build_army(self):
        if not self.units(CYBERNETICSCORE).ready.exists:
            return

        await self.build_voidrays()

    async def build_cannons(self):
        if self.minerals > 600:
            if self.already_pending(FORGE) or self.units(FORGE).ready.exists:
                await self.build(PHOTONCANNON, near=self.nexuses.random)
            else:
                if self.pylon:
                    await self.build(FORGE, near=self.pylon)

    async def build_stalkers(self):
        for gateway in self.units(GATEWAY).ready.noqueue:
            if self.can_afford(STALKER) and self.supply_left >= 2:
                await self.do(gateway.train(STALKER))

    async def build_voidrays(self):
        for stargate in self.units(STARGATE).ready.noqueue:
            if self.can_afford(VOIDRAY) and self.supply_left >= 4:
                await self.do(stargate.train(VOIDRAY))

    async def attack(self):
        if not self.seen_enemy_start and self.units(VOIDRAY).amount > 0:
            for voidray in self.units(VOIDRAY):
                distance_to_voidray = voidray.position.distance_to(self.enemy_start_locations[0])
                if distance_to_voidray <= 2:
                    self.seen_enemy_start = True
                    break

        idle_voidrays = self.units(VOIDRAY).idle
        if idle_voidrays.amount >= 15:
            for voidray in idle_voidrays:
                await self.do(voidray.attack(self.find_target(self.state)))

        elif self.units(VOIDRAY).amount >= 1 and len(self.known_enemy_units) > 0:
            if self.must_defend():
                for voidray in idle_voidrays:
                    await self.do(voidray.attack(random.choice(self.known_enemy_units)))

    def must_defend(self):
        for enemy in self.known_enemy_units:
            for nexus in self.nexuses:
                if enemy.position.distance_to(nexus) < self.DEFEND_DISTANCE:
                    return True
        return False

    def find_target(self, state):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        elif not self.seen_enemy_start:
            return self.enemy_start_locations[0]
        else:
            return self.enemy_start_locations[0].random_on_distance(50)
