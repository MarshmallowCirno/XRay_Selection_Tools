from .preferences import get_preferences


def populate_prefs_tools_keymap():
    """Fill preferences keymap collection property from template"""
    prefs_prop = get_preferences().tools_keymap
    default_keymap = {
        "SET": {"description": "Set", "icon": "SELECT_SET",
                "active": True, "shift": False, "ctrl": False, "alt": False},
        "ADD": {"description": "Extend", "icon": "SELECT_EXTEND",
                "active": True, "shift": True, "ctrl": False, "alt": False},
        "SUB": {"description": "Subtract", "icon": "SELECT_SUBTRACT",
                "active": True, "shift": False, "ctrl": True, "alt": False},
        "XOR": {"description": "Difference", "icon": "SELECT_DIFFERENCE",
                "active": False, "shift": False, "ctrl": False, "alt": True},
        "AND": {"description": "Intersect", "icon": "SELECT_INTERSECT",
                "active": True, "shift": True, "ctrl": True, "alt": False}
    }

    for key, values in default_keymap.items():
        if key not in prefs_prop.keys():
            item = prefs_prop.add()
            item["name"] = key
            item["description"] = values["description"]
            item["icon"] = values["icon"]
            item["active"] = values["active"]
            item["shift"] = values["shift"]
            item["ctrl"] = values["ctrl"]
            item["alt"] = values["alt"]


def get_tool_keymap_from_prefs(bl_operator):
    """Get tool keymap from preferences collection property"""
    prefs_prop = get_preferences().tools_keymap

    if bl_operator in {"mesh.select_circle_xray", "object.select_circle_xray",
                       "view3d.select_circle"}:
        prefs_prop = dict(prefs_prop)
        prefs_prop.pop("XOR")
        prefs_prop.pop("AND")

    tool_keymap = []
    for key, values in prefs_prop.items():
        if values["active"]:
            tool_keymap.append(
                (
                    bl_operator,
                    {
                        "type": 'EVT_TWEAK_L',
                        "value": 'ANY',
                        "shift": values["shift"],
                        "ctrl": values["ctrl"],
                        "alt": values["alt"]
                    },
                    {"properties": [("mode", key)]}
                )
            )
    tool_keymap.reverse()
    tool_keymap = tuple(tool_keymap)
    return tool_keymap


def update_tools_keymaps(self, context):
    from .tools import unregister as unregister_tools
    from .tools_dummy import unregister as unregister_tools_dummy
    from .tools import register as register_tools
    from .tools_dummy import register as register_tools_dummy

    unregister_tools()
    unregister_tools_dummy()
    register_tools()
    register_tools_dummy()
