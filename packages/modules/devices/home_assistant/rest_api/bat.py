#!/usr/bin/env python3
from typing import Dict, Union

from dataclass_utils import dataclass_from_dict
from modules.common.abstract_device import AbstractBat
from modules.common.component_state import BatState
from modules.common.component_type import ComponentDescriptor
from modules.common.fault_state import ComponentInfo, FaultState
from modules.common.simcount import SimCounter
from modules.common.store import get_bat_value_store
from modules.devices.home_assistant.rest_api.api import parse_value
from modules.devices.home_assistant.rest_api.config import RestApiBatSetup


class RestApiBat(AbstractBat):
    def __init__(self, device_id: int, component_config: Union[Dict, RestApiBatSetup]) -> None:
        self.__device_id = device_id
        self.component_config = dataclass_from_dict(RestApiBatSetup, component_config)

    def initialize(self) -> None:
        self.sim_counter = SimCounter(self.__device_id, self.component_config.id, prefix="speicher")
        self.store = get_bat_value_store(self.component_config.id)
        self.fault_state = FaultState(ComponentInfo.from_component_config(self.component_config))

    def get_entity_mapping(self) -> Dict[str, str]:
        config = self.component_config.configuration

        mapping = {}

        if config.entity_power is not None:
            mapping[f"bat_{self.__device_id}_power"] = config.entity_power

        if config.entity_charge is not None:
            mapping[f"bat_{self.__device_id}_charge"] = config.entity_charge

        if config.entity_discharge is not None:
            mapping[f"bat_{self.__device_id}_discharge"] = config.entity_discharge

        if config.entity_exported is not None:
            mapping[f"bat_{self.__device_id}_soc"] = config.entity_soc

        if config.entity_imported is not None:
            mapping[f"bat_{self.__device_id}_imported"] = config.entity_imported

        if config.entity_exported is not None:
            mapping[f"bat_{self.__device_id}_exported"] = config.entity_exported

        return mapping

    def update(self, response) -> None:
        power = parse_value(response, key=f"bat_{self.__device_id}_power", factor=1000.0)

        if power is None:
            charge = parse_value(response, key=f"bat_{self.__device_id}_charge", factor=1000.0)
            discharge = parse_value(response, key=f"bat_{self.__device_id}_discharge", factor=1000.0)

            if charge is not None or discharge is not None:
                power = (charge or 0) - (discharge or 0)
        soc = parse_value(response, key=f"bat_{self.__device_id}_soc")
        imported = parse_value(response, key=f"bat_{self.__device_id}_imported", factor=1000.0)
        exported = parse_value(response, key=f"bat_{self.__device_id}_exported", factor=1000.0)

        if imported is None or exported is None:
            imported, exported = self.sim_counter.sim_count(power)

        bat_state = BatState(
            power=power,
            exported=exported,
            imported=imported,
            soc=soc
        )
        self.store.set(bat_state)


component_descriptor = ComponentDescriptor(configuration_factory=RestApiBatSetup)
