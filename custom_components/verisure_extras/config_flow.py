# ABOUTME: Config flow for Verisure Extras: picks the source alarm and stores the PIN.
# ABOUTME: The PIN is only ever kept in the config entry data, never logged.
from __future__ import annotations

import re
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_ALARM_ENTITY,
    CONF_PIN,
    DEFAULT_ALARM_ENTITY,
    DOMAIN,
)

PIN_PATTERN = re.compile(r"\d{4,8}")

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ALARM_ENTITY, default=DEFAULT_ALARM_ENTITY): EntitySelector(
            EntitySelectorConfig(domain="alarm_control_panel")
        ),
        vol.Required(CONF_PIN): TextSelector(
            TextSelectorConfig(type=TextSelectorType.PASSWORD)
        ),
    }
)


class VerisureExtrasConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Verisure Extras."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for the source alarm entity and the PIN."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if PIN_PATTERN.fullmatch(user_input[CONF_PIN]):
                return self.async_create_entry(title="Verisure Extras", data=user_input)
            errors[CONF_PIN] = "invalid_pin"
        return self.async_show_form(
            step_id="user", data_schema=USER_SCHEMA, errors=errors
        )
