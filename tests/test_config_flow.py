# ABOUTME: Tests for the Verisure Extras config and options flows.
# ABOUTME: Uses a fake PIN (1234) that never matches a real alarm code.
import pytest
from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.verisure_extras.const import (
    CONF_ALARM_ENTITY,
    CONF_PIN,
    DOMAIN,
)

FAKE_PIN = "1234"


async def test_user_flow_creates_entry(hass: HomeAssistant) -> None:
    """A valid alarm entity and PIN create a config entry holding the PIN."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_ALARM_ENTITY: "alarm_control_panel.verisure_alarm",
            CONF_PIN: FAKE_PIN,
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Verisure Extras"
    assert result["data"] == {
        CONF_ALARM_ENTITY: "alarm_control_panel.verisure_alarm",
        CONF_PIN: FAKE_PIN,
    }


@pytest.mark.parametrize("bad_pin", ["123", "123456789", "12a4", "12 34", "abcd"])
async def test_user_flow_rejects_invalid_pin(
    hass: HomeAssistant, bad_pin: str
) -> None:
    """PINs must be 4-8 digits; anything else shows a form error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_ALARM_ENTITY: "alarm_control_panel.verisure_alarm",
            CONF_PIN: bad_pin,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_PIN: "invalid_pin"}

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_ALARM_ENTITY: "alarm_control_panel.verisure_alarm",
            CONF_PIN: FAKE_PIN,
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_user_flow_single_instance(hass: HomeAssistant) -> None:
    """A second config entry is refused."""
    MockConfigEntry(domain=DOMAIN, data={CONF_PIN: FAKE_PIN}).add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "single_instance_allowed"
