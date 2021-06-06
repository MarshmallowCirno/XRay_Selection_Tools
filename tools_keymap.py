from .preferences import get_preferences


def populate_preferences_keymaps_of_tools():
    """Fill preferences keymaps collection property from template"""
    # keymaps_of_tools = collection of keymap (box, circle, lasso)
    # keymap = collection of kmi
    keymaps = get_preferences().keymaps_of_tools
    tools = ("BOX", "LASSO", "CIRCLE")
    default_keymap = {
        "DEF": {"description": "Active Mode", "icon": "PROPERTIES",
                "active": True, "shift": False, "ctrl": False, "alt": False},
        "SET": {"description": "Set", "icon": "SELECT_SET",
                "active": False, "shift": False, "ctrl": False, "alt": False},
        "ADD": {"description": "Extend", "icon": "SELECT_EXTEND",
                "active": True, "shift": True, "ctrl": False, "alt": False},
        "SUB": {"description": "Subtract", "icon": "SELECT_SUBTRACT",
                "active": True, "shift": False, "ctrl": True, "alt": False},
        "XOR": {"description": "Difference", "icon": "SELECT_DIFFERENCE",
                "active": False, "shift": False, "ctrl": False, "alt": True},
        "AND": {"description": "Intersect", "icon": "SELECT_INTERSECT",
                "active": True, "shift": True, "ctrl": True, "alt": False}
    }
    for tool in tools:
        keymap = keymaps.get(tool, None)
        if keymap is None:
            keymap = keymaps.add()
            keymap["name"] = tool
        # remove XOR and AND from circle tools
        if tool == "CIRCLE":
            default_keymap.pop("XOR")
            default_keymap.pop("AND")

        kmis = keymap.kmis
        for key, values in default_keymap.items():
            if key not in kmis.keys():
                kmi = kmis.add()
                kmi["name"] = key
                kmi["description"] = values["description"]
                kmi["icon"] = values["icon"]
                kmi["active"] = values["active"]
                kmi["shift"] = values["shift"]
                kmi["ctrl"] = values["ctrl"]
                kmi["alt"] = values["alt"]


def get_keymap_of_tool_from_preferences(bl_operator):
    """Get tool keymap from preferences collection property"""
    # keymaps_of_tools = collection of keymap (box, circle, lasso)
    # keymap_of_tool = collection of kmi
    keymaps = get_preferences().keymaps_of_tools
    operator_tool = {
        "mesh.select_box_xray": "BOX",
        "object.select_box_xray": "BOX",
        "view3d.select_box": "BOX",
        "mesh.select_circle_xray": "CIRCLE",
        "object.select_circle_xray": "CIRCLE",
        "view3d.select_circle": "CIRCLE",
        "mesh.select_lasso_xray": "LASSO",
        "object.select_lasso_xray": "LASSO",
        "view3d.select_lasso": "LASSO"
    }
    tool = operator_tool[bl_operator]
    keymap = keymaps[tool]
    kmis = keymap.kmis

    keyconfig_kmis = []
    for key, values in kmis.items():
        if values["active"]:
            kmi = (
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
            if key == "DEF":
                kmi[2]["properties"] = []

            if tool == "CIRCLE":
                kmi[2]["properties"].append(("wait_for_input", False))

            keyconfig_kmis.append(kmi)

    keyconfig_kmis.reverse()
    keyconfig_kmis = tuple(keyconfig_kmis)
    return keyconfig_kmis


def update_keymaps_of_tools(self, context):
    from .tools import unregister as unregister_tools
    from .tools_dummy import unregister as unregister_tools_dummy
    from .tools import register as register_tools
    from .tools_dummy import register as register_tools_dummy

    unregister_tools()
    unregister_tools_dummy()
    register_tools()
    register_tools_dummy()
