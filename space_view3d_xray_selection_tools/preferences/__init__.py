from .properties import XRAYSELPreferences, XRAYSELToolKeymapPG, XRAYSELToolKmiPG, XRAYSELToolMeDirectionProps
from ..addon_info import get_preferences
from ..tools.tools_keymap import populate_preferences_keymaps_of_tools


def populate_preferences_direction_properties():
    left = get_preferences().me_direction_properties.add()
    left.name = "RIGHT_TO_LEFT"
    left = get_preferences().me_direction_properties.add()
    left.name = "LEFT_TO_RIGHT"


CLASSES = (XRAYSELToolMeDirectionProps, XRAYSELToolKmiPG, XRAYSELToolKeymapPG, XRAYSELPreferences)


def register():
    from bpy.utils import register_class

    for cls in CLASSES:
        register_class(cls)

    populate_preferences_keymaps_of_tools()
    populate_preferences_direction_properties()


def unregister():
    get_preferences().me_direction_properties.clear()
    get_preferences().keymaps_of_tools.clear()

    from bpy.utils import unregister_class

    for cls in CLASSES:
        unregister_class(cls)
