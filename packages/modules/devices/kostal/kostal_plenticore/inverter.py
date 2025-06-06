#!/usr/bin/env python3
from typing import Any, Callable
from modules.common.abstract_device import AbstractInverter
from modules.common.component_state import InverterState
from modules.common.component_type import ComponentDescriptor
from modules.common.fault_state import ComponentInfo, FaultState
from modules.common.modbus import ModbusDataType
from modules.common.store import get_inverter_value_store
from modules.devices.kostal.kostal_plenticore.config import KostalPlenticoreInverterSetup


class KostalPlenticoreInverter(AbstractInverter):
    def __init__(self, component_config: KostalPlenticoreInverterSetup) -> None:
        self.component_config = component_config

    def initialize(self) -> None:
        self.store = get_inverter_value_store(self.component_config.id)
        self.fault_state = FaultState(ComponentInfo.from_component_config(self.component_config))

    def read_state(self, reader: Callable[[int, ModbusDataType], Any]) -> InverterState:
        # PV-Anlage kann nichts verbrauchen, also ggf. Register-/Rundungsfehler korrigieren.
        power = reader(575, ModbusDataType.INT_16) * -1
        exported = reader(320, ModbusDataType.FLOAT_32)

        return InverterState(
            power=power,
            exported=exported
        )

    def dc_in_string_1_2(self, reader: Callable[[int, ModbusDataType], Any]):
        return reader(260, ModbusDataType.FLOAT_32) + reader(270, ModbusDataType.FLOAT_32)

    def update(self, state):
        self.store.set(state)


component_descriptor = ComponentDescriptor(configuration_factory=KostalPlenticoreInverterSetup)
