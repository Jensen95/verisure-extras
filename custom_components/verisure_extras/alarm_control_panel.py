# ABOUTME: Wrapper alarm_control_panel that arms and disarms the Verisure alarm without a code.
# ABOUTME: Mirrors the source alarm's state and injects the stored PIN into service calls.
from __future__ import annotations

from homeassistant.components.alarm_control_panel import (
    ATTR_CODE,
    DOMAIN as ALARM_DOMAIN,
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
    AlarmControlPanelState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import CONF_ALARM_ENTITY, CONF_PIN, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the wrapper alarm entity."""
    async_add_entities([VerisureExtrasAlarm(entry)])


class VerisureExtrasAlarm(AlarmControlPanelEntity):
    """Alarm entity that needs no code from the caller."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_should_poll = False
    _attr_supported_features = (
        AlarmControlPanelEntityFeature.ARM_HOME
        | AlarmControlPanelEntityFeature.ARM_AWAY
    )
    _attr_code_arm_required = False
    _attr_code_format = None

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the entity from a config entry."""
        self._entry = entry
        self._source_entity_id: str = entry.data[CONF_ALARM_ENTITY]
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Verisure Alarm (no PIN)",
            manufacturer="Verisure Extras",
        )

    async def async_added_to_hass(self) -> None:
        """Start following the source alarm."""
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, [self._source_entity_id], self._handle_source_event
            )
        )
        self._update_from_source()

    @callback
    def _handle_source_event(self, event: Event[EventStateChangedData]) -> None:
        """Handle a state change of the source alarm."""
        self._update_from_source()
        self.async_write_ha_state()

    @callback
    def _update_from_source(self) -> None:
        """Copy state and changed_by from the source entity."""
        source = self.hass.states.get(self._source_entity_id)
        if source is None or source.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            self._attr_available = False
            self._attr_alarm_state = None
            self._attr_changed_by = None
            return
        try:
            self._attr_alarm_state = AlarmControlPanelState(source.state)
        except ValueError:
            self._attr_available = False
            self._attr_alarm_state = None
            self._attr_changed_by = None
            return
        self._attr_available = True
        self._attr_changed_by = source.attributes.get("changed_by")

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        """Arm the source alarm in home mode using the stored PIN."""
        await self._async_call_source("alarm_arm_home", self._entry.data[CONF_PIN])

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        """Arm the source alarm in away mode using the stored PIN."""
        await self._async_call_source("alarm_arm_away", self._entry.data[CONF_PIN])

    async def _async_call_source(self, service: str, code: str) -> None:
        """Call an alarm_control_panel service on the source entity."""
        await self.hass.services.async_call(
            ALARM_DOMAIN,
            service,
            {ATTR_ENTITY_ID: self._source_entity_id, ATTR_CODE: code},
            blocking=True,
        )

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Disarm the source alarm using the stored PIN."""
        await self._async_call_source("alarm_disarm", self._entry.data[CONF_PIN])
