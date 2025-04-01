from typing import TYPE_CHECKING, Literal

import bpy

from ... import tools
from ...operators import ot_keymap

if TYPE_CHECKING:
    from bpy._typing.rna_enums import IconItems


class XRAYSELToolKeyMapItemPG(bpy.types.PropertyGroup):
    """Preferences of a single tool KeyMapItem entry."""

    if TYPE_CHECKING:
        description: str
        icon: IconItems
        active: bool
        shift: bool
        ctrl: bool
        alt: bool
        oskey: bool
    else:
        description: bpy.props.StringProperty(name="Description")
        icon: bpy.props.StringProperty(name="Icon")
        active: bpy.props.BoolProperty(
            name="Active",
            description="Enable or disable selection mode",
            update=tools.update_keymaps_of_tools,
            default=True,
        )
        shift: bpy.props.BoolProperty(
            name="Shift",
            description="Shift key is pressed",
            update=tools.update_keymaps_of_tools,
            default=False,
        )
        ctrl: bpy.props.BoolProperty(
            name="Ctrl",
            description="Ctrl key is pressed",
            update=tools.update_keymaps_of_tools,
            default=False,
        )
        alt: bpy.props.BoolProperty(
            name="Alt",
            description="Alt key is pressed",
            update=tools.update_keymaps_of_tools,
            default=False,
        )
        oskey: bpy.props.BoolProperty(
            name="Cmd",
            description="Operating system key is pressed",
            update=tools.update_keymaps_of_tools,
            default=False,
        )


class XRAYSELToolKeyMapItemsPG(bpy.types.PropertyGroup):
    """Collection of KeyMapItem preferences, grouped by a tool type."""

    if TYPE_CHECKING:
        keymap_items: bpy.types.bpy_prop_collection_idprop[XRAYSELToolKeyMapItemPG]
    else:
        keymap_items: bpy.props.CollectionProperty(name="KMIS", type=XRAYSELToolKeyMapItemPG)


class XRAYSELKeymapsPreferencesPG(bpy.types.PropertyGroup):
    if TYPE_CHECKING:
        tool_keymaps: bpy.types.bpy_prop_collection_idprop[XRAYSELToolKeyMapItemsPG]
        is_mesh_keyboard_keymap_enabled: bool
        is_mesh_mouse_keymap_enabled: bool
        is_object_keyboard_keymap_enabled: bool
        is_object_mouse_keymap_enabled: bool
        is_toggles_keymap_enabled: bool
        active_tab: Literal['BOX', 'CIRCLE', 'LASSO']
    else:
        tool_keymaps: bpy.props.CollectionProperty(
            type=XRAYSELToolKeyMapItemsPG,
            name="Keymaps of Tools",
        )
        is_mesh_keyboard_keymap_enabled: bpy.props.BoolProperty(
            name="Mesh Mode Keyboard Shortcuts",
            description="Enable to add shortcuts to the Blender keymap, or disable to remove them",
            update=ot_keymap.toggle_mesh_keyboard_keymap,
            default=True,
        )
        is_mesh_mouse_keymap_enabled: bpy.props.BoolProperty(
            name="Mesh Mode Mouse Shortcuts",
            description="Enable to add shortcuts to the Blender keymap, or disable to remove them",
            update=ot_keymap.toggle_mesh_mouse_keymap,
            default=False,
        )
        is_object_keyboard_keymap_enabled: bpy.props.BoolProperty(
            name="Object Mode Keyboard Shortcuts",
            description="Enable to add shortcuts to the Blender keymap, or disable to remove them",
            update=ot_keymap.toggle_object_keyboard_keymap,
            default=True,
        )
        is_object_mouse_keymap_enabled: bpy.props.BoolProperty(
            name="Object Mode Mouse Shortcuts",
            description="Enable to add shortcuts to the Blender keymap, or disable to remove them",
            update=ot_keymap.toggle_object_mouse_keymap,
            default=False,
        )
        is_toggles_keymap_enabled: bpy.props.BoolProperty(
            name="Preferences Toggles Shortcuts",
            description="Enable to add shortcuts to the Blender keymap, or disable to remove them",
            update=ot_keymap.toggle_toggles_keymap,
            default=False,
        )
        active_tab: bpy.props.EnumProperty(
            name="Tool Selection Modifier Keys",
            items=[
                ('BOX', "Box Tool", ""),
                ('CIRCLE', "Circle Tool", ""),
                ('LASSO', "Lasso Tool", ""),
            ],
            default='BOX',
            options={'SKIP_SAVE'},
        )
