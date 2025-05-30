#!/usr/bin/env python3
import logging

from modules.common.abstract_device import AbstractCounter
from modules.common.component_state import CounterState
from modules.common.component_type import ComponentDescriptor
from modules.common.fault_state import ComponentInfo, FaultState
from modules.common.store import get_counter_value_store
from modules.devices.solar_view.solar_view.api import request
from modules.devices.solar_view.solar_view.config import SolarViewCounterSetup

log = logging.getLogger(__name__)


class SolarViewCounter(AbstractCounter):
    def __init__(self, component_config: SolarViewCounterSetup) -> None:
        self.component_config = component_config

    def initialize(self) -> None:
        self.store = get_counter_value_store(self.component_config.id)
        self.fault_state = FaultState(ComponentInfo.from_component_config(self.component_config))

    def update(self, ip_address: str, port: int, timeout: int) -> None:
        exported_values = request(ip_address, port, timeout, '21*')
        exported = 1000 * int(exported_values[9])

        values = request(ip_address, port, timeout, '22*')
        imported = 1000 * int(values[9])
        power = -1 * int(values[10])

        if len(values) > 20:
            self.store.set(CounterState(
                imported=imported,
                exported=exported,
                power=power,
                currents=[float(values[20]), float(values[22]), float(values[24])],
                voltages=[float(values[19]), float(values[21]), float(values[23])]
            ))
        else:
            self.store.set(CounterState(
                imported=imported,
                exported=exported,
                power=power
            ))


component_descriptor = ComponentDescriptor(configuration_factory=SolarViewCounterSetup)
