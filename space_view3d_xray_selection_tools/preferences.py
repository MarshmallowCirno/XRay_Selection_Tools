import os
from typing import TYPE_CHECKING

import bpy

if TYPE_CHECKING:
    # Only imported for type-checking
    from .ui_preferences import XRAYSELPreferences


def get_addon_name():
    return os.path.basename(os.path.dirname(os.path.realpath(__file__)))


def get_preferences() -> "XRAYSELPreferences":
    return bpy.context.preferences.addons[__package__].preferences
