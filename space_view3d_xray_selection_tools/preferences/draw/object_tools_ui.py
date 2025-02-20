from typing import TYPE_CHECKING

import bpy

from ...operators import ot_keymap
from . import keymap_ui

if TYPE_CHECKING:
    from ..addon_preferences import XRAYSELPreferences


def _draw_flow_vertical_separator(flow: bpy.types.UILayout):
    row = flow.row()
    row.scale_y = 0.7
    row.label(text="")
    row = flow.row()
    row.scale_y = 0.7
    row.label(text="")


def draw_object_tools_preferences(addon_prefs: "XRAYSELPreferences", box: bpy.types.UILayout):
    """Object Tools tab."""
    object_tools_props = addon_prefs.object_tools

    # Keymap
    if addon_prefs.keymaps.is_object_keyboard_keymap_enabled:
        box.label(text="Modify shortcuts here or disable them by unchecking")
        col = box.column()
        keymap_ui.draw_keymap_items(col, "Object Mode", ot_keymap.object_keyboard_keymap, None, False)
        box.separator(factor=1.7)

    flow = box.grid_flow(columns=2, row_major=True, align=True)

    # Select through
    flow.label(text="Start selection with X-Ray shading enabled")
    flow.prop(object_tools_props, "show_xray", text="Show X-Ray", icon='XRAY')

    # Select toggle
    flow.label(text="Toggle X-Ray shading while selecting using a following key")
    split = flow.split(align=True)
    sub = split.row(align=True)
    sub.active = object_tools_props.xray_toggle_key != 'DISABLED'
    sub.prop(object_tools_props, "xray_toggle_type", text="")
    split.prop(object_tools_props, "xray_toggle_key", text="")

    # Behavior
    _draw_flow_vertical_separator(flow)
    flow.label(text="Box tool behavior")
    row = flow.row(align=True)
    row.prop(object_tools_props, "box_select_behavior", text="")
    row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "selection_behavior"  # pyright: ignore[reportAttributeAccessIssue]
    flow.label(text="Circle tool behavior")
    row = flow.row(align=True)
    row.prop(object_tools_props, "circle_select_behavior", text="")
    row.label(text="", icon='BLANK1')
    flow.label(text="Lasso tool behavior")
    row = flow.row(align=True)
    row.prop(object_tools_props, "lasso_select_behavior", text="")
    row.label(text="", icon='BLANK1')

    # Gizmo
    _draw_flow_vertical_separator(flow)
    flow.label(text="Temporarily hide the gizmo of the active tool")
    row = flow.row(align=True)
    row.prop(object_tools_props, "hide_gizmo", text="Hide Gizmo", icon='GIZMO')
    row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "hide_gizmo"  # pyright: ignore[reportAttributeAccessIssue]

    # Icon
    _draw_flow_vertical_separator(flow)
    flow.label(text="Display the box tool crosshair or lasso tool icon")
    split = flow.split(align=True)
    split.prop(object_tools_props, "show_crosshair", text="Show Crosshair", icon='RESTRICT_SELECT_OFF')
    row = split.row(align=True)
    row.prop(object_tools_props, "show_lasso_icon", text="Show Lasso Icon", icon='RESTRICT_SELECT_OFF')
    row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "wait_for_input_cursor"  # pyright: ignore[reportAttributeAccessIssue]

    # Startup
    _draw_flow_vertical_separator(flow)
    flow.label(text="Automatically activate following tool at startup")
    flow.prop(object_tools_props, "tool_to_activate", text="")

    # Group with builtin tools
    _draw_flow_vertical_separator(flow)
    flow.label(text="Group with built-in selection tools in the toolbar")
    row = flow.row(align=True)
    row.prop(object_tools_props, "group_with_builtins", text="Group with Builtins", icon='GROUP')
    row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "group_with_builtins"  # pyright: ignore[reportAttributeAccessIssue]
