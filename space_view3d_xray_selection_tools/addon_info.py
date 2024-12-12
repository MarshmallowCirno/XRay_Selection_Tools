from typing import TYPE_CHECKING

import bpy

if TYPE_CHECKING:
    # Only imported for type-checking
    from .preferences.properties import XRAYSELPreferences


def get_addon_package() -> str:
    """Return the name of the addon package."""
    return __package__


def get_preferences() -> "XRAYSELPreferences":
    return bpy.context.preferences.addons[__package__].preferences
