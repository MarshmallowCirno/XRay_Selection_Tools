from . import addon_preferences, properties
from .. import addon_info
from ..tools import tools_keymap


def populate_preferences_direction_properties():
    left = addon_info.get_preferences().mesh_tools.directions_properties.add()
    left.name = "RIGHT_TO_LEFT"
    left = addon_info.get_preferences().mesh_tools.directions_properties.add()
    left.name = "LEFT_TO_RIGHT"


CLASSES = (
    properties.XRAYSELToolKmiPG,
    properties.XRAYSELToolKeymapPG,
    properties.XRAYSELToolMeDirectionProps,
    properties.XRAYSELMeshToolsPreferencesPG,
    properties.XRAYSELObjectToolsPreferencesPG,
    properties.XRAYSELKeymapsPreferencesPG,
    addon_preferences.XRAYSELPreferences,
)


def register():
    from bpy.utils import register_class

    for cls in CLASSES:
        register_class(cls)

    tools_keymap.populate_preferences_keymaps_of_tools()
    populate_preferences_direction_properties()


def unregister():
    addon_info.get_preferences().mesh_tools.directions_properties.clear()
    addon_info.get_preferences().keymaps.tools_keymaps.clear()

    from bpy.utils import unregister_class

    for cls in CLASSES:
        unregister_class(cls)
