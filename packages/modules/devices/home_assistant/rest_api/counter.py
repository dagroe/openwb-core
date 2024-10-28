#!/usr/bin/env python3
from typing import Dict, Union

from dataclass_utils import dataclass_from_dict
from modules.common.abstract_device import AbstractCounter
from modules.common.component_state import CounterState
from modules.common.component_type import ComponentDescriptor
from modules.common.fault_state import ComponentInfo, FaultState
from modules.common.simcount._simcounter import SimCounter
from modules.common.store import get_counter_value_store
from modules.devices.home_assistant.rest_api.api import parse_value, parse_values
from modules.devices.home_assistant.rest_api.config import RestApiCounterSetup

import logging

log = logging.getLogger(__name__)

class RestApiCounter(AbstractCounter):
    def __init__(self, device_id: int, component_config: Union[Dict, RestApiCounterSetup]) -> None:
        self.__device_id = device_id
        self.component_config = dataclass_from_dict(RestApiCounterSetup, component_config)

    def initialize(self) -> None:
        self.sim_counter = SimCounter(self.__device_id, self.component_config.id, prefix="bezug")
        self.store = get_counter_value_store(self.component_config.id)
        self.fault_state = FaultState(ComponentInfo.from_component_config(self.component_config))

    def get_entity_mapping(self) -> Dict[str, str]:
        config = self.component_config.configuration

        mapping = {}

        if config.entity_power is not None:
            mapping[f"count_{self.__device_id}_power"] = config.entity_power

        if config.entity_exported is not None:
            mapping[f"count_{self.__device_id}_exported"] = config.entity_exported

        if config.entity_imported is not None:
            mapping[f"count_{self.__device_id}_imported"] = config.entity_imported

        if config.entity_power_l1 is not None:
            mapping[f"count_{self.__device_id}_power_l1"] = config.entity_power_l1

        if config.entity_power_l2 is not None:
            mapping[f"count_{self.__device_id}_power_l2"] = config.entity_power_l2

        if config.entity_power_l3 is not None:
            mapping[f"count_{self.__device_id}_power_l3"] = config.entity_power_l3

        if config.entity_current_l1 is not None:
            mapping[f"count_{self.__device_id}_current_l1"] = config.entity_current_l1

        if config.entity_current_l2 is not None:
            mapping[f"count_{self.__device_id}_current_l2"] = config.entity_current_l2

        if config.entity_current_l3 is not None:
            mapping[f"count_{self.__device_id}_current_l3"] = config.entity_current_l3

        if config.entity_voltage_l1 is not None:
            mapping[f"count_{self.__device_id}_voltage_l1"] = config.entity_voltage_l1

        if config.entity_voltage_l2 is not None:
            mapping[f"count_{self.__device_id}_voltage_l2"] = config.entity_voltage_l2

        if config.entity_voltage_l3 is not None:
            mapping[f"count_{self.__device_id}_voltage_l3"] = config.entity_voltage_l3

        if config.entity_frequency is not None:
            mapping[f"count_{self.__device_id}_frequency"] = config.entity_frequency

        return mapping

    def update(self, response):
        power = parse_value(response, key=f"count_{self.__device_id}_power", factor=1000.0)

        powers = parse_values(response, keys=[f"count_{self.__device_id}_power_l1", f"count_{self.__device_id}_power_l2", f"count_{self.__device_id}_power_l3"], factor=1000.0)

        currents = parse_values(response, keys=[f"count_{self.__device_id}_current_l1", f"count_{self.__device_id}_current_l2", f"count_{self.__device_id}_current_l3"], factor=1000.0)

        voltages = parse_values(response, keys=[f"count_{self.__device_id}_voltage_l1", f"count_{self.__device_id}_voltage_l2", f"count_{self.__device_id}_voltage_l3"])

        imported = parse_value(response, key=f"count_{self.__device_id}_imported", factor=1000.0)
        exported = parse_value(response, key=f"count_{self.__device_id}_exported", factor=1000.0)

        if imported is None or exported is None:
            imported, exported = self.sim_counter.sim_count(power)

        frequency = parse_value(response, f"count_{self.__device_id}_frequency")

        counter_state = CounterState(
            power=power,
            powers=powers,
            exported=exported,
            imported=imported,
            currents=currents,
            voltages=voltages,
            frequency=frequency
        )
        self.store.set(counter_state)

        log.info(f"update counter: power: {power} - powers: {powers} - currents: {None} - voltages: {voltages} - frequency: {frequency} - exported: {exported} - imported: {imported}")


component_descriptor = ComponentDescriptor(configuration_factory=RestApiCounterSetup)
