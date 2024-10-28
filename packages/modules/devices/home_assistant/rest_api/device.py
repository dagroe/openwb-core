#!/usr/bin/env python3
import logging
from typing import List, Union, Iterable

from helpermodules.cli import run_using_positional_cli_args
from modules.common.abstract_device import DeviceDescriptor
from modules.common.configurable_device import ConfigurableDevice, ComponentFactoryByType, MultiComponentUpdater
from modules.devices.home_assistant.rest_api import bat, counter, inverter
from modules.devices.home_assistant.rest_api.api import template_post_request
from modules.devices.home_assistant.rest_api.bat import RestApiBat
from modules.devices.home_assistant.rest_api.config import (RestApi,
                                                 RestApiBatConfiguration,
                                                 RestApiBatSetup,
                                                 RestApiConfiguration,
                                                 RestApiCounterConfiguration,
                                                 RestApiCounterSetup,
                                                 RestApiInverterConfiguration,
                                                 RestApiInverterSetup)
from modules.devices.home_assistant.rest_api.counter import RestApiCounter
from modules.devices.home_assistant.rest_api.inverter import RestApiInverter

log = logging.getLogger(__name__)
RestApiComponent = Union[RestApiBat, RestApiCounter, RestApiInverter]


def create_device(device_config: RestApi):
    def create_bat(component_config: RestApiBatSetup) -> RestApiBat:
        return RestApiBat(device_config.id, component_config)

    def create_counter(component_config: RestApiCounterSetup) -> RestApiCounter:
        return RestApiCounter(device_config.id, component_config)

    def create_inverter(component_config: RestApiInverterSetup) -> RestApiInverter:
        return RestApiInverter(device_config.id, component_config)

    def update_components(components: Iterable[RestApiComponent]):
        # merge all mappings to build single template for query
        mapping = {}
        for component in components:
            mapping.update(component.get_entity_mapping())

        jsonObject = template_post_request(url=device_config.configuration.url, token=device_config.configuration.token, mapping=mapping)
        for component in components:
            component.update(jsonObject)

    return ConfigurableDevice(
        device_config,
        component_factory=ComponentFactoryByType(bat=create_bat, counter=create_counter, inverter=create_inverter),
        component_updater=MultiComponentUpdater(update_components)
    )


def read_legacy(url: str, component_config: Union[RestApiBatSetup, RestApiCounterSetup, RestApiInverterSetup]) -> None:
    dev = create_device(RestApi(configuration=RestApiConfiguration(url=url)))
    dev.add_component(component_config)
    dev.update()


def read_legacy_bat(ip_address: str, entity_power: str, entity_soc: str):
    config = RestApiBatConfiguration(entity_power=entity_power, entity_soc=entity_soc)
    read_legacy(ip_address, bat.component_descriptor.configuration_factory(id=None, configuration=config))


def read_legacy_counter(ip_address: str, entity_power: str, entity_imported: str, entity_exported: str,
                        entity_power_l1: str, entity_power_l2: str, entity_power_l3: str,
                        entity_current_l1: str, entity_current_l2: str, entity_current_l3: str):
    config = RestApiCounterConfiguration(entity_power=entity_power,
                                      entity_imported=None if entity_imported == "" else entity_imported,
                                      entity_exported=None if entity_exported == "" else entity_exported,
                                      entity_power_l1=None if entity_power_l1 == "" else entity_power_l1,
                                      entity_power_l2=None if entity_power_l2 == "" else entity_power_l2,
                                      entity_power_l3=None if entity_power_l3 == "" else entity_power_l3,
                                      entity_current_l1=None if entity_current_l1 == "" else entity_current_l1,
                                      entity_current_l2=None if entity_current_l2 == "" else entity_current_l2,
                                      entity_current_l3=None if entity_current_l3 == "" else entity_current_l3
                                      )
    read_legacy(
        ip_address,
        counter.component_descriptor.configuration_factory(id=None, configuration=config))


def read_legacy_inverter(ip_address: str, entity_power: str, entity_exported: str, num: int):
    config = RestApiInverterConfiguration(entity_power=entity_power, entity_exported=None if entity_exported == "" else entity_exported)
    read_legacy(ip_address, inverter.component_descriptor.configuration_factory(id=num, configuration=config))


def main(argv: List[str]):
    run_using_positional_cli_args(
        {"bat": read_legacy_bat, "counter": read_legacy_counter, "inverter": read_legacy_inverter}, argv
    )


device_descriptor = DeviceDescriptor(configuration_factory=RestApi)
