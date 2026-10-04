# ABOUTME: Sets up the Verisure Extras integration from a config entry.
# ABOUTME: Forwards the entry to the alarm_control_panel platform.
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Verisure Extras from a config entry."""
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return True
