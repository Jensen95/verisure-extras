# ABOUTME: Tests for the Verisure Extras config and options flows.
# ABOUTME: Uses a fake PIN (1234) that never matches a real alarm code.
from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

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
