from .tools_dummy import register as register_dummy_tools, unregister as unregister_dummy_tools
from .tools_main import register as register_main_tools, unregister as unregister_main_tools
from .tools_utils import reset_active_tool


def reload_tools(self, context):
    """
    Reloads tools by unregistering and registering them again.
    This is used to update tool groups and position in toolbar.
    """
    reset_active_tool()

    unregister_main_tools()
    unregister_dummy_tools()

    register_main_tools()
    register_dummy_tools()


def update_keymaps_of_tools(self, context) -> None:
    """
    Apply changes of addon preferences keymap collection property to keyconfig tool keymaps.
    """
    unregister_main_tools()
    unregister_dummy_tools()

    register_main_tools()
    register_dummy_tools()


def register() -> None:
    tools_main.register()
    tools_dummy.register()


def unregister() -> None:
    tools_utils.reset_active_tool()
    tools_main.unregister()
    tools_dummy.unregister()
