from typing import TYPE_CHECKING, Literal, cast

import bpy
import rna_keymap_ui

from ...operators import ot_keymap

if TYPE_CHECKING:
    from ...preferences.properties.keymaps_props import XRAYSELToolKeyMapItemPG
    from ..addon_preferences import XRAYSELPreferences


def draw_keymap_items(
    col: bpy.types.UILayout,
    km_name: str,
    keymap: list[tuple[bpy.types.KeyMap, bpy.types.KeyMapItem]],
    map_type: set[Literal['MOUSE', 'TWEAK', 'KEYBOARD']] | None = None,
    allow_remove: bool = False,
):
    kc = bpy.context.window_manager.keyconfigs.user
    km = kc.keymaps[km_name]
    kmi_idnames = [km_tuple[1].idname for km_tuple in keymap]
    if allow_remove:
        col.context_pointer_set("keymap", km)

    if map_type is None:
        kmis = [kmi for kmi in km.keymap_items if kmi.idname in kmi_idnames and kmi.map_type]
    else:
        kmis = [kmi for kmi in km.keymap_items if kmi.idname in kmi_idnames and kmi.map_type in map_type]

    for kmi in kmis:
        rna_keymap_ui.draw_kmi(['ADDON', 'USER', 'DEFAULT'], kc, km, kmi, col, 0)


def draw_keymaps(addon_prefs: "XRAYSELPreferences", box: bpy.types.UILayout):
    """Keymaps tab."""
    keymaps_props = addon_prefs.keymaps

    # Object and Mesh Mode Keymap
    col = box.column()
    row = col.row(align=True)
    row.label(text="Shortcuts for activating tools and modifying preferences")
    row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "tool_keymaps"  # pyright: ignore[reportAttributeAccessIssue]

    col = box.column()
    icon: Literal['CHECKBOX_HLT', 'CHECKBOX_DEHLT']

    km_col = col.column(align=True)
    icon = 'CHECKBOX_HLT' if keymaps_props.is_mesh_keyboard_keymap_enabled else 'CHECKBOX_DEHLT'
    km_col.prop(keymaps_props, "is_mesh_keyboard_keymap_enabled", text="Mesh Mode Tools: Keyboard Shortcuts", icon=icon)
    if keymaps_props.is_mesh_keyboard_keymap_enabled:
        sub_box = km_col.box()
        kmi_col = sub_box.column(align=True)
        draw_keymap_items(kmi_col, "Mesh", ot_keymap.mesh_keyboard_keymap, {'KEYBOARD'}, True)

    km_col = col.column(align=True)
    icon = 'CHECKBOX_HLT' if keymaps_props.is_object_keyboard_keymap_enabled else 'CHECKBOX_DEHLT'
    km_col.prop(
        keymaps_props, "is_object_keyboard_keymap_enabled", text="Object Mode Tools: Keyboard Shortcuts", icon=icon
    )
    if keymaps_props.is_object_keyboard_keymap_enabled:
        sub_box = km_col.box()
        kmi_col = sub_box.column(align=True)
        draw_keymap_items(kmi_col, "Object Mode", ot_keymap.object_keyboard_keymap, {'KEYBOARD'}, True)

    km_col = col.column(align=True)
    icon = 'CHECKBOX_HLT' if keymaps_props.is_mesh_mouse_keymap_enabled else 'CHECKBOX_DEHLT'
    km_col.prop(keymaps_props, "is_mesh_mouse_keymap_enabled", text="Mesh Mode Tools: Mouse Shortcuts", icon=icon)
    if keymaps_props.is_mesh_mouse_keymap_enabled:
        sub_box = km_col.box()
        kmi_col = sub_box.column(align=True)
        draw_keymap_items(kmi_col, "Mesh", ot_keymap.mesh_mouse_keymap, {'MOUSE', 'TWEAK'}, True)

    km_col = col.column(align=True)
    icon = 'CHECKBOX_HLT' if keymaps_props.is_object_mouse_keymap_enabled else 'CHECKBOX_DEHLT'
    km_col.prop(keymaps_props, "is_object_mouse_keymap_enabled", text="Object Mode Tools: Mouse Shortcuts", icon=icon)
    if keymaps_props.is_object_mouse_keymap_enabled:
        sub = km_col.box()
        kmi_col = sub.column(align=True)
        draw_keymap_items(kmi_col, "Object Mode", ot_keymap.object_mouse_keymap, {'MOUSE', 'TWEAK'}, True)

    km_col = col.column(align=True)
    icon = 'CHECKBOX_HLT' if keymaps_props.is_toggles_keymap_enabled else 'CHECKBOX_DEHLT'
    km_col.prop(keymaps_props, "is_toggles_keymap_enabled", text="Preferences Toggle Shortcuts", icon=icon)
    if keymaps_props.is_toggles_keymap_enabled:
        sub_box = km_col.box()
        kmi_col = sub_box.column(align=True)
        draw_keymap_items(kmi_col, "Mesh", ot_keymap.toggles_keymap, {'MOUSE', 'TWEAK', 'KEYBOARD'}, True)

    # Tool Selection Mode Keymap
    box.separator()
    row = box.row(align=True)
    row.label(text="Shortcuts for selection modes of toolbar tools")
    row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "tool_selection_mode_keymaps"  # pyright: ignore[reportAttributeAccessIssue]

    col = box.column(align=True)
    row = col.row(align=True)
    row.prop(keymaps_props, "active_tab", expand=True)

    tool = keymaps_props.active_tab
    keymap = addon_prefs.keymaps.tool_keymaps[tool]
    keymap_items = keymap.keymap_items
    for prop_group in keymap_items.values():  # type: ignore
        kmi_props = cast("XRAYSELToolKeyMapItemPG", prop_group)

        row = col.row(align=True)
        row.prop(kmi_props, "active", text=kmi_props.description, icon=kmi_props.icon)

        sub = row.row(align=True)
        sub.active = kmi_props.active
        sub.prop(kmi_props, "shift", text="Shift", toggle=True)
        sub.prop(kmi_props, "ctrl", text="Ctrl", toggle=True)
        sub.prop(kmi_props, "alt", text="Alt", toggle=True)
        sub.prop(kmi_props, "oskey", text="Cmd", toggle=True)
