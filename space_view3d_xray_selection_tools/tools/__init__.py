import bpy

from . import tools_dummy, tools_main, tools_utils


def reload_tools(_pg: bpy.types.PropertyGroup, _context: bpy.types.Context) -> None:
    """
    Reloads tools by unregistering and registering them again.
    This is used to update tool groups and position in toolbar.
    """
    tools_utils.reset_active_tool()

    tools_main.unregister()
    tools_dummy.unregister()

    tools_main.register()
    tools_dummy.register()


def update_keymaps_of_tools(_pg: bpy.types.PropertyGroup, _context: bpy.types.Context) -> None:
    """
    Apply changes of addon preferences keymap collection property to keyconfig tool keymaps.
    """
    tools_main.unregister()
    tools_dummy.unregister()

    tools_main.register()
    tools_dummy.register()


def register() -> None:
    tools_main.register()
    tools_dummy.register()


def unregister() -> None:
    tools_utils.reset_active_tool()
    tools_main.unregister()
    tools_dummy.unregister()
