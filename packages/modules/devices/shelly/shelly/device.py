#!/usr/bin/env python3
import logging
from typing import List
import os
from modules.common import req

from helpermodules.cli import run_using_positional_cli_args
from modules.common.abstract_device import DeviceDescriptor
from modules.common.configurable_device import (ConfigurableDevice, ComponentFactoryByType, IndependentComponentUpdater)
from modules.devices.shelly.shelly.inverter import ShellyInverter
from modules.devices.shelly.shelly.bat import ShellyBat
from modules.devices.shelly.shelly.counter import ShellyCounter
from modules.devices.shelly.shelly.config import Shelly, ShellyConfiguration
from modules.devices.shelly.shelly.config import ShellyInverterSetup, ShellyInverterConfiguration
from modules.devices.shelly.shelly.config import ShellyBatSetup
from modules.devices.shelly.shelly.config import ShellyCounterSetup


log = logging.getLogger(__name__)


def get_device_generation(address: str) -> int:
    url = "http://" + address + "/shelly"
    generation = 1
    device_info = req.get_http_session().get(url, timeout=3).json()
    if 'gen' in device_info:  # gen 2+
        generation = int(device_info['gen'])
    return generation


def create_device(device_config: Shelly) -> ConfigurableDevice:
    def create_counter_component(component_config: ShellyCounterSetup) -> ShellyCounter:
        return ShellyCounter(component_config,
                             device_id=device_config.id,
                             ip_address=device_config.configuration.ip_address,
                             factor=device_config.configuration.factor,
                             generation=get_device_generation(device_config.configuration.ip_address))

    def create_inverter_component(component_config: ShellyInverterSetup) -> ShellyInverter:
        return ShellyInverter(component_config,
                              device_id=device_config.id,
                              ip_address=device_config.configuration.ip_address,
                              factor=device_config.configuration.factor,
                              generation=get_device_generation(device_config.configuration.ip_address))

    def create_bat_component(component_config: ShellyBatSetup) -> ShellyBat:
        return ShellyBat(component_config,
                         device_id=device_config.id,
                         ip_address=device_config.configuration.ip_address,
                         factor=device_config.configuration.factor,
                         generation=get_device_generation(device_config.configuration.ip_address))

    return ConfigurableDevice(
        device_config=device_config,
        component_factory=ComponentFactoryByType(
            counter=create_counter_component,
            inverter=create_inverter_component,
            bat=create_bat_component
        ),
        component_updater=IndependentComponentUpdater(lambda component: component.update())
    )


def run_device_legacy(device_config: Shelly,
                      component_config: ShellyInverterSetup) -> None:
    device = create_device(device_config)
    device.add_component(component_config)
    log.debug("Shelly Configuration: %s, Component Configuration: %s", device_config, component_config)
    device.update()


def create_legacy_device_config(address: str, generation: int,
                                num: int) -> Shelly:
    device_config = Shelly(configuration=ShellyConfiguration(ip_address=address, generation=generation), id=num)
    log.debug("Config: %s", device_config.configuration)
    return device_config


def read_legacy_inverter(address: str, num: int) -> None:
    component_config = ShellyInverterSetup(configuration=ShellyInverterConfiguration())
    component_config.id = num
    generation = 1
    generation_file_name = '/var/www/html/openWB/ramdisk/shelly_wr_ret.' + address + '_shelly_infog'
    # ToDo: remove hardcoded path to ramdisk!
    if os.path.isfile(generation_file_name):
        with open(generation_file_name, 'r') as file:
            generation = int(file.read())
    else:
        generation = get_device_generation(address)
        with open(generation_file_name, 'w') as file:
            file.write(str(generation))
    run_device_legacy(create_legacy_device_config(address, generation,
                                                  num), component_config)


def main(argv: List[str]) -> None:
    run_using_positional_cli_args(
        {"inverter": read_legacy_inverter}, argv)


device_descriptor = DeviceDescriptor(configuration_factory=Shelly)
