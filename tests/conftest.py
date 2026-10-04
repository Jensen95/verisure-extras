# ABOUTME: Shared pytest fixtures for the Verisure Extras tests.
# ABOUTME: Enables loading of custom integrations from custom_components.
import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.verisure_extras.const import (
    CONF_ALARM_ENTITY,
    CONF_PIN,
    DOMAIN,
)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading of custom integrations in every test."""
    yield


SOURCE_ENTITY = "alarm_control_panel.verisure_alarm"
FAKE_PIN = "1234"


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a config entry holding a fake PIN."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Verisure Extras",
        data={CONF_ALARM_ENTITY: SOURCE_ENTITY, CONF_PIN: FAKE_PIN},
    )


@pytest.fixture
async def init_integration(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> MockConfigEntry:
    """Set up the integration with a disarmed source alarm."""
    hass.states.async_set(
        SOURCE_ENTITY,
        "disarmed",
        {"changed_by": "Alice", "supported_features": 3},
    )
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    return mock_config_entry
