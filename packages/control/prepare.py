""" Aufbereitung der Daten für den Algorithmus
"""

import logging

from control import data
from modules.common.component_type import ComponentType


log = logging.getLogger(__name__)


class Prepare:
    def __init__(self):
        pass

    def setup_algorithm(self) -> None:
        """ bereitet die Daten für den Algorithmus vor und startet diesen.
        """
        try:
            data.data.pv_all_data.calc_power_for_all_components()
            data.data.bat_all_data.calc_power_for_all_components()
            for cp in data.data.cp_data.values():
                cp.setup_values_at_start()
            levels = data.data.counter_all_data.get_list_of_elements_per_level()
            for level in reversed(levels):
                for element in level:
                    if element["type"] == ComponentType.COUNTER.value:
                        data.data.counter_data[f"counter{element['id']}"].setup_counter()
            for cp in data.data.cp_data.values():
                cp.update(data.data.ev_data)
            # Nach cp update, da für die Speicher-Sperre der Lademodus bekannt sein muss.
            data.data.bat_all_data.setup_bat()
            data.data.cp_all_data.get_cp_sum()
            data.data.cp_all_data.no_charge()
            data.data.counter_all_data.set_home_consumption()
            data.data.io_actions.setup()
        except Exception:
            log.exception("Fehler im Prepare-Modul")
        data.data.print_all()
