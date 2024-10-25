#!/usr/bin/env python3
import logging
from typing import Iterable, Union

from modules.common.abstract_device import DeviceDescriptor
from modules.common.component_context import SingleComponentUpdateContext
from modules.common.configurable_device import ConfigurableDevice, ComponentFactoryByType, MultiComponentUpdater
from modules.common.modbus import ModbusTcpClient_
from modules.devices.fox_ess.fox_ess_h3_pro.bat import FoxEssH3ProBat
from modules.devices.fox_ess.fox_ess_h3_pro.counter import FoxEssH3ProCounter
from modules.devices.fox_ess.fox_ess_h3_pro.inverter import FoxEssH3ProInverter
from modules.devices.fox_ess.fox_ess_h3_pro.config import FoxEssH3Pro, FoxEssH3ProBatSetup, FoxEssH3ProCounterSetup, FoxEssH3ProInverterSetup

log = logging.getLogger(__name__)


def create_device(device_config: FoxEssH3Pro):
    def create_bat_component(component_config: FoxEssH3ProBatSetup):
        return FoxEssH3ProBat(component_config)

    def create_counter_component(component_config: FoxEssH3ProCounterSetup):
        return FoxEssH3ProCounter(component_config)

    def create_inverter_component(component_config: FoxEssH3ProInverterSetup):
        return FoxEssH3ProInverter(component_config)

    def update_components(components: Iterable[Union[FoxEssH3ProBat, FoxEssH3ProCounter, FoxEssH3ProInverter]]):
        with client as c:
            for component in components:
                with SingleComponentUpdateContext(component.fault_state):
                    component.update(c)

    try:
        client = ModbusTcpClient_(device_config.configuration.ip_address, device_config.configuration.port)
    except Exception:
        log.exception("Fehler in create_device")
    return ConfigurableDevice(
        device_config=device_config,
        component_factory=ComponentFactoryByType(
            bat=create_bat_component,
            counter=create_counter_component,
            inverter=create_inverter_component,
        ),
        component_updater=MultiComponentUpdater(update_components)
    )


device_descriptor = DeviceDescriptor(configuration_factory=FoxEssH3Pro)
