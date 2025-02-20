from .. import addon_info
from ..tools import tools_keymap
from . import addon_preferences, properties


def populate_addon_preferences_direction_properties():
    left = addon_info.get_preferences().mesh_tools.direction_properties.add()
    left.name = 'RIGHT_TO_LEFT'
    left = addon_info.get_preferences().mesh_tools.direction_properties.add()
    left.name = 'LEFT_TO_RIGHT'


_classes = (
    properties.XRAYSELToolKeyMapItemPG,
    properties.XRAYSELToolKeyMapItemsPG,
    properties.XRAYSELToolMeDirectionProps,
    properties.XRAYSELMeshToolsPreferencesPG,
    properties.XRAYSELObjectToolsPreferencesPG,
    properties.XRAYSELKeymapsPreferencesPG,
    addon_preferences.XRAYSELPreferences,
)


def register():
    from bpy.utils import register_class  # pyright: ignore[reportUnknownVariableType]

    for cls in _classes:
        register_class(cls)

    tools_keymap.populate_addon_preferences_keymaps()
    populate_addon_preferences_direction_properties()


def unregister():
    addon_info.get_preferences().mesh_tools.direction_properties.clear()
    addon_info.get_preferences().keymaps.tool_keymaps.clear()

    from bpy.utils import unregister_class  # pyright: ignore[reportUnknownVariableType]

    for cls in _classes:
        unregister_class(cls)
