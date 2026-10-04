# Verisure Extras

A small Home Assistant custom integration that complements the built-in
[Verisure](https://www.home-assistant.io/integrations/verisure/) integration.

The built-in alarm entity (`alarm_control_panel.verisure_alarm`) needs the numeric PIN
for every arm and disarm. Verisure Extras stores the PIN once and exposes a wrapper
alarm entity, **Verisure Alarm (no PIN)**, that needs no code. Scripts, dashboards and
automations can arm and disarm without ever seeing the PIN.

## Features

- Wrapper `alarm_control_panel` supporting `arm_home` and `arm_away`, no code needed.
- State and `changed_by` mirror the source alarm. The wrapper is `unavailable` when the
  source is unavailable, unknown or missing.
- Options: allow disarm without a code (default on), and change the stored PIN.
  With passwordless disarm off, the wrapper asks for a code on disarm and forwards that
  code to the source.
- Own device, single instance, diagnostics with the PIN redacted.

## Installation

### HACS (custom repository)

1. HACS, three-dots menu, **Custom repositories**.
2. Add `https://github.com/Jensen95/verisure-extras` as type **Integration**.
3. Download, then restart Home Assistant.

Note: HACS cannot use private GitHub repositories ("Private GitHub repositories can not
be used with HACS at all"). The repository must be public for this route; otherwise
copy `custom_components/verisure_extras` into your config directory manually.

### Manual

Copy `custom_components/verisure_extras` into `<config>/custom_components/` and restart.

## Setup

Settings, Devices & services, Add integration, **Verisure Extras**. Pick the source
alarm entity (default `alarm_control_panel.verisure_alarm`) and enter the PIN (4 to 8
digits).

## Security notes

- The PIN is stored **unencrypted** in `.storage/core.config_entries`, like any Home
  Assistant config entry. Anyone with HA admin access, file access to the config
  directory, or a backup can read it.
- The PIN is never written to logs, entity attributes, state, diagnostics or error
  messages by this integration. Errors from the source alarm are replaced with a generic
  message because they could echo the code.
- Passwordless disarm is a trade-off: anyone who can call services on the wrapper entity
  (any dashboard user, voice assistant, or automation) can disarm the alarm. Turn off
  **Allow disarm without a code** in the options if you do not want that; arming stays
  passwordless.
- Do not expose the wrapper entity to voice assistants or cloud services unless you
  accept that risk.

## Development

```bash
pip install -r requirements_test.txt
pytest
ruff check . && ruff format --check .
```

Tested against Home Assistant core 2026.9.4 with Python 3.14.

## License

MIT
