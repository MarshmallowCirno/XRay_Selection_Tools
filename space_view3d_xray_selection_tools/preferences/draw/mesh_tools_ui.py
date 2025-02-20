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


def draw_mesh_tools_preferences(addon_prefs: "XRAYSELPreferences", box: bpy.types.UILayout):
    """Mesh Tools tab."""
    use_directional_props = addon_prefs.mesh_tools.directional_box_tool | addon_prefs.mesh_tools.directional_lasso_tool
    mesh_tools_props = addon_prefs.mesh_tools

    dir_tools: list[str] = []
    def_tools: list[str] = ["Circle"]
    if mesh_tools_props.directional_box_tool:
        dir_tools.append("Box")
    else:
        def_tools.append("Box")
    if mesh_tools_props.directional_lasso_tool:
        dir_tools.append("Lasso")
    else:
        def_tools.append("Lasso")

    rtl_props = mesh_tools_props.direction_properties["RIGHT_TO_LEFT"]
    ltr_props = mesh_tools_props.direction_properties["LEFT_TO_RIGHT"]

    rtl_select_through_available = rtl_props.select_through
    ltr_select_through_available = ltr_props.select_through
    def_select_through_available = mesh_tools_props.select_through

    # Keymap
    if addon_prefs.keymaps.is_mesh_keyboard_keymap_enabled:
        box.label(text="Modify shortcuts here or disable them by unchecking")
        col = box.column()
        keymap_ui.draw_keymap_items(col, "Mesh", ot_keymap.mesh_keyboard_keymap, None, False)
        box.separator(factor=1.7)

    flow = box.grid_flow(columns=2, row_major=True, align=True)

    # Select through
    if not use_directional_props:
        flow.label(text="Start selection with \"Select Through\" mode enabled")
        flow.prop(mesh_tools_props, "select_through", text="Select Through", icon='MOD_WIREFRAME')

    # Select through toggle
    flow.label(text="Toggle \"Select Through\" mode while selecting using a following key")
    split = flow.split(align=True)
    sub = split.row(align=True)
    sub.active = mesh_tools_props.select_through_toggle_key != 'DISABLED'
    sub.prop(mesh_tools_props, "select_through_toggle_type", text="")
    split.prop(mesh_tools_props, "select_through_toggle_key", text="")

    if use_directional_props:
        _draw_flow_vertical_separator(flow)
        # Labels
        flow.label(text="Tool")
        split = flow.split(align=True)
        row = split.row()
        row.label(text="", icon='BLANK1')
        sub = row.row()
        sub.alignment = 'CENTER'
        sub.label(text=" and ".join(dir_tools))
        row = split.row()
        row.label(text="", icon='BLANK1')
        sub = row.row()
        sub.alignment = 'CENTER'
        sub.label(text=" and ".join(dir_tools))
        row = split.row()
        row.label(text="", icon='BLANK1')
        sub = row.row()
        sub.alignment = 'CENTER'
        sub.label(text=" and ".join(def_tools))

        # Directions
        flow.label(text="Drag direction")
        split = flow.split(align=True)
        row = split.row()
        row.label(text="", icon='BACK')
        sub = row.row()
        sub.alignment = 'CENTER'
        sub.label(text="Right to Left")
        row = split.row()
        row.label(text="", icon='FORWARD')
        sub = row.row()
        sub.alignment = 'CENTER'
        sub.label(text="Left to Right")
        row = split.row()
        row.label(text="", icon='ARROW_LEFTRIGHT')
        sub = row.row()
        sub.alignment = 'CENTER'
        sub.label(text="Any")

        # Select through
        flow.label(text="Start selection with \"Select Through\" mode enabled")
        split = flow.split(align=True)
        split.prop(rtl_props, "select_through", text="Select Through", icon='MOD_WIREFRAME')
        split.prop(ltr_props, "select_through", text="Select Through", icon='MOD_WIREFRAME')
        split.prop(mesh_tools_props, "select_through", text="Select Through", icon='MOD_WIREFRAME')

        # Color
        flow.label(text="Color of the selection frame when not selecting through")
        split = flow.split(align=True)
        split.prop(rtl_props, "default_color", text="")
        split.prop(ltr_props, "default_color", text="")
        split.prop(mesh_tools_props, "default_color", text="")
        flow.label(text="Color of the selection frame when selecting through")
        split = flow.split(align=True)
        split.prop(rtl_props, "select_through_color", text="")
        split.prop(ltr_props, "select_through_color", text="")
        split.prop(mesh_tools_props, "select_through_color", text="")

        # Show x-ray
        flow.label(text="Enable X-Ray shading during selection")
        split = flow.split(align=True)
        row = split.row(align=True)
        row.active = rtl_select_through_available
        row.prop(rtl_props, "show_xray", text="Show X-Ray", icon='XRAY')
        row = split.row(align=True)
        row.active = ltr_select_through_available
        row.prop(ltr_props, "show_xray", text="Show X-Ray", icon='XRAY')
        row = split.row(align=True)
        row.active = def_select_through_available
        row.prop(mesh_tools_props, "show_xray", text="Show X-Ray", icon='XRAY')

        # All edges
        row = flow.row(align=True)
        row.label(text="Select all edges intersecting the selection region")
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "select_all_edges"  # pyright: ignore[reportAttributeAccessIssue]
        split = flow.split(align=True)
        row = split.row(align=True)
        row.active = rtl_select_through_available
        row.prop(rtl_props, "select_all_edges", text="Select All Edges", icon='EDGESEL')
        row = split.row(align=True)
        row.active = ltr_select_through_available
        row.prop(ltr_props, "select_all_edges", text="Select All Edges", icon='EDGESEL')
        row = split.row(align=True)
        row.active = def_select_through_available
        row.prop(mesh_tools_props, "select_all_edges", text="Select All Edges", icon='EDGESEL')

        # All faces
        row = flow.row(align=True)
        row.label(text="Select all faces intersecting the selection region")
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "select_all_faces"  # pyright: ignore[reportAttributeAccessIssue]
        split = flow.split(align=True)
        row = split.row(align=True)
        row.active = rtl_select_through_available
        row.prop(rtl_props, "select_all_faces", text="Select All Faces", icon='FACESEL')
        row = split.row(align=True)
        row.active = ltr_select_through_available
        row.prop(ltr_props, "select_all_faces", text="Select All Faces", icon='FACESEL')
        row = split.row(align=True)
        row.active = def_select_through_available
        row.prop(mesh_tools_props, "select_all_faces", text="Select All Faces", icon='FACESEL')

        # Backfacing
        row = flow.row(align=True)
        row.label(text="Select elements with normals pointing away from the view")
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "select_backfacing"  # pyright: ignore[reportAttributeAccessIssue]
        split = flow.split(align=True)
        row = split.row(align=True)
        row.active = rtl_select_through_available
        row.prop(rtl_props, "select_backfacing", text="Select Backfacing", icon='NORMALS_FACE')
        row = split.row(align=True)
        row.active = ltr_select_through_available
        row.prop(ltr_props, "select_backfacing", text="Select Backfacing", icon='NORMALS_FACE')
        row = split.row(align=True)
        row.active = def_select_through_available
        row.prop(mesh_tools_props, "select_backfacing", text="Select Backfacing", icon='NORMALS_FACE')
    else:
        # Color
        _draw_flow_vertical_separator(flow)
        flow.label(text="Color of the selection frame when not selecting through")
        flow.prop(mesh_tools_props, "default_color", text="")
        flow.label(text="Color of the selection frame when selecting through")
        flow.prop(mesh_tools_props, "select_through_color", text="")

        # Show x-ray
        _draw_flow_vertical_separator(flow)
        flow.label(text="Enable X-Ray shading during selection")
        row = flow.row()
        row.active = def_select_through_available
        row.prop(mesh_tools_props, "show_xray", text="Show X-Ray", icon='XRAY')

        # All edges and faces
        _draw_flow_vertical_separator(flow)
        flow.label(text="Select all edges intersecting the selection region")
        row = flow.row(align=True)
        row.active = def_select_through_available
        row.prop(mesh_tools_props, "select_all_edges", text="Select All Edges", icon='EDGESEL')
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "select_all_edges"  # pyright: ignore[reportAttributeAccessIssue]

        flow.label(text="Select all faces intersecting the selection region")
        row = flow.row(align=True)
        row.active = def_select_through_available
        row.prop(mesh_tools_props, "select_all_faces", text="Select All Faces", icon='FACESEL')
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "select_all_faces"  # pyright: ignore[reportAttributeAccessIssue]

        flow.label(text="Select elements with normals pointing away from the view")
        row = flow.row(align=True)
        row.active = def_select_through_available
        row.prop(mesh_tools_props, "select_backfacing", text="Select Backfacing", icon='NORMALS_FACE')
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "select_backfacing"  # pyright: ignore[reportAttributeAccessIssue]

    # Directional toggles
    _draw_flow_vertical_separator(flow)
    flow.label(text="Set tool behavior based on drag direction")
    split = flow.split(align=True)
    split.prop(mesh_tools_props, "directional_box_tool", text="Directional Box", icon='UV_SYNC_SELECT')
    row = split.row(align=True)
    row.prop(mesh_tools_props, "directional_lasso_tool", text="Directional Lasso", icon='UV_SYNC_SELECT')
    row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "drag_direction"  # pyright: ignore[reportAttributeAccessIssue]

    # Modifiers
    _draw_flow_vertical_separator(flow)
    flow.label(text="Temporarily hide these modifiers during selection")
    split = flow.split(align=True)
    if use_directional_props:
        split.active = rtl_select_through_available or ltr_select_through_available or def_select_through_available
    else:
        split.active = def_select_through_available
    split.prop(mesh_tools_props, "hide_mirror", text="Hide Mirror", icon='MOD_MIRROR')
    row = split.row(align=True)
    row.prop(mesh_tools_props, "hide_solidify", text="Hide Solidify", icon='MOD_SOLIDIFY')
    row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "hide_modifiers"  # pyright: ignore[reportAttributeAccessIssue]

    # Gizmo
    _draw_flow_vertical_separator(flow)
    flow.label(text="Temporarily hide the gizmo of the active tool")
    row = flow.row(align=True)
    row.prop(mesh_tools_props, "hide_gizmo", text="Hide Gizmo", icon='GIZMO')
    row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "hide_gizmo"  # pyright: ignore[reportAttributeAccessIssue]

    # Icon
    _draw_flow_vertical_separator(flow)
    flow.label(text="Display the box tool crosshair or lasso tool icon")
    split = flow.split(align=True)
    split.prop(mesh_tools_props, "show_crosshair", text="Show Crosshair", icon='RESTRICT_SELECT_OFF')
    row = split.row(align=True)
    row.prop(mesh_tools_props, "show_lasso_icon", text="Show Lasso Icon", icon='RESTRICT_SELECT_OFF')
    row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "wait_for_input_cursor"  # pyright: ignore[reportAttributeAccessIssue]

    # Startup
    _draw_flow_vertical_separator(flow)
    flow.label(text="Automatically activate following tool at startup")
    flow.prop(mesh_tools_props, "tool_to_activate", text="")

    # Group with builtin tools
    _draw_flow_vertical_separator(flow)
    flow.label(text="Group with built-in selection tools in the toolbar")
    row = flow.row(align=True)
    row.prop(mesh_tools_props, "group_with_builtins", text="Group with Builtins", icon='GROUP')
    row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "group_with_builtins"  # pyright: ignore[reportAttributeAccessIssue]
