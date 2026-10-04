# ABOUTME: Tests that diagnostics for Verisure Extras redact the stored PIN.
# ABOUTME: Uses the fake PIN 1234 and checks it appears nowhere in the output.
import json

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.components.diagnostics import (
    get_diagnostics_for_config_entry,
)

from .conftest import FAKE_PIN, SOURCE_ENTITY


async def test_diagnostics_redact_pin(
    hass: HomeAssistant, hass_client, init_integration
) -> None:
    """The PIN is redacted while other config data stays visible."""
    assert await async_setup_component(hass, "diagnostics", {})
    diagnostics = await get_diagnostics_for_config_entry(
        hass, hass_client, init_integration
    )

    assert diagnostics["entry"]["data"]["pin"] == "**REDACTED**"
    assert diagnostics["entry"]["data"]["alarm_entity"] == SOURCE_ENTITY
    assert FAKE_PIN not in json.dumps(diagnostics)
