import json
import logging
from typing import Callable, Optional, List, TypeVar, Dict, Any

from requests import Session
from modules.common import req

import jq

log = logging.getLogger(__name__)
T = TypeVar('T')
RequestFunction = Callable[[Session], T]


def template_post_request(url: str, token: str, mapping: Dict[str, str]) -> Any:
    template_parts = [f"\\\"{key}\\\": {{{{states('{value}')}}}}" for key, value in mapping.items()]
    template = f"{{\"template\": \"{{{', '.join(template_parts)}}}\" }}"
    log.info(f"sending query for template {template}")
    response = req.get_http_session().post(url, data=template, timeout=5, headers={'Authorization': f"Bearer {token}"}).text
    cleaned_response = response.replace('unknown', 'null')
    log.info(f"got response: {cleaned_response}")
    return json.loads(cleaned_response)


def parse_value(res: Dict[str, str], key: str, factor: float = 1.0) -> Optional[float]:
    value = res.get(key, None)
    if value is None:
        return None
    return float(value) * factor

def parse_values(res: Dict[str, str], keys: List[str], factor: float = 1.0) -> Optional[List[float]]:
    values = [res.get(key, None) for key in keys]
    if values.count(None):
        return None
    return [float(value) * factor for value in values]
