from typing import TYPE_CHECKING, cast

import bpy

if TYPE_CHECKING:
    from .preferences.addon_preferences import XRAYSELPreferences


def get_addon_package() -> str:
    """Return the name of the addon package."""
    assert isinstance(__package__, str)
    return __package__


def get_preferences() -> "XRAYSELPreferences":
    assert isinstance(__package__, str)
    return cast("XRAYSELPreferences", bpy.context.preferences.addons[__package__].preferences)
