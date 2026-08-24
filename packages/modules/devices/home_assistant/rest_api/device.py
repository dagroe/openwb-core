#!/usr/bin/env python3
import logging
from typing import Iterable, Union

from modules.common.abstract_device import DeviceDescriptor
from modules.common.component_context import SingleComponentUpdateContext
from modules.common.configurable_device import ConfigurableDevice, ComponentFactoryByType, MultiComponentUpdater
from modules.devices.home_assistant.rest_api.api import template_post_request
from modules.devices.home_assistant.rest_api.bat import RestApiBat
from modules.devices.home_assistant.rest_api.config import (RestApi, RestApiBatSetup, RestApiCounterSetup,
                                                            RestApiInverterSetup)
from modules.devices.home_assistant.rest_api.counter import RestApiCounter
from modules.devices.home_assistant.rest_api.inverter import RestApiInverter

log = logging.getLogger(__name__)
RestApiComponent = Union[RestApiBat, RestApiCounter, RestApiInverter]


def create_device(device_config: RestApi):
    def create_bat_component(component_config: RestApiBatSetup) -> RestApiBat:
        return RestApiBat(component_config, device_id=device_config.id)

    def create_counter_component(component_config: RestApiCounterSetup) -> RestApiCounter:
        return RestApiCounter(component_config, device_id=device_config.id)

    def create_inverter_component(component_config: RestApiInverterSetup) -> RestApiInverter:
        return RestApiInverter(component_config, device_id=device_config.id)

    def update_components(components: Iterable[RestApiComponent]):
        configuration = device_config.configuration
        if not configuration.url:
            raise ValueError("Keine URL zur Home Assistant Instanz definiert. Bitte Konfiguration anpassen.")
        if not configuration.token:
            raise ValueError("Kein Token definiert. Bitte Konfiguration anpassen.")

        # Die Entitäten aller Komponenten werden zu einer einzigen Template-Abfrage zusammengefasst,
        # damit pro Regelintervall nur ein Request an Home Assistant nötig ist.
        mapping = {}
        for component in components:
            mapping.update(component.get_entity_mapping())
        if not mapping:
            raise ValueError("Für keine Komponente sind Entitäts-IDs konfiguriert. "
                             "Bitte Konfiguration anpassen.")

        response = template_post_request(url=configuration.url, token=configuration.token, mapping=mapping)
        for component in components:
            with SingleComponentUpdateContext(component.fault_state):
                component.update(response)

    return ConfigurableDevice(
        device_config=device_config,
        component_factory=ComponentFactoryByType(
            bat=create_bat_component,
            counter=create_counter_component,
            inverter=create_inverter_component,
        ),
        component_updater=MultiComponentUpdater(update_components)
    )


device_descriptor = DeviceDescriptor(configuration_factory=RestApi)
