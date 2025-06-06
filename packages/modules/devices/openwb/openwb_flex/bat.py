#!/usr/bin/env python3
from typing import TypedDict, Any

from modules.common import modbus
from modules.common.abstract_device import AbstractBat
from modules.common.component_state import BatState
from modules.common.component_type import ComponentDescriptor
from modules.common.fault_state import ComponentInfo, FaultState
from modules.common.lovato import Lovato
from modules.common.mpm3pm import Mpm3pm
from modules.common.sdm import Sdm120
from modules.common.sdm import Sdm630_72
from modules.common.simcount import SimCounter
from modules.common.store import get_bat_value_store
from modules.devices.openwb.openwb_flex.config import BatKitFlexSetup
from modules.devices.openwb.openwb_flex.versions import kit_bat_version_factory


class KwargsDict(TypedDict):
    device_id: int
    client: modbus.ModbusTcpClient_


class BatKitFlex(AbstractBat):
    def __init__(self, component_config: BatKitFlexSetup, **kwargs: Any) -> None:
        self.component_config = component_config
        self.kwargs: KwargsDict = kwargs

    def initialize(self) -> None:
        self.__device_id: int = self.kwargs['device_id']
        self.__tcp_client: modbus.ModbusTcpClient_ = self.kwargs['client']
        factory = kit_bat_version_factory(self.component_config.configuration.version)
        self.__client = factory(self.component_config.configuration.id, self.__tcp_client)
        self.sim_counter = SimCounter(self.__device_id, self.component_config.id, prefix="speicher")
        self.store = get_bat_value_store(self.component_config.id)
        self.fault_state = FaultState(ComponentInfo.from_component_config(self.component_config))

    def update(self):
        # TCP-Verbindung schließen möglichst bevor etwas anderes gemacht wird, um im Fehlerfall zu verhindern,
        # dass offene Verbindungen den Modbus-Adapter blockieren.
        with self.__tcp_client:
            if isinstance(self.__client, Sdm630_72):
                _, power = self.__client.get_power()
                power = power * -1
            else:
                _, power = self.__client.get_power()
            if isinstance(self.__client, Lovato) or isinstance(self.__client, Sdm120):
                imported, exported = self.sim_counter.sim_count(power)
            else:
                imported = self.__client.get_imported()
                exported = self.__client.get_exported()

            voltages = self.__client.get_voltages()
            powers, power = self.__client.get_power()

            if isinstance(self.__client, Mpm3pm):
                currents = [powers[i] / voltages[i] for i in range(3)]
            else:
                currents = self.__client.get_currents()

        bat_state = BatState(
            currents=currents,
            imported=imported,
            exported=exported,
            power=power
        )
        self.store.set(bat_state)


component_descriptor = ComponentDescriptor(configuration_factory=BatKitFlexSetup)
