# ABOUTME: Tests for the PIN-less wrapper alarm_control_panel entity.
# ABOUTME: Source alarm services are mocked; the fake PIN 1234 is only used here.
import pytest
import voluptuous as vol
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.entity_platform import async_get_platforms
from pytest_homeassistant_custom_component.common import async_mock_service

from custom_components.verisure_extras.const import (
    CONF_ALLOW_DISARM_WITHOUT_PIN,
    DOMAIN,
)

from .conftest import FAKE_PIN, SOURCE_ENTITY

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
    """Unavailable, unknown or unrecognised source states are unavailable."""
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


def get_wrapper(hass: HomeAssistant):
    """Return the wrapper entity object.

    The wrapper and the source share the same service names, so the tests mock the
    source services and call the wrapper's methods directly instead of via services.
    """
    (platform,) = async_get_platforms(hass, DOMAIN)
    return platform.entities[ENTITY_ID]


@pytest.mark.parametrize("action", ["arm_home", "arm_away"])
async def test_arm_forwards_stored_pin(
    hass: HomeAssistant, init_integration, action: str
) -> None:
    """Arming without a code calls the source with the stored PIN."""
    calls = async_mock_service(hass, "alarm_control_panel", f"alarm_{action}")

    await getattr(get_wrapper(hass), f"async_alarm_{action}")()

    assert len(calls) == 1
    assert calls[0].data == {"entity_id": SOURCE_ENTITY, "code": FAKE_PIN}


async def test_disarm_uses_stored_pin_by_default(
    hass: HomeAssistant, init_integration
) -> None:
    """With passwordless disarm on (the default) the stored PIN is used."""
    calls = async_mock_service(hass, "alarm_control_panel", "alarm_disarm")

    await get_wrapper(hass).async_alarm_disarm()

    assert len(calls) == 1
    assert calls[0].data == {"entity_id": SOURCE_ENTITY, "code": FAKE_PIN}


@pytest.fixture
async def init_integration_pin_required(hass: HomeAssistant, mock_config_entry) -> None:
    """Set up with passwordless disarm turned off."""
    hass.states.async_set(SOURCE_ENTITY, "armed_away")
    mock_config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        mock_config_entry, options={CONF_ALLOW_DISARM_WITHOUT_PIN: False}
    )
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()


async def test_disarm_requires_user_code_when_pinless_disarm_off(
    hass: HomeAssistant, init_integration_pin_required
) -> None:
    """With passwordless disarm off the caller's code is forwarded."""
    assert hass.states.get(ENTITY_ID).attributes["code_format"] == "number"
    calls = async_mock_service(hass, "alarm_control_panel", "alarm_disarm")

    await get_wrapper(hass).async_alarm_disarm("9876")

    assert len(calls) == 1
    assert calls[0].data == {"entity_id": SOURCE_ENTITY, "code": "9876"}


async def test_disarm_without_code_rejected_when_pinless_disarm_off(
    hass: HomeAssistant, init_integration_pin_required
) -> None:
    """A missing code is refused and nothing is sent to the source."""
    calls = async_mock_service(hass, "alarm_control_panel", "alarm_disarm")

    with pytest.raises(ServiceValidationError) as err:
        await get_wrapper(hass).async_alarm_disarm()

    assert calls == []
    assert FAKE_PIN not in str(err.value)


@pytest.mark.parametrize("action", ["arm_home", "arm_away", "disarm"])
@pytest.mark.parametrize(
    "error",
    [
        HomeAssistantError(f"Wrong code {FAKE_PIN}"),
        ServiceValidationError(f"Invalid code {FAKE_PIN}"),
        vol.Invalid(f"expected code {FAKE_PIN}"),
    ],
)
async def test_source_error_does_not_leak_pin(
    hass: HomeAssistant,
    init_integration,
    caplog: pytest.LogCaptureFixture,
    action: str,
    error: Exception,
) -> None:
    """Errors from the source become HomeAssistantError without the PIN."""

    async def failing(call) -> None:
        raise error

    hass.services.async_register("alarm_control_panel", f"alarm_{action}", failing)

    with pytest.raises(HomeAssistantError) as err:
        await getattr(get_wrapper(hass), f"async_alarm_{action}")()

    assert FAKE_PIN not in str(err.value)
    assert FAKE_PIN not in repr(err.value)
    assert FAKE_PIN not in repr(err.value.translation_placeholders)
    assert err.value.__cause__ is None
    assert err.value.__suppress_context__
    assert FAKE_PIN not in caplog.text
