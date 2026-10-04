# ABOUTME: Config flow for Verisure Extras: picks the source alarm and stores the PIN.
# ABOUTME: The PIN is only ever kept in the config entry data, never logged.
from __future__ import annotations

import re
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_ALARM_ENTITY,
    CONF_ALLOW_DISARM_WITHOUT_PIN,
    CONF_PIN,
    DEFAULT_ALARM_ENTITY,
    DEFAULT_ALLOW_DISARM_WITHOUT_PIN,
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

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(
            CONF_ALLOW_DISARM_WITHOUT_PIN, default=DEFAULT_ALLOW_DISARM_WITHOUT_PIN
        ): bool,
        vol.Optional(CONF_PIN): TextSelector(
            TextSelectorConfig(type=TextSelectorType.PASSWORD)
        ),
    }
)


class VerisureExtrasConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Verisure Extras."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlowWithReload:
        """Return the options flow handler."""
        return VerisureExtrasOptionsFlow()

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


class VerisureExtrasOptionsFlow(OptionsFlowWithReload):
    """Handle the options of Verisure Extras."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Change passwordless disarm and optionally replace the PIN."""
        errors: dict[str, str] = {}
        if user_input is not None:
            new_pin = user_input.pop(CONF_PIN, None)
            if new_pin and not PIN_PATTERN.fullmatch(new_pin):
                errors[CONF_PIN] = "invalid_pin"
            else:
                if new_pin:
                    self.hass.config_entries.async_update_entry(
                        self.config_entry,
                        data={**self.config_entry.data, CONF_PIN: new_pin},
                    )
                return self.async_create_entry(data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                OPTIONS_SCHEMA,
                {
                    CONF_ALLOW_DISARM_WITHOUT_PIN: self.config_entry.options.get(
                        CONF_ALLOW_DISARM_WITHOUT_PIN,
                        DEFAULT_ALLOW_DISARM_WITHOUT_PIN,
                    )
                },
            ),
            errors=errors,
        )
