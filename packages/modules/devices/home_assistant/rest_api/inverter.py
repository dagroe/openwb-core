#!/usr/bin/env python3
from typing import Any, Dict, TypedDict

from modules.common.abstract_device import AbstractInverter
from modules.common.component_state import InverterState
from modules.common.component_type import ComponentDescriptor, ComponentType
from modules.common.fault_state import ComponentInfo, FaultState
from modules.common.simcount import SimCounter
from modules.common.store import get_inverter_value_store
from modules.common.utils.peak_filter import PeakFilter
from modules.devices.home_assistant.rest_api.api import (ENERGY_FACTORS, POWER_FACTORS, parse_required_value,
                                                         parse_value, unit_factor)
from modules.devices.home_assistant.rest_api.config import RestApiInverterSetup


class KwargsDict(TypedDict):
    device_id: int


class RestApiInverter(AbstractInverter):
    def __init__(self, component_config: RestApiInverterSetup, **kwargs: Any) -> None:
        self.component_config = component_config
        self.kwargs: KwargsDict = kwargs

    def initialize(self) -> None:
        self.__device_id: int = self.kwargs['device_id']
        self.sim_counter = SimCounter(self.__device_id, self.component_config.id, prefix="pv")
        self.store = get_inverter_value_store(self.component_config.id)
        self.fault_state = FaultState(ComponentInfo.from_component_config(self.component_config))
        self.peak_filter = PeakFilter(ComponentType.INVERTER, self.component_config.id, self.fault_state)

    def _key(self, name: str) -> str:
        return f"{self.component_config.type}_{self.component_config.id}_{name}"

    def get_entity_mapping(self) -> Dict[str, str]:
        config = self.component_config.configuration
        mapping = {}
        for name in ("power", "exported"):
            entity = getattr(config, f"entity_{name}")
            if entity:
                mapping[self._key(name)] = entity
        return mapping

    def update(self, response: Dict[str, Any]) -> None:
        config = self.component_config.configuration
        power_factor = unit_factor(config.unit_power, POWER_FACTORS, "die Leistung")
        energy_factor = unit_factor(config.unit_energy, ENERGY_FACTORS, "die Energiemengen")

        # openWB erwartet die Erzeugungsleistung negativ, Home Assistant liefert sie üblicherweise positiv.
        power = parse_required_value(response, self._key("power"), config.entity_power, power_factor)
        if power >= 0:
            power = power * -1

        exported = parse_value(response, self._key("exported"), energy_factor)
        _, exported = self.peak_filter.check_values(power, None, exported)
        if exported is None:
            _, exported = self.sim_counter.sim_count(power)

        self.store.set(InverterState(
            power=power,
            exported=exported
        ))


component_descriptor = ComponentDescriptor(configuration_factory=RestApiInverterSetup)
