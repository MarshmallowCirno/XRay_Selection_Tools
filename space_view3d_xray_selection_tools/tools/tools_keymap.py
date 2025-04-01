from typing import TYPE_CHECKING, Any, Literal, NamedTuple, TypedDict, cast

import bpy

from .. import addon_info

if TYPE_CHECKING:
    from ..preferences.properties.keymaps_props import XRAYSELToolKeyMapItemPG


class _FallbackKeymapTemplate(NamedTuple):
    keymap_name: str
    operator_idname: str
    tool_type: Literal['BOX', 'CIRCLE', 'LASSO']


_MAIN_DATA = (
    ("3D View Tool: Object, Select Box X-Ray (fallback)", "object.select_box_xray", 'BOX'),
    ("3D View Tool: Object, Select Circle X-Ray (fallback)", "object.select_circle_xray", 'CIRCLE'),
    ("3D View Tool: Object, Select Lasso X-Ray (fallback)", "object.select_lasso_xray", 'LASSO'),
    ("3D View Tool: Edit Mesh, Select Box X-Ray (fallback)", "mesh.select_box_xray", 'BOX'),
    ("3D View Tool: Edit Mesh, Select Circle X-Ray (fallback)", "mesh.select_circle_xray", 'CIRCLE'),
    ("3D View Tool: Edit Mesh, Select Lasso X-Ray (fallback)", "mesh.select_lasso_xray", 'LASSO'),
)
_DUMMY_DATA = (
    ("3D View Tool: Edit Curve, Select Box X-Ray (fallback)", "view3d.select_box", 'BOX'),
    ("3D View Tool: Edit Curve, Select Circle X-Ray (fallback)", "view3d.select_circle", 'CIRCLE'),
    ("3D View Tool: Edit Curve, Select Lasso X-Ray (fallback)", "view3d.select_lasso", 'LASSO'),
    ("3D View Tool: Edit Armature, Select Box X-Ray (fallback)", "view3d.select_box", 'BOX'),
    ("3D View Tool: Edit Armature, Select Circle X-Ray (fallback)", "view3d.select_circle", 'CIRCLE'),
    ("3D View Tool: Edit Armature, Select Lasso X-Ray (fallback)", "view3d.select_lasso", 'LASSO'),
    ("3D View Tool: Edit Metaball, Select Box X-Ray (fallback)", "view3d.select_box", 'BOX'),
    ("3D View Tool: Edit Metaball, Select Circle X-Ray (fallback)", "view3d.select_circle", 'CIRCLE'),
    ("3D View Tool: Edit Metaball, Select Lasso X-Ray (fallback)", "view3d.select_lasso", 'LASSO'),
    ("3D View Tool: Edit Lattice, Select Box X-Ray (fallback)", "view3d.select_box", 'BOX'),
    ("3D View Tool: Edit Lattice, Select Circle X-Ray (fallback)", "view3d.select_circle", 'CIRCLE'),
    ("3D View Tool: Edit Lattice, Select Lasso X-Ray (fallback)", "view3d.select_lasso", 'LASSO'),
    ("3D View Tool: Pose, Select Box X-Ray (fallback)", "view3d.select_box", 'BOX'),
    ("3D View Tool: Pose, Select Circle X-Ray (fallback)", "view3d.select_circle", 'CIRCLE'),
    ("3D View Tool: Pose, Select Lasso X-Ray (fallback)", "view3d.select_lasso", 'LASSO'),
)
MAIN_FALLBACK_KEYMAP_TEMPLATES = tuple(map(_FallbackKeymapTemplate._make, _MAIN_DATA))
DUMMY_FALLBACK_KEYMAP_TEMPLATES = tuple(map(_FallbackKeymapTemplate._make, _DUMMY_DATA))


def add_fallback_keymaps(keymap_templates: tuple[_FallbackKeymapTemplate, ...]) -> None:
    """
    Add empty fallback keymaps from template to keyconfig.
    """
    # https://developer.blender.org/rBc9d9bfa84ad
    kc = bpy.context.window_manager.keyconfigs.default
    for template in keymap_templates:
        kc.keymaps.new(name=template.keymap_name, space_type='VIEW_3D', region_type='WINDOW', tool=True)


def add_fallback_keymap_items(keymap_templates: tuple[_FallbackKeymapTemplate, ...]) -> None:
    """
    Fill tool fallback keymaps with keymap items from the addon preferences.
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

    if select_mouse == 'RIGHT' and rmb_action == 'FALLBACK_TOOL':
        event_type = 'RIGHTMOUSE'
    else:
        event_type = 'LEFTMOUSE'

    kc = bpy.context.window_manager.keyconfigs.addon
    addon_prefs_kms = addon_info.get_preferences().keymaps.tool_keymaps

    for template in keymap_templates:
        km = kc.keymaps.new(name=template.keymap_name, space_type='VIEW_3D', region_type='WINDOW', tool=True)
        addon_prefs_km = addon_prefs_kms[template.tool_type]
        addon_prefs_km_items = addon_prefs_km.keymap_items

        for prop_group in reversed(addon_prefs_km_items.values()):  # type: ignore
            kmi_prefs = cast("XRAYSELToolKeyMapItemPG", prop_group)

            if not kmi_prefs["active"]:
                continue

            kmi = km.keymap_items.new(
                template.operator_idname,
                event_type,
                'CLICK_DRAG',
                ctrl=kmi_prefs["ctrl"],
                shift=kmi_prefs["shift"],
                alt=kmi_prefs["alt"],
                oskey=kmi_prefs["oskey"],
            )
            if kmi_prefs["name"] != 'DEF':
                kmi.properties.mode = kmi_prefs["name"]  # pyright: ignore [reportAttributeAccessIssue]
            if template.operator_idname in {
                "mesh.select_circle_xray",
                "object.select_circle_xray",
                "view3d.select_circle",
            }:
                kmi.properties.wait_for_input = False  # pyright: ignore [reportAttributeAccessIssue]


def clear_fallback_keymaps(keymap_templates: tuple[_FallbackKeymapTemplate, ...]) -> None:
    """
    Remove tool fallback keymap items.
    """
    kc = bpy.context.window_manager.keyconfigs.addon
    for template in keymap_templates:
        km = kc.keymaps.get(template.keymap_name)
        if km is not None:
            kc.keymaps.remove(km)


def populate_addon_preferences_keymaps() -> None:
    """
    Fill empty preferences keymaps collection properties with default values.
    """
    addon_prefs_kms = addon_info.get_preferences().keymaps.tool_keymaps
    default_km_config = {
        'DEF': {
            "description": "Active Mode",
            "icon": 'PROPERTIES',
            "active": True,
            "shift": False,
            "ctrl": False,
            "alt": False,
            "oskey": False,
        },
        'SET': {
            "description": "Set",
            "icon": 'SELECT_SET',
            "active": False,
            "shift": False,
            "ctrl": False,
            "alt": False,
            "oskey": False,
        },
        'ADD': {
            "description": "Extend",
            "icon": 'SELECT_EXTEND',
            "active": True,
            "shift": True,
            "ctrl": False,
            "alt": False,
            "oskey": False,
        },
        'SUB': {
            "description": "Subtract",
            "icon": 'SELECT_SUBTRACT',
            "active": True,
            "shift": False,
            "ctrl": True,
            "alt": False,
            "oskey": False,
        },
        'XOR': {
            "description": "Difference",
            "icon": 'SELECT_DIFFERENCE',
            "active": False,
            "shift": False,
            "ctrl": False,
            "alt": True,
            "oskey": False,
        },
        'AND': {
            "description": "Intersect",
            "icon": 'SELECT_INTERSECT',
            "active": True,
            "shift": True,
            "ctrl": True,
            "alt": False,
            "oskey": False,
        },
    }

    for tool_type in ('BOX', 'CIRCLE', 'LASSO'):
        addon_prefs_km = addon_prefs_kms.get(tool_type)
        if addon_prefs_km is None:
            addon_prefs_km = addon_prefs_kms.add()
            addon_prefs_km["name"] = tool_type

        km_items = addon_prefs_km.keymap_items
        for selection_mode, kmi_config in default_km_config.items():
            if tool_type == 'CIRCLE' and selection_mode in {'XOR', 'AND'}:
                continue

            if selection_mode not in km_items:
                kmi = km_items.add()
                kmi["name"] = selection_mode
            else:
                kmi = km_items[selection_mode]

            for key in ("description", "icon", "active", "shift", "ctrl", "alt", "oskey"):
                if key not in kmi:
                    kmi[key] = kmi_config[key]


class _WorkSpaceToolKeyMapItemEvent(TypedDict):
    type: str
    value: str
    shift: bool
    ctrl: bool
    alt: bool
    oskey: bool


class _WorkSpaceToolKeyMapItemProperties(TypedDict):
    properties: list[tuple[str, Any]]


class WorkSpaceToolKeyMapItem(NamedTuple):
    idname: str
    args: _WorkSpaceToolKeyMapItemEvent
    data: _WorkSpaceToolKeyMapItemProperties


def _tool_type_from_operator(bl_operator: str) -> Literal['BOX', 'CIRCLE', 'LASSO'] | None:
    match bl_operator:
        case "mesh.select_box_xray" | "object.select_box_xray" | "view3d.select_box":
            return 'BOX'
        case "mesh.select_circle_xray" | "object.select_circle_xray" | "view3d.select_circle":
            return 'CIRCLE'
        case "mesh.select_lasso_xray" | "object.select_lasso_xray" | "view3d.select_lasso":
            return 'LASSO'
        case _:
            return


def keymap_from_addon_preferences(operator: str) -> tuple[WorkSpaceToolKeyMapItem, ...]:
    """
    Construct toolbar tool keymap from the addon preferences.
    """
    tool_type = _tool_type_from_operator(operator)
    assert tool_type is not None
    addon_prefs_kms = addon_info.get_preferences().keymaps.tool_keymaps  # Configs group of all tool types.
    addon_prefs_km = addon_prefs_kms[tool_type]  # Configs group of a single tool type.
    addon_prefs_km_items = addon_prefs_km.keymap_items  # Configs of a single tool type.

    bl_keymap: list[WorkSpaceToolKeyMapItem] = []
    for prop_group_name, prop_group in addon_prefs_km_items.items():  # type: ignore
        selection_mode = cast(str, prop_group_name)
        kmi_prefs = cast("XRAYSELToolKeyMapItemPG", prop_group)

        if not kmi_prefs["active"]:
            continue

        kmi = WorkSpaceToolKeyMapItem(
            operator,
            {
                "type": 'LEFTMOUSE',
                "value": 'CLICK_DRAG',
                "shift": kmi_prefs["shift"],
                "ctrl": kmi_prefs["ctrl"],
                "alt": kmi_prefs["alt"],
                "oskey": kmi_prefs["oskey"],
            },
            {"properties": []},
        )
        if selection_mode != 'DEF':
            kmi.data["properties"].append(("mode", selection_mode))
        if tool_type == 'CIRCLE':
            kmi.data["properties"].append(("wait_for_input", False))

        bl_keymap.append(kmi)

    bl_keymap.reverse()  # Keymap items are registered in the reverse order.
    return tuple(bl_keymap)
