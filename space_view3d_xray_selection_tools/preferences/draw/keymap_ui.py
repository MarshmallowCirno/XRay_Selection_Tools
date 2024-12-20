from typing import TYPE_CHECKING

import bpy
import rna_keymap_ui

from ...operators import ot_keymap

if TYPE_CHECKING:
    # Only imported for type-checking
    from ..addon_preferences import XRAYSELPreferences


def draw_keymap_items(col, km_name, keymap, map_type=None, allow_remove=False):
    kc = bpy.context.window_manager.keyconfigs.user
    km = kc.keymaps.get(km_name)
    kmi_idnames = [km_tuple[1].idname for km_tuple in keymap]
    if allow_remove:
        col.context_pointer_set("keymap", km)

    if map_type is None:
        kmis = [kmi for kmi in km.keymap_items if kmi.idname in kmi_idnames and kmi.map_type]
    else:
        kmis = [kmi for kmi in km.keymap_items if kmi.idname in kmi_idnames and kmi.map_type in map_type]

    for kmi in kmis:
        rna_keymap_ui.draw_kmi(['ADDON', 'USER', 'DEFAULT'], kc, km, kmi, col, 0)


def draw_keymaps(self: "XRAYSELPreferences", box):
    """Advanced Keymap tab."""

    # Object and Mesh Mode Keymap
    col = box.column()
    row = col.row(align=True)
    row.label(text="Shortcuts for activating tools and modifying preferences")
    row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "tool_keymaps"

    col = box.column()

    km_col = col.column(align=True)
    icon = 'CHECKBOX_HLT' if self.enable_me_keyboard_keymap else 'CHECKBOX_DEHLT'
    km_col.prop(self, "enable_me_keyboard_keymap", text="Mesh Mode Tools: Keyboard Shortcuts", icon=icon)
    if self.enable_me_keyboard_keymap:
        sub_box = km_col.box()
        kmi_col = sub_box.column(align=True)
        draw_keymap_items(kmi_col, "Mesh", ot_keymap.me_keyboard_keymap, {'KEYBOARD'}, True)

    km_col = col.column(align=True)
    icon = 'CHECKBOX_HLT' if self.enable_ob_keyboard_keymap else 'CHECKBOX_DEHLT'
    km_col.prop(self, "enable_ob_keyboard_keymap", text="Object Mode Tools: Keyboard Shortcuts", icon=icon)
    if self.enable_ob_keyboard_keymap:
        sub_box = km_col.box()
        kmi_col = sub_box.column(align=True)
        draw_keymap_items(kmi_col, "Object Mode", ot_keymap.ob_keyboard_keymap, {'KEYBOARD'}, True)

    km_col = col.column(align=True)
    icon = 'CHECKBOX_HLT' if self.enable_me_mouse_keymap else 'CHECKBOX_DEHLT'
    km_col.prop(self, "enable_me_mouse_keymap", text="Mesh Mode Tools: Mouse Shortcuts", icon=icon)
    if self.enable_me_mouse_keymap:
        sub_box = km_col.box()
        kmi_col = sub_box.column(align=True)
        draw_keymap_items(kmi_col, "Mesh", ot_keymap.me_mouse_keymap, {'MOUSE', 'TWEAK'}, True)

    km_col = col.column(align=True)
    icon = 'CHECKBOX_HLT' if self.enable_ob_mouse_keymap else 'CHECKBOX_DEHLT'
    km_col.prop(self, "enable_ob_mouse_keymap", text="Object Mode Tools: Mouse Shortcuts", icon=icon)
    if self.enable_ob_mouse_keymap:
        sub = km_col.box()
        kmi_col = sub.column(align=True)
        draw_keymap_items(kmi_col, "Object Mode", ot_keymap.ob_mouse_keymap, {'MOUSE', 'TWEAK'}, True)

    km_col = col.column(align=True)
    icon = 'CHECKBOX_HLT' if self.enable_toggles_keymap else 'CHECKBOX_DEHLT'
    km_col.prop(self, "enable_toggles_keymap", text="Preferences Toggle Shortcuts", icon=icon)
    if self.enable_toggles_keymap:
        sub_box = km_col.box()
        kmi_col = sub_box.column(align=True)
        draw_keymap_items(kmi_col, "Mesh", ot_keymap.toggles_keymap, {'MOUSE', 'TWEAK', 'KEYBOARD'}, True)

    # Tool Selection Mode Keymap
    box.separator()
    row = box.row(align=True)
    row.label(text="Shortcuts for selection modes of toolbar tools")
    row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "tool_selection_mode_keymaps"

    col = box.column(align=True)
    row = col.row(align=True)
    row.prop(self, "tool_keymap_tabs", expand=True)

    tool = self.tool_keymap_tabs
    keymap = self.keymaps_of_tools[tool]
    kmis = keymap.kmis
    for mode in kmis.keys():
        row = col.row(align=True)
        description = kmis[mode].description
        icon = kmis[mode].icon
        row.prop(kmis[mode], "active", text=description, icon=icon)

        sub = row.row(align=True)
        sub.active = kmis[mode].active
        sub.prop(kmis[mode], "shift", text="Shift", toggle=True)
        sub.prop(kmis[mode], "ctrl", text="Ctrl", toggle=True)
        sub.prop(kmis[mode], "alt", text="Alt", toggle=True)
