#!/usr/bin/env python3
import logging
from typing import Tuple, List, TypedDict, Any

from modules.common import modbus
from modules.common.abstract_device import AbstractCounter
from modules.common.component_state import CounterState
from modules.common.component_type import ComponentDescriptor
from modules.common.fault_state import ComponentInfo, FaultState
from modules.common.simcount._simcounter import SimCounter
from modules.common.modbus import ModbusDataType
from modules.common.store import get_counter_value_store
from modules.devices.e3dc.e3dc.config import E3dcCounterSetup

log = logging.getLogger(__name__)


def get_meter_phases(id: int, meters: List[int]) -> List[int]:
    return next(meters[i+1:i+4] for i in reversed(range(0, len(meters), 4)) if meters[i] == id)


def read_counter(client: modbus.ModbusTcpClient_, modbus_id: int) -> Tuple[int, List[int]]:
    log.debug("Beginning EVU update")
    # 40130,40131, 40132 je Phasenleistung in Watt
    # max 7 Leistungsmesser verbaut ab 40105, typ 1 ist evu
    # Modbus Dokumentation Leistungsmesser von #0 bis #6
    # bei den meisten e3dc auf 40128
    # farm haben typ 5, normale e3dc haben nur typ 1 und keinen typ 5
    # bei farm ist typ 1 vorhanden aber liefert immer 0
    meters = list(map(int, client.read_holding_registers(40104, [ModbusDataType.INT_16] * 28, unit=modbus_id)))
    log.debug("meters: %s", meters)
    try:
        powers = get_meter_phases(5, meters)
        log.debug("e3dc farm detected")
    except StopIteration:
        powers = get_meter_phases(1, meters)
        log.debug("e3dc no farm detected")
    power = sum(powers)  # power wird nicht mehr über modbus (40073) gelesen , da 0 bei Farm
    log.debug("power: %d, powers %s", power, powers)
    return power, powers


class KwargsDict(TypedDict):
    device_id: int
    modbus_id: int
    client: modbus.ModbusTcpClient_


class E3dcCounter(AbstractCounter):
    def __init__(self, component_config: E3dcCounterSetup, **kwargs: Any) -> None:
        self.component_config = component_config
        self.kwargs: KwargsDict = kwargs

    def initialize(self) -> None:
        self.__device_id: int = self.kwargs['device_id']
        self.__modbus_id: int = self.kwargs['modbus_id']
        self.client: modbus.ModbusTcpClient_ = self.kwargs['client']
        self.sim_counter = SimCounter(self.__device_id, self.component_config.id, prefix="bezug")
        self.store = get_counter_value_store(self.component_config.id)
        self.fault_state = FaultState(ComponentInfo.from_component_config(self.component_config))

    def update(self) -> None:
        power, powers = read_counter(self.client, self.__modbus_id)
        imported, exported = self.sim_counter.sim_count(power)
        counter_state = CounterState(
            imported=imported,
            exported=exported,
            powers=powers,
            power=power
        )
        self.store.set(counter_state)


component_descriptor = ComponentDescriptor(configuration_factory=E3dcCounterSetup)
