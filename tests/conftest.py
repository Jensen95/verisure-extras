# ABOUTME: Shared pytest fixtures for the Verisure Extras tests.
# ABOUTME: Enables loading of custom integrations from custom_components.
import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading of custom integrations in every test."""
    yield
