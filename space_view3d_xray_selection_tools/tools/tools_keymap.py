from typing import TYPE_CHECKING, Literal, cast

import bpy

from .. import addon_info
from ..types import WorkSpaceToolKeymapItem

if TYPE_CHECKING:
    from ..preferences.properties.keymaps_props import XRAYSELToolKmiPG

FALLBACK_KEYMAP_DICT = {  # keymap_name, (keymap_item_idname, tool_type)
    "3D View Tool: Object, Select Box X-Ray (fallback)": ("object.select_box_xray", "BOX"),
    "3D View Tool: Object, Select Circle X-Ray (fallback)": ("object.select_circle_xray", "CIRCLE"),
    "3D View Tool: Object, Select Lasso X-Ray (fallback)": ("object.select_lasso_xray", "LASSO"),
    "3D View Tool: Edit Mesh, Select Box X-Ray (fallback)": ("mesh.select_box_xray", "BOX"),
    "3D View Tool: Edit Mesh, Select Circle X-Ray (fallback)": ("mesh.select_circle_xray", "CIRCLE"),
    "3D View Tool: Edit Mesh, Select Lasso X-Ray (fallback)": ("mesh.select_lasso_xray", "LASSO"),
}

DUMMY_FALLBACK_KEYMAP_DICT = {  # keymap_name, (keymap_item_idname, tool_type)
    "3D View Tool: Edit Curve, Select Box X-Ray (fallback)": ("view3d.select_box", "BOX"),
    "3D View Tool: Edit Curve, Select Circle X-Ray (fallback)": ("view3d.select_circle", "CIRCLE"),
    "3D View Tool: Edit Curve, Select Lasso X-Ray (fallback)": ("view3d.select_lasso", "LASSO"),
    "3D View Tool: Edit Armature, Select Box X-Ray (fallback)": ("view3d.select_box", "BOX"),
    "3D View Tool: Edit Armature, Select Circle X-Ray (fallback)": ("view3d.select_circle", "CIRCLE"),
    "3D View Tool: Edit Armature, Select Lasso X-Ray (fallback)": ("view3d.select_lasso", "LASSO"),
    "3D View Tool: Edit Metaball, Select Box X-Ray (fallback)": ("view3d.select_box", "BOX"),
    "3D View Tool: Edit Metaball, Select Circle X-Ray (fallback)": ("view3d.select_circle", "CIRCLE"),
    "3D View Tool: Edit Metaball, Select Lasso X-Ray (fallback)": ("view3d.select_lasso", "LASSO"),
    "3D View Tool: Edit Lattice, Select Box X-Ray (fallback)": ("view3d.select_box", "BOX"),
    "3D View Tool: Edit Lattice, Select Circle X-Ray (fallback)": ("view3d.select_circle", "CIRCLE"),
    "3D View Tool: Edit Lattice, Select Lasso X-Ray (fallback)": ("view3d.select_lasso", "LASSO"),
    "3D View Tool: Pose, Select Box X-Ray (fallback)": ("view3d.select_box", "BOX"),
    "3D View Tool: Pose, Select Circle X-Ray (fallback)": ("view3d.select_circle", "CIRCLE"),
    "3D View Tool: Pose, Select Lasso X-Ray (fallback)": ("view3d.select_lasso", "LASSO"),
}


def add_fallback_keymap(keymap_dict: dict[str, tuple[str, ...]]) -> None:
    """
    Create empty fallback keymap for every tool.
    """
    # https://developer.blender.org/rBc9d9bfa84ad
    kc = bpy.context.window_manager.keyconfigs.default
    for keymap_name in keymap_dict.keys():
        kc.keymaps.new(name=keymap_name, space_type='VIEW_3D', region_type='WINDOW', tool=True)


def add_fallback_keymap_items(keymap_dict: dict[str, tuple[str, ...]]) -> None:
    """
    Fill tool fallback keymaps with keymap items from addon preferences.
    """
    # keyconfig.preferences isn't available at blender startup if bpy.app.version < (4, 0, 0)
    kc = bpy.context.window_manager.keyconfigs.active
    if kc is None or kc.preferences is None:  # pyright: ignore[reportUnnecessaryComparison]
        select_mouse = addon_info.get_preferences().select_mouse
        rmb_action = addon_info.get_preferences().rmb_action
    else:
        select_mouse = addon_info.get_preferences().select_mouse = cast(
            Literal['LEFT', 'RIGHT'],
            kc.preferences.select_mouse,  # pyright: ignore [reportAttributeAccessIssue]
        )
        rmb_action = addon_info.get_preferences().rmb_action = cast(
            Literal['TWEAK', 'FALLBACK_TOOL'],
            kc.preferences.rmb_action,  # pyright: ignore [reportAttributeAccessIssue]
        )

    kc = bpy.context.window_manager.keyconfigs.addon
    addon_prefs_keymaps = addon_info.get_preferences().keymaps.tools_keymaps

    if select_mouse == 'RIGHT' and rmb_action == 'FALLBACK_TOOL':
        event_type = 'RIGHTMOUSE'
    else:
        event_type = 'LEFTMOUSE'

    for keymap_name, (keymap_item_idname, tool) in keymap_dict.items():
        km = kc.keymaps.new(name=keymap_name, space_type='VIEW_3D', region_type='WINDOW', tool=True)
        addon_prefs_keymap = addon_prefs_keymaps[tool]
        addon_prefs_keymap_items = addon_prefs_keymap.kmis

        for props_group in reversed(addon_prefs_keymap_items.values()):  # type: ignore
            kmi_props = cast("XRAYSELToolKmiPG", props_group)

            if kmi_props["active"]:
                kmi = km.keymap_items.new(
                    keymap_item_idname,
                    event_type,
                    'CLICK_DRAG',
                    ctrl=kmi_props["ctrl"],
                    shift=kmi_props["shift"],
                    alt=kmi_props["alt"],
                )
                if kmi_props["name"] != 'DEF':
                    kmi.properties.mode = kmi_props["name"]  # pyright: ignore [reportAttributeAccessIssue]

                if keymap_item_idname in {
                    "mesh.select_circle_xray",
                    "object.select_circle_xray",
                    "view3d.select_circle",
                }:
                    kmi.properties.wait_for_input = False  # pyright: ignore [reportAttributeAccessIssue]


def remove_fallback_keymap_items(keymap_dict: dict[str, tuple[str, ...]]) -> None:
    """
    Remove tool fallback keymap items.
    """
    for keymap_name in keymap_dict.keys():
        kc = bpy.context.window_manager.keyconfigs.addon
        km = kc.keymaps.get(keymap_name)
        if km is not None:
            for kmi in km.keymap_items:
                km.keymap_items.remove(kmi)


def populate_preferences_keymaps_of_tools() -> None:
    """
    Fill preferences keymaps collection property from template.
    """
    addon_prefs_tool_keymaps = addon_info.get_preferences().keymaps.tools_keymaps
    default_addon_prefs_keymap_dict = {
        "DEF": {
            "description": "Active Mode",
            "icon": "PROPERTIES",
            "active": True,
            "shift": False,
            "ctrl": False,
            "alt": False,
        },
        "SET": {
            "description": "Set",
            "icon": "SELECT_SET",
            "active": False,
            "shift": False,
            "ctrl": False,
            "alt": False,
        },
        "ADD": {
            "description": "Extend",
            "icon": "SELECT_EXTEND",
            "active": True,
            "shift": True,
            "ctrl": False,
            "alt": False,
        },
        "SUB": {
            "description": "Subtract",
            "icon": "SELECT_SUBTRACT",
            "active": True,
            "shift": False,
            "ctrl": True,
            "alt": False,
        },
        "XOR": {
            "description": "Difference",
            "icon": "SELECT_DIFFERENCE",
            "active": False,
            "shift": False,
            "ctrl": False,
            "alt": True,
        },
        "AND": {
            "description": "Intersect",
            "icon": "SELECT_INTERSECT",
            "active": True,
            "shift": True,
            "ctrl": True,
            "alt": False,
        },
    }

    for tool in {"BOX", "LASSO", "CIRCLE"}:
        addon_prefs_tool_keymap = addon_prefs_tool_keymaps.get(tool)
        if addon_prefs_tool_keymap is None:
            addon_prefs_tool_keymap = addon_prefs_tool_keymaps.add()
            addon_prefs_tool_keymap["name"] = tool

        keymap_dict = default_addon_prefs_keymap_dict
        # Remove XOR and AND from circle tools
        if tool == "CIRCLE":
            keymap_dict.pop("XOR")
            keymap_dict.pop("AND")

        kmis = addon_prefs_tool_keymap.kmis
        for mode, props in keymap_dict.items():
            if mode not in kmis:
                kmi = kmis.add()
                kmi["name"] = mode
                kmi["description"] = props["description"]
                kmi["icon"] = props["icon"]
                kmi["active"] = props["active"]
                kmi["shift"] = props["shift"]
                kmi["ctrl"] = props["ctrl"]
                kmi["alt"] = props["alt"]


def get_tool_keymap_from_preferences(bl_operator: str) -> tuple[WorkSpaceToolKeymapItem, ...]:
    """
    Get tool keymap items from addon preferences keymap collection property.
    """
    addon_prefs_tool_keymaps = addon_info.get_preferences().keymaps.tools_keymaps  # Collection of tools keymaps.
    tool = {
        "mesh.select_box_xray": "BOX",
        "object.select_box_xray": "BOX",
        "view3d.select_box": "BOX",
        "mesh.select_circle_xray": "CIRCLE",
        "object.select_circle_xray": "CIRCLE",
        "view3d.select_circle": "CIRCLE",
        "mesh.select_lasso_xray": "LASSO",
        "object.select_lasso_xray": "LASSO",
        "view3d.select_lasso": "LASSO",
    }[bl_operator]
    addon_prefs_tool_keymap = addon_prefs_tool_keymaps[tool]  # Collection of a tool KeymapItemGroups.
    addon_prefs_tool_keymap_items = addon_prefs_tool_keymap.kmis  # KeymapItems for a tool selection mode.

    bl_tool_keymap: list[WorkSpaceToolKeymapItem] = []  # Flattened KeymapItems for tool selection modes.
    for idname, props_group in addon_prefs_tool_keymap_items.items():  # type: ignore
        mode = cast(str, idname)
        kmi_props = cast("XRAYSELToolKmiPG", props_group)

        if kmi_props["active"]:
            kmi = (
                bl_operator,
                {
                    "type": 'LEFTMOUSE',
                    "value": 'CLICK_DRAG',
                    "shift": kmi_props["shift"],
                    "ctrl": kmi_props["ctrl"],
                    "alt": kmi_props["alt"],
                },
                {"properties": [("mode", mode)]},
            )
            if mode == "DEF":
                kmi[2]["properties"] = []

            if tool == "CIRCLE":
                kmi[2]["properties"].append(("wait_for_input", False))  # pyright: ignore [reportArgumentType]

            bl_tool_keymap.append(kmi)

    bl_tool_keymap.reverse()
    return tuple(bl_tool_keymap)
