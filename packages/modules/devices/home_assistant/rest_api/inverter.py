#!/usr/bin/env python3
from typing import Dict, Union

from dataclass_utils import dataclass_from_dict
from modules.common.abstract_device import AbstractInverter
from modules.common.component_state import InverterState
from modules.common.component_type import ComponentDescriptor
from modules.common.fault_state import ComponentInfo, FaultState
from modules.common.simcount import SimCounter
from modules.common.store import get_inverter_value_store
from modules.devices.home_assistant.rest_api.api import parse_value
from modules.devices.home_assistant.rest_api.config import RestApiInverterSetup


class RestApiInverter(AbstractInverter):
    def __init__(self, device_id: int, component_config: Union[Dict, RestApiInverterSetup]) -> None:
        self.__device_id = device_id
        self.component_config = dataclass_from_dict(RestApiInverterSetup, component_config)

    def initialize(self) -> None:
        self.store = get_inverter_value_store(self.component_config.id)
        self.fault_state = FaultState(ComponentInfo.from_component_config(self.component_config))


    def get_entity_mapping(self) -> Dict[str, str]:
        config = self.component_config.configuration

        mapping = {}

        if config.entity_power is not None:
            mapping[f"inv_{self.__device_id}_power"] = config.entity_power

        if config.entity_exported is not None:
            mapping[f"inv_{self.__device_id}_exported"] = config.entity_exported

        return mapping

    def update(self, response) -> None:
        power = parse_value(response, key=f"inv_{self.__device_id}_power", factor=1000.0)
        exported = parse_value(response, key=f"inv_{self.__device_id}_exported", factor=1000.0)

        if power is not None and power >= 0:
            power = power * -1

        inverter_state = InverterState(
            power=power,
            exported=exported
        )
        self.store.set(inverter_state)


component_descriptor = ComponentDescriptor(configuration_factory=RestApiInverterSetup)
