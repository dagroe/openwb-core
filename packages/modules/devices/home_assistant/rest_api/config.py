from typing import Optional

from modules.common.component_setup import ComponentSetup
from ..vendor import vendor_descriptor


class RestApiConfiguration:
    def __init__(self, url: Optional[str] = None, token: Optional[str] = None):
        # Basis-URL der Home Assistant Instanz, z.B. http://homeassistant.local:8123
        self.url = url
        # Long-Lived Access Token aus dem Home Assistant Benutzerprofil
        self.token = token


class RestApi:
    def __init__(self,
                 name: str = "Home Assistant REST API",
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
                 entity_power: Optional[str] = None,
                 entity_charge: Optional[str] = None,
                 entity_discharge: Optional[str] = None,
                 entity_soc: Optional[str] = None,
                 entity_imported: Optional[str] = None,
                 entity_exported: Optional[str] = None,
                 unit_power: str = "W",
                 unit_energy: str = "kWh"):
        self.entity_power = entity_power
        self.entity_charge = entity_charge
        self.entity_discharge = entity_discharge
        self.entity_soc = entity_soc
        self.entity_imported = entity_imported
        self.entity_exported = entity_exported
        self.unit_power = unit_power
        self.unit_energy = unit_energy


class RestApiBatSetup(ComponentSetup[RestApiBatConfiguration]):
    def __init__(self,
                 name: str = "Home Assistant Speicher",
                 type: str = "bat",
                 id: int = 0,
                 configuration: RestApiBatConfiguration = None) -> None:
        super().__init__(name, type, id, configuration or RestApiBatConfiguration())


class RestApiCounterConfiguration:
    def __init__(self,
                 entity_power: Optional[str] = None,
                 entity_imported: Optional[str] = None,
                 entity_exported: Optional[str] = None,
                 entity_power_l1: Optional[str] = None,
                 entity_power_l2: Optional[str] = None,
                 entity_power_l3: Optional[str] = None,
                 entity_current_l1: Optional[str] = None,
                 entity_current_l2: Optional[str] = None,
                 entity_current_l3: Optional[str] = None,
                 entity_voltage_l1: Optional[str] = None,
                 entity_voltage_l2: Optional[str] = None,
                 entity_voltage_l3: Optional[str] = None,
                 entity_frequency: Optional[str] = None,
                 unit_power: str = "W",
                 unit_energy: str = "kWh"):
        self.entity_power = entity_power
        self.entity_imported = entity_imported
        self.entity_exported = entity_exported
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
        self.unit_power = unit_power
        self.unit_energy = unit_energy


class RestApiCounterSetup(ComponentSetup[RestApiCounterConfiguration]):
    def __init__(self,
                 name: str = "Home Assistant Zähler",
                 type: str = "counter",
                 id: int = 0,
                 configuration: RestApiCounterConfiguration = None) -> None:
        super().__init__(name, type, id, configuration or RestApiCounterConfiguration())


class RestApiInverterConfiguration:
    def __init__(self,
                 entity_power: Optional[str] = None,
                 entity_exported: Optional[str] = None,
                 unit_power: str = "W",
                 unit_energy: str = "kWh"):
        self.entity_power = entity_power
        self.entity_exported = entity_exported
        self.unit_power = unit_power
        self.unit_energy = unit_energy


class RestApiInverterSetup(ComponentSetup[RestApiInverterConfiguration]):
    def __init__(self,
                 name: str = "Home Assistant Wechselrichter",
                 type: str = "inverter",
                 id: int = 0,
                 configuration: RestApiInverterConfiguration = None) -> None:
        super().__init__(name, type, id, configuration or RestApiInverterConfiguration())
