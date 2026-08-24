#!/usr/bin/env python3
from typing import Any, Dict, TypedDict

from modules.common.abstract_device import AbstractBat
from modules.common.component_state import BatState
from modules.common.component_type import ComponentDescriptor, ComponentType
from modules.common.fault_state import ComponentInfo, FaultState
from modules.common.simcount import SimCounter
from modules.common.store import get_bat_value_store
from modules.common.utils.peak_filter import PeakFilter
from modules.devices.home_assistant.rest_api.api import (ENERGY_FACTORS, POWER_FACTORS, parse_required_value,
                                                         parse_value, unit_factor)
from modules.devices.home_assistant.rest_api.config import RestApiBatSetup


class KwargsDict(TypedDict):
    device_id: int


class RestApiBat(AbstractBat):
    def __init__(self, component_config: RestApiBatSetup, **kwargs: Any) -> None:
        self.component_config = component_config
        self.kwargs: KwargsDict = kwargs

    def initialize(self) -> None:
        self.__device_id: int = self.kwargs['device_id']
        self.sim_counter = SimCounter(self.__device_id, self.component_config.id, prefix="speicher")
        self.store = get_bat_value_store(self.component_config.id)
        self.fault_state = FaultState(ComponentInfo.from_component_config(self.component_config))
        self.peak_filter = PeakFilter(ComponentType.BAT, self.component_config.id, self.fault_state)

    def _key(self, name: str) -> str:
        return f"{self.component_config.type}_{self.component_config.id}_{name}"

    def get_entity_mapping(self) -> Dict[str, str]:
        config = self.component_config.configuration
        mapping = {}
        for name in ("power", "charge", "discharge", "soc", "imported", "exported"):
            entity = getattr(config, f"entity_{name}")
            if entity:
                mapping[self._key(name)] = entity
        return mapping

    def update(self, response: Dict[str, Any]) -> None:
        config = self.component_config.configuration
        power_factor = unit_factor(config.unit_power, POWER_FACTORS, "die Leistung")
        energy_factor = unit_factor(config.unit_energy, ENERGY_FACTORS, "die Energiemengen")

        if config.entity_power:
            power = parse_required_value(response, self._key("power"), config.entity_power, power_factor)
        else:
            # Manche Speicher liefern Laden und Entladen als getrennte, stets positive Entitäten.
            charge = parse_value(response, self._key("charge"), power_factor)
            discharge = parse_value(response, self._key("discharge"), power_factor)
            if charge is None and discharge is None:
                raise ValueError("Es ist weder eine Entitäts-ID für die Leistung noch für Laden/Entladen "
                                 "konfiguriert. Bitte Konfiguration anpassen.")
            power = (charge or 0) - (discharge or 0)

        soc = parse_value(response, self._key("soc"))
        imported = parse_value(response, self._key("imported"), energy_factor)
        exported = parse_value(response, self._key("exported"), energy_factor)

        imported, exported = self.peak_filter.check_values(power, imported, exported)
        if imported is None or exported is None:
            imported, exported = self.sim_counter.sim_count(power)

        self.store.set(BatState(
            power=power,
            imported=imported,
            exported=exported,
            soc=soc if soc is not None else 0
        ))


component_descriptor = ComponentDescriptor(configuration_factory=RestApiBatSetup)
