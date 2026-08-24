import json
import logging
from typing import Any, Dict, List, Optional

from modules.common import req

log = logging.getLogger(__name__)

# Home Assistant liefert Leistungen und Energiemengen in der Einheit, die am Sensor konfiguriert ist.
# openWB rechnet intern in W bzw. Wh, daher werden die Werte anhand der eingestellten Einheit skaliert.
POWER_FACTORS = {"W": 1.0, "kW": 1000.0}
ENERGY_FACTORS = {"Wh": 1.0, "kWh": 1000.0}


def unit_factor(unit: str, factors: Dict[str, float], description: str) -> float:
    try:
        return factors[unit]
    except KeyError:
        raise ValueError(f"Unbekannte Einheit '{unit}' für {description}. "
                         f"Erlaubt sind: {', '.join(factors)}.")


def _render_entity(entity: str) -> str:
    # states() liefert immer einen String zurück. Der float-Filter mit Default 'null' sorgt dafür, dass
    # nicht-numerische Zustände wie 'unavailable' oder 'unknown' als JSON-null gerendert werden und die
    # Antwort in jedem Fall gültiges JSON bleibt.
    return f"{{{{ states({json.dumps(entity)}) | float('null') }}}}"


def build_template(mapping: Dict[str, str]) -> str:
    """Baut aus der Zuordnung Schlüssel -> Entitäts-ID ein Jinja-Template, das ein JSON-Objekt rendert."""
    parts = [f"{json.dumps(key)}: {_render_entity(entity)}" for key, entity in mapping.items()]
    return "{" + ", ".join(parts) + "}"


def template_post_request(url: str, token: str, mapping: Dict[str, str]) -> Dict[str, Any]:
    """Fragt alle Entitäten aller Komponenten mit einem einzigen Request an der Template-API ab."""
    template = build_template(mapping)
    log.debug(f"Sende Template-Abfrage an Home Assistant: {template}")
    response = req.get_http_session().post(
        f"{url.rstrip('/')}/api/template",
        json={"template": template},
        headers={"Authorization": f"Bearer {token}"},
        timeout=5,
    )
    log.debug(f"Antwort von Home Assistant: {response.text}")
    return json.loads(response.text)


def parse_value(res: Dict[str, Any], key: str, factor: float = 1.0) -> Optional[float]:
    value = res.get(key)
    if value is None:
        return None
    return float(value) * factor


def parse_values(res: Dict[str, Any], keys: List[str], factor: float = 1.0) -> Optional[List[float]]:
    values = [res.get(key) for key in keys]
    if any(value is None for value in values):
        return None
    return [float(value) * factor for value in values]


def parse_required_value(res: Dict[str, Any], key: str, entity: Optional[str], factor: float = 1.0) -> float:
    value = parse_value(res, key, factor)
    if value is None:
        if entity is None or entity == "":
            raise ValueError("Es ist keine Entitäts-ID für die Leistung konfiguriert. "
                             "Bitte Konfiguration anpassen.")
        raise ValueError(f"Die Entität '{entity}' hat keinen gültigen Zahlenwert geliefert. "
                         "Bitte prüfen, ob die Entitäts-ID korrekt ist und einen numerischen Zustand hat.")
    return value
