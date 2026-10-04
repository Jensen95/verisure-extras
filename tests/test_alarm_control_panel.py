# ABOUTME: Tests for the PIN-less wrapper alarm_control_panel entity.
# ABOUTME: Source alarm services are mocked; the fake PIN 1234 is only used here.
import pytest
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant

from .conftest import SOURCE_ENTITY

ENTITY_ID = "alarm_control_panel.verisure_alarm_no_pin"


async def test_mirrors_source_state_and_changed_by(
    hass: HomeAssistant, init_integration
) -> None:
    """The wrapper starts with the source state and follows its changes."""
    state = hass.states.get(ENTITY_ID)
    assert state is not None
    assert state.state == "disarmed"
    assert state.attributes["changed_by"] == "Alice"

    hass.states.async_set(SOURCE_ENTITY, "armed_away", {"changed_by": "Bob"})
    await hass.async_block_till_done()

    state = hass.states.get(ENTITY_ID)
    assert state.state == "armed_away"
    assert state.attributes["changed_by"] == "Bob"


@pytest.mark.parametrize("source_state", ["unavailable", "unknown", "garbage"])
async def test_unavailable_when_source_unavailable(
    hass: HomeAssistant, init_integration, source_state: str
) -> None:
    """Unavailable, unknown or unrecognised source states make the wrapper unavailable."""
    hass.states.async_set(SOURCE_ENTITY, source_state)
    await hass.async_block_till_done()

    assert hass.states.get(ENTITY_ID).state == STATE_UNAVAILABLE


async def test_unavailable_when_source_removed_and_recovers(
    hass: HomeAssistant, init_integration
) -> None:
    """A removed source makes the wrapper unavailable until it returns."""
    hass.states.async_remove(SOURCE_ENTITY)
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).state == STATE_UNAVAILABLE

    hass.states.async_set(SOURCE_ENTITY, "armed_home")
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).state == "armed_home"


async def test_missing_source_at_startup_is_unavailable(
    hass: HomeAssistant, mock_config_entry
) -> None:
    """If the source does not exist yet the wrapper starts unavailable."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert hass.states.get(ENTITY_ID).state == STATE_UNAVAILABLE


async def test_entity_has_own_device_and_no_code(
    hass: HomeAssistant, init_integration, device_registry, entity_registry
) -> None:
    """The entity advertises arm_home/arm_away, no code, and has its own device."""
    state = hass.states.get(ENTITY_ID)
    assert state.attributes["supported_features"] == 3
    assert state.attributes["code_format"] is None
    assert state.attributes["code_arm_required"] is False

    entry = entity_registry.async_get(ENTITY_ID)
    assert entry.unique_id == init_integration.entry_id
    device = device_registry.async_get(entry.device_id)
    assert device.name == "Verisure Alarm (no PIN)"
