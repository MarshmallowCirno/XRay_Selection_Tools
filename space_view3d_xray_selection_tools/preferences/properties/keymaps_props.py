import bpy

from ... import tools
from ...operators import ot_keymap


class XRAYSELToolKmiPG(bpy.types.PropertyGroup):
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


class XRAYSELToolKeymapPG(bpy.types.PropertyGroup):
    kmis: bpy.props.CollectionProperty(name="KMIS", type=XRAYSELToolKmiPG)


class XRAYSELKeymapsPreferencesPG(bpy.types.PropertyGroup):

    tools_keymaps: bpy.props.CollectionProperty(
        type=XRAYSELToolKeymapPG,
        name="Keymaps of Tools",
    )
    is_mesh_keyboard_keymap_enabled: bpy.props.BoolProperty(
        name="Mesh Mode Keyboard Shortcuts",
        description="Enable to add shortcuts to the Blender keymap, or disable to remove them",
        update=ot_keymap.toggle_me_keyboard_keymap,
        default=True,
    )
    is_mesh_mouse_keymap_enabled: bpy.props.BoolProperty(
        name="Mesh Mode Mouse Shortcuts",
        description="Enable to add shortcuts to the Blender keymap, or disable to remove them",
        update=ot_keymap.toggle_me_mouse_keymap,
        default=False,
    )
    is_object_keyboard_keymap_enabled: bpy.props.BoolProperty(
        name="Object Mode Keyboard Shortcuts",
        description="Enable to add shortcuts to the Blender keymap, or disable to remove them",
        update=ot_keymap.toggle_ob_keyboard_keymap,
        default=True,
    )
    is_object_mouse_keymap_enabled: bpy.props.BoolProperty(
        name="Object Mode Mouse Shortcuts",
        description="Enable to add shortcuts to the Blender keymap, or disable to remove them",
        update=ot_keymap.toggle_ob_mouse_keymap,
        default=False,
    )
    is_toggles_keymap_enabled: bpy.props.BoolProperty(
        name="Preferences Toggles Shortcuts",
        description="Enable to add shortcuts to the Blender keymap, or disable to remove them",
        update=ot_keymap.toggle_toggles_keymap,
        default=False,
    )

    # noinspection PyTypeChecker
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
