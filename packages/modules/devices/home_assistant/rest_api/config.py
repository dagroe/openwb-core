from typing import Optional

from modules.common.component_setup import ComponentSetup
from ..vendor import vendor_descriptor


class RestApiConfiguration:
    def __init__(self, url=None, token=None):
        self.url = url
        self.token = token


class RestApi:
    def __init__(self,
                 name: str = "Rest API",
                 type: str = "rest_api",
                 id: int = 0,
                 configuration: RestApiConfiguration = None) -> None:
        self.name = name
        self.type = type
        self.vendor = vendor_descriptor.configuration_factory().type
        self.id = id
        self.configuration = configuration or RestApiConfiguration()


class RestApiBatConfiguration:
    def __init__(self,
                 entity_imported: Optional[str] = None,
                 entity_exported: Optional[str] = None,
                 entity_soc: str = "",
                 entity_power: Optional[str] = None,
                 entity_charge: Optional[str] = None,
                 entity_discharge: Optional[str] = None):
        self.entity_imported = entity_imported
        self.entity_exported = entity_exported
        self.entity_soc = entity_soc
        self.entity_power = entity_power
        self.entity_charge = entity_charge
        self.entity_discharge = entity_discharge


class RestApiBatSetup(ComponentSetup[RestApiBatConfiguration]):
    def __init__(self,
                 name: str = "Rest API Speicher",
                 type: str = "bat",
                 id: int = 0,
                 configuration: RestApiBatConfiguration = None) -> None:
        super().__init__(name, type, id, configuration or RestApiBatConfiguration())


class RestApiCounterConfiguration:
    def __init__(self, entity_power: str = "", entity_exported: Optional[str] = None, entity_imported: Optional[str] = None,
                 entity_power_l1: Optional[str] = None,
                 entity_power_l2: Optional[str] = None,
                 entity_power_l3: Optional[str] = None,
                 entity_current_l1: Optional[str] = None,
                 entity_current_l2: Optional[str] = None,
                 entity_current_l3: Optional[str] = None,
                 entity_voltage_l1: Optional[str] = None,
                 entity_voltage_l2: Optional[str] = None,
                 entity_voltage_l3: Optional[str] = None,
                 entity_frequency: Optional[str] = None):
        self.entity_power = entity_power
        self.entity_exported = entity_exported
        self.entity_imported = entity_imported
        self.entity_power_l1 = entity_power_l1
        self.entity_power_l2 = entity_power_l2
        self.entity_power_l3 = entity_power_l3
        self.entity_current_l1 = entity_current_l1
        self.entity_current_l2 = entity_current_l2
        self.entity_current_l3 = entity_current_l3
        self.entity_voltage_l1 = entity_voltage_l1
        self.entity_voltage_l2 = entity_voltage_l2
        self.entity_voltage_l3 = entity_voltage_l3
        self.entity_frequency = entity_frequency


class RestApiCounterSetup(ComponentSetup[RestApiCounterConfiguration]):
    def __init__(self,
                 name: str = "Rest API Zähler",
                 type: str = "counter",
                 id: int = 0,
                 configuration: RestApiCounterConfiguration = None) -> None:
        super().__init__(name, type, id, configuration or RestApiCounterConfiguration())


class RestApiInverterConfiguration:
    def __init__(self, entity_power: str = "", entity_exported: Optional[str] = None):
        self.entity_power = entity_power
        self.entity_exported = entity_exported


class RestApiInverterSetup(ComponentSetup[RestApiInverterConfiguration]):
    def __init__(self,
                 name: str = "Rest API Wechselrichter",
                 type: str = "inverter",
                 id: int = 0,
                 configuration: RestApiInverterConfiguration = None) -> None:
        super().__init__(name, type, id, configuration or RestApiInverterConfiguration())
