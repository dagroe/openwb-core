from typing import Optional

from helpermodules.auto_str import auto_str
from modules.common.component_setup import ComponentSetup
from ..vendor import vendor_descriptor


class FoxEssH3ProConfiguration:
    def __init__(self,
                 ip_address: Optional[str] = None,
                 port: int = 502):
        self.ip_address = ip_address
        self.port = port


class FoxEssH3Pro:
    def __init__(self,
                 name: str = "FoxESS H3-Pro",
                 type: str = "fox_ess_h3_pro",
                 id: int = 0,
                 configuration: FoxEssH3ProConfiguration = None) -> None:
        self.name = name
        self.type = type
        self.vendor = vendor_descriptor.configuration_factory().type
        self.id = id
        self.configuration = configuration or FoxEssH3ProConfiguration()


@auto_str
class FoxEssH3ProBatConfiguration:
    def __init__(self, modbus_id: int = 1):
        self.modbus_id = modbus_id


@auto_str
class FoxEssH3ProBatSetup(ComponentSetup[FoxEssH3ProBatConfiguration]):
    def __init__(self,
                 name: str = "FoxEss H3-Pro Speicher",
                 type: str = "bat",
                 id: int = 0,
                 configuration: FoxEssH3ProBatConfiguration = None) -> None:
        super().__init__(name, type, id, configuration or FoxEssH3ProBatConfiguration())


@auto_str
class FoxEssH3ProCounterConfiguration:
    def __init__(self, modbus_id: int = 1):
        self.modbus_id = modbus_id


@auto_str
class FoxEssH3ProCounterSetup(ComponentSetup[FoxEssH3ProCounterConfiguration]):
    def __init__(self,
                 name: str = "FoxESS H3-Pro Zähler",
                 type: str = "counter",
                 id: int = 0,
                 configuration: FoxEssH3ProCounterConfiguration = None) -> None:
        super().__init__(name, type, id, configuration or FoxEssH3ProCounterConfiguration())


@auto_str
class FoxEssH3ProInverterConfiguration:
    def __init__(self, modbus_id: int = 1):
        self.modbus_id = modbus_id


@auto_str
class FoxEssH3ProInverterSetup(ComponentSetup[FoxEssH3ProInverterConfiguration]):
    def __init__(self,
                 name: str = "FoxEss H3-Pro Wechselrichter",
                 type: str = "inverter",
                 id: int = 0,
                 configuration: FoxEssH3ProInverterConfiguration = None) -> None:
        super().__init__(name, type, id, configuration or FoxEssH3ProInverterConfiguration())
