#!/usr/bin/env python3
from typing import Any, Dict, List, TypedDict

from modules.common.abstract_device import AbstractCounter
from modules.common.component_state import CounterState
from modules.common.component_type import ComponentDescriptor, ComponentType
from modules.common.fault_state import ComponentInfo, FaultState
from modules.common.simcount import SimCounter
from modules.common.store import get_counter_value_store
from modules.common.utils.peak_filter import PeakFilter
from modules.devices.home_assistant.rest_api.api import (ENERGY_FACTORS, POWER_FACTORS, parse_required_value,
                                                         parse_value, parse_values, unit_factor)
from modules.devices.home_assistant.rest_api.config import RestApiCounterSetup

PHASE_ENTITIES = ("power", "current", "voltage")


class KwargsDict(TypedDict):
    device_id: int


class RestApiCounter(AbstractCounter):
    def __init__(self, component_config: RestApiCounterSetup, **kwargs: Any) -> None:
        self.component_config = component_config
        self.kwargs: KwargsDict = kwargs

    def initialize(self) -> None:
        self.__device_id: int = self.kwargs['device_id']
        self.sim_counter = SimCounter(self.__device_id, self.component_config.id, prefix="bezug")
        self.store = get_counter_value_store(self.component_config.id)
        self.fault_state = FaultState(ComponentInfo.from_component_config(self.component_config))
        self.peak_filter = PeakFilter(ComponentType.COUNTER, self.component_config.id, self.fault_state)

    def _key(self, name: str) -> str:
        return f"{self.component_config.type}_{self.component_config.id}_{name}"

    def _phase_keys(self, name: str) -> List[str]:
        return [self._key(f"{name}_l{phase}") for phase in (1, 2, 3)]

    def get_entity_mapping(self) -> Dict[str, str]:
        config = self.component_config.configuration
        names = ["power", "imported", "exported", "frequency"]
        names += [f"{name}_l{phase}" for name in PHASE_ENTITIES for phase in (1, 2, 3)]
        mapping = {}
        for name in names:
            entity = getattr(config, f"entity_{name}")
            if entity:
                mapping[self._key(name)] = entity
        return mapping

    def update(self, response: Dict[str, Any]) -> None:
        config = self.component_config.configuration
        power_factor = unit_factor(config.unit_power, POWER_FACTORS, "die Leistung")
        energy_factor = unit_factor(config.unit_energy, ENERGY_FACTORS, "die Energiemengen")

        power = parse_required_value(response, self._key("power"), config.entity_power, power_factor)
        powers = parse_values(response, self._phase_keys("power"), power_factor)
        # Ströme, Spannungen und Frequenz liefert Home Assistant bereits in A, V bzw. Hz.
        currents = parse_values(response, self._phase_keys("current"))
        voltages = parse_values(response, self._phase_keys("voltage"))
        frequency = parse_value(response, self._key("frequency"))

        imported = parse_value(response, self._key("imported"), energy_factor)
        exported = parse_value(response, self._key("exported"), energy_factor)

        imported, exported = self.peak_filter.check_values(power, imported, exported)
        if imported is None or exported is None:
            imported, exported = self.sim_counter.sim_count(power)

        counter_state = CounterState(
            power=power,
            powers=powers,
            currents=currents,
            voltages=voltages,
            imported=imported,
            exported=exported,
            # ohne konfigurierte Entität den Vorgabewert von CounterState beibehalten
            frequency=frequency if frequency is not None else 50
        )
        self.store.set(counter_state)


component_descriptor = ComponentDescriptor(configuration_factory=RestApiCounterSetup)
