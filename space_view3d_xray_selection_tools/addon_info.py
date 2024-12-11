from typing import TYPE_CHECKING

import bpy

if TYPE_CHECKING:
    # Only imported for type-checking
    from .ui_preferences import XRAYSELPreferences


def get_preferences() -> "XRAYSELPreferences":
    return bpy.context.preferences.addons[__package__].preferences
