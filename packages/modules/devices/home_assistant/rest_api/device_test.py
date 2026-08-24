import json
from unittest.mock import Mock

import pytest
import requests_mock

from modules.common.fault_state import FaultState
from modules.common.simcount import SimCounter
from modules.devices.home_assistant.rest_api import bat, counter, inverter
from modules.devices.home_assistant.rest_api.config import (RestApi, RestApiBatConfiguration, RestApiBatSetup,
                                                            RestApiConfiguration, RestApiCounterConfiguration,
                                                            RestApiCounterSetup, RestApiInverterConfiguration,
                                                            RestApiInverterSetup)
from modules.devices.home_assistant.rest_api.device import create_device

TEMPLATE_URL = "http://sample_host:8123/api/template"


@pytest.fixture
def mock_value_store(monkeypatch) -> Mock:
    mock_value_store = Mock()
    mock_value_store_factory = Mock(return_value=mock_value_store)
    monkeypatch.setattr(bat, "get_bat_value_store", mock_value_store_factory)
    monkeypatch.setattr(counter, "get_counter_value_store", mock_value_store_factory)
    monkeypatch.setattr(inverter, "get_inverter_value_store", mock_value_store_factory)
    return mock_value_store


@pytest.fixture(autouse=True)
def mock_sim_counter(monkeypatch) -> Mock:
    mock = Mock(return_value=(0, 0))
    monkeypatch.setattr(SimCounter, "sim_count", mock)
    return mock


@pytest.fixture(autouse=True)
def mock_fault_state(monkeypatch) -> None:
    monkeypatch.setattr(FaultState, "store_error", Mock())


def device_config() -> RestApi:
    return RestApi(configuration=RestApiConfiguration(url="http://sample_host:8123", token="sample_token"))


def test_all_components_are_queried_with_a_single_request(mock_value_store: Mock,
                                                          requests_mock: requests_mock.Mocker):
    # setup
    requests_mock.post(TEMPLATE_URL, text=json.dumps({
        "bat_1_power": 500, "bat_1_soc": 80,
        "counter_2_power": 1000,
        "inverter_3_power": 2000,
    }))
    device = create_device(device_config())
    device.add_component(RestApiBatSetup(
        id=1, configuration=RestApiBatConfiguration(entity_power="sensor.bat", entity_soc="sensor.soc")))
    device.add_component(RestApiCounterSetup(
        id=2, configuration=RestApiCounterConfiguration(entity_power="sensor.counter")))
    device.add_component(RestApiInverterSetup(
        id=3, configuration=RestApiInverterConfiguration(entity_power="sensor.pv")))

    # execution
    device.update()

    # evaluation
    assert requests_mock.call_count == 1
    request = requests_mock.request_history[0]
    assert request.headers["Authorization"] == "Bearer sample_token"
    template = request.json()["template"]
    for entity in ("sensor.bat", "sensor.soc", "sensor.counter", "sensor.pv"):
        assert f'states("{entity}")' in template
    assert len(mock_value_store.set.mock_calls) == 3


@pytest.mark.parametrize("component_config,expected_power", [
    pytest.param(RestApiBatSetup(id=1, configuration=RestApiBatConfiguration(entity_power="sensor.x")),
                 42.0, id="bat"),
    pytest.param(RestApiCounterSetup(id=1, configuration=RestApiCounterConfiguration(entity_power="sensor.x")),
                 42.0, id="counter"),
    pytest.param(RestApiInverterSetup(id=1, configuration=RestApiInverterConfiguration(entity_power="sensor.x")),
                 -42.0, id="inverter"),
])
def test_power_is_parsed(mock_value_store: Mock, requests_mock: requests_mock.Mocker, component_config,
                         expected_power: float):
    # setup
    key = f"{component_config.type}_1_power"
    requests_mock.post(TEMPLATE_URL, text=json.dumps({key: 42}))
    device = create_device(device_config())
    device.add_component(component_config)

    # execution
    device.update()

    # evaluation
    assert mock_value_store.set.call_args[0][0].power == expected_power


def test_counter_currents_and_voltages_are_not_scaled(mock_value_store: Mock, requests_mock: requests_mock.Mocker):
    # setup
    requests_mock.post(TEMPLATE_URL, text=json.dumps({
        "counter_1_power": 3450,
        "counter_1_current_l1": 5, "counter_1_current_l2": 6, "counter_1_current_l3": 7,
        "counter_1_voltage_l1": 230, "counter_1_voltage_l2": 231, "counter_1_voltage_l3": 232,
    }))
    device = create_device(device_config())
    device.add_component(RestApiCounterSetup(id=1, configuration=RestApiCounterConfiguration(
        entity_power="sensor.power",
        entity_current_l1="sensor.c1", entity_current_l2="sensor.c2", entity_current_l3="sensor.c3",
        entity_voltage_l1="sensor.v1", entity_voltage_l2="sensor.v2", entity_voltage_l3="sensor.v3")))

    # execution
    device.update()

    # evaluation
    state = mock_value_store.set.call_args[0][0]
    assert state.currents == [5, 6, 7]
    assert state.voltages == [230, 231, 232]


def test_kw_unit_is_converted_to_watt(mock_value_store: Mock, requests_mock: requests_mock.Mocker):
    # setup
    requests_mock.post(TEMPLATE_URL, text=json.dumps({"counter_1_power": 3.45}))
    device = create_device(device_config())
    device.add_component(RestApiCounterSetup(id=1, configuration=RestApiCounterConfiguration(
        entity_power="sensor.power", unit_power="kW")))

    # execution
    device.update()

    # evaluation
    assert mock_value_store.set.call_args[0][0].power == 3450


def test_energy_entities_are_converted_from_kwh(mock_value_store: Mock, requests_mock: requests_mock.Mocker):
    # setup
    requests_mock.post(TEMPLATE_URL, text=json.dumps({
        "counter_1_power": 1000, "counter_1_imported": 12.5, "counter_1_exported": 3.25}))
    device = create_device(device_config())
    device.add_component(RestApiCounterSetup(id=1, configuration=RestApiCounterConfiguration(
        entity_power="sensor.power", entity_imported="sensor.imp", entity_exported="sensor.exp")))

    # execution
    device.update()

    # evaluation
    state = mock_value_store.set.call_args[0][0]
    assert state.imported == 12500
    assert state.exported == 3250


def test_bat_power_from_charge_and_discharge_entities(mock_value_store: Mock, requests_mock: requests_mock.Mocker):
    # setup
    requests_mock.post(TEMPLATE_URL, text=json.dumps({"bat_1_charge": 0, "bat_1_discharge": 700}))
    device = create_device(device_config())
    device.add_component(RestApiBatSetup(id=1, configuration=RestApiBatConfiguration(
        entity_charge="sensor.charge", entity_discharge="sensor.discharge")))

    # execution
    device.update()

    # evaluation
    assert mock_value_store.set.call_args[0][0].power == -700


def test_unavailable_entity_raises_fault_state(mock_value_store: Mock, requests_mock: requests_mock.Mocker,
                                               monkeypatch):
    # setup: der float-Filter rendert nicht-numerische Zustände als null
    requests_mock.post(TEMPLATE_URL, text=json.dumps({"counter_1_power": None}))
    store_error = Mock()
    monkeypatch.setattr(FaultState, "store_error", store_error)
    device = create_device(device_config())
    device.add_component(RestApiCounterSetup(
        id=1, configuration=RestApiCounterConfiguration(entity_power="sensor.power")))

    # execution
    device.update()

    # evaluation
    assert len(mock_value_store.set.mock_calls) == 0
    assert store_error.called


def test_missing_token_is_reported(mock_value_store: Mock, requests_mock: requests_mock.Mocker, monkeypatch):
    # setup
    requests_mock.post(TEMPLATE_URL, text="{}")
    store_error = Mock()
    monkeypatch.setattr(FaultState, "store_error", store_error)
    device = create_device(RestApi(configuration=RestApiConfiguration(url="http://sample_host:8123")))
    device.add_component(RestApiCounterSetup(
        id=1, configuration=RestApiCounterConfiguration(entity_power="sensor.power")))

    # execution
    device.update()

    # evaluation
    assert requests_mock.call_count == 0
    assert store_error.called
