from typing import TYPE_CHECKING

from . import keymap_ui
from ...operators import ot_keymap

if TYPE_CHECKING:
    # Only imported for type-checking
    from ..addon_preferences import XRAYSELPreferences


def draw_flow_vertical_separator(flow):
    row = flow.row()
    row.scale_y = 0.7
    row.label(text="")
    row = flow.row()
    row.scale_y = 0.7
    row.label(text="")


def draw_mesh_tools_preferences(self: "XRAYSELPreferences", box):
    """Mesh Tools tab."""
    use_directional_props = self.me_directional_box | self.me_directional_lasso

    dir_tools = []
    def_tools = ["Circle"]
    if self.me_directional_box:
        dir_tools.append("Box")
    else:
        def_tools.append("Box")
    if self.me_directional_lasso:
        dir_tools.append("Lasso")
    else:
        def_tools.append("Lasso")

    rtl_props = self.me_direction_properties["RIGHT_TO_LEFT"]
    ltr_props = self.me_direction_properties["LEFT_TO_RIGHT"]

    rtl_st_available = rtl_props.select_through or self.me_select_through_toggle_key != 'DISABLED'
    ltr_st_available = ltr_props.select_through or self.me_select_through_toggle_key != 'DISABLED'
    def_st_available = self.me_select_through or self.me_select_through_toggle_key != 'DISABLED'

    # Keymap
    if self.enable_me_keyboard_keymap:
        box.label(text="Modify shortcuts here or disable them by unchecking")
        col = box.column()
        keymap_ui.draw_keymap_items(col, "Mesh", ot_keymap.me_keyboard_keymap, None, False)
        box.separator(factor=1.7)

    flow = box.grid_flow(columns=2, row_major=True, align=True)

    # Select through
    if not use_directional_props:
        flow.label(text="Start selection with \"Select Through\" mode enabled")
        flow.prop(self, "me_select_through", text="Select Through", icon='MOD_WIREFRAME')

    # Select through toggle
    flow.label(text="Toggle \"Select Through\" mode while selecting using a following key")
    split = flow.split(align=True)
    sub = split.row(align=True)
    sub.active = self.me_select_through_toggle_key != 'DISABLED'
    sub.prop(self, "me_select_through_toggle_type", text="")
    split.prop(self, "me_select_through_toggle_key", text="")

    if use_directional_props:
        draw_flow_vertical_separator(flow)
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
        split.prop(self, "me_select_through", text="Select Through", icon='MOD_WIREFRAME')

        # Color
        flow.label(text="Color of the selection frame when not selecting through")
        split = flow.split(align=True)
        split.prop(rtl_props, "default_color", text="")
        split.prop(ltr_props, "default_color", text="")
        split.prop(self, "me_default_color", text="")
        flow.label(text="Color of the selection frame when selecting through")
        split = flow.split(align=True)
        split.prop(rtl_props, "select_through_color", text="")
        split.prop(ltr_props, "select_through_color", text="")
        split.prop(self, "me_select_through_color", text="")

        # Show x-ray
        flow.label(text="Enable X-Ray shading during selection")
        split = flow.split(align=True)
        row = split.row(align=True)
        row.active = rtl_st_available
        row.prop(rtl_props, "show_xray", text="Show X-Ray", icon='XRAY')
        row = split.row(align=True)
        row.active = ltr_st_available
        row.prop(ltr_props, "show_xray", text="Show X-Ray", icon='XRAY')
        row = split.row(align=True)
        row.active = def_st_available
        row.prop(self, "me_show_xray", text="Show X-Ray", icon='XRAY')

        # All edges
        row = flow.row(align=True)
        row.label(text="Select all edges intersecting the selection region")
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_select_all_edges"
        split = flow.split(align=True)
        row = split.row(align=True)
        row.active = rtl_st_available
        row.prop(rtl_props, "select_all_edges", text="Select All Edges", icon='EDGESEL')
        row = split.row(align=True)
        row.active = ltr_st_available
        row.prop(ltr_props, "select_all_edges", text="Select All Edges", icon='EDGESEL')
        row = split.row(align=True)
        row.active = def_st_available
        row.prop(self, "me_select_all_edges", text="Select All Edges", icon='EDGESEL')

        # All faces
        row = flow.row(align=True)
        row.label(text="Select all faces intersecting the selection region")
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_select_all_faces"
        split = flow.split(align=True)
        row = split.row(align=True)
        row.active = rtl_st_available
        row.prop(rtl_props, "select_all_faces", text="Select All Faces", icon='FACESEL')
        row = split.row(align=True)
        row.active = ltr_st_available
        row.prop(ltr_props, "select_all_faces", text="Select All Faces", icon='FACESEL')
        row = split.row(align=True)
        row.active = def_st_available
        row.prop(self, "me_select_all_faces", text="Select All Faces", icon='FACESEL')

        # Backfacing
        row = flow.row(align=True)
        row.label(text="Select elements with normals pointing away from the view")
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_select_backfacing"
        split = flow.split(align=True)
        row = split.row(align=True)
        row.active = rtl_st_available
        row.prop(rtl_props, "select_backfacing", text="Select Backfacing", icon='NORMALS_FACE')
        row = split.row(align=True)
        row.active = ltr_st_available
        row.prop(ltr_props, "select_backfacing", text="Select Backfacing", icon='NORMALS_FACE')
        row = split.row(align=True)
        row.active = def_st_available
        row.prop(self, "me_select_backfacing", text="Select Backfacing", icon='NORMALS_FACE')
    else:
        # Color
        draw_flow_vertical_separator(flow)
        flow.label(text="Color of the selection frame when not selecting through")
        flow.prop(self, "me_default_color", text="")
        flow.label(text="Color of the selection frame when selecting through")
        flow.prop(self, "me_select_through_color", text="")

        # Show x-ray
        draw_flow_vertical_separator(flow)
        flow.label(text="Enable X-Ray shading during selection")
        row = flow.row()
        row.active = def_st_available
        row.prop(self, "me_show_xray", text="Show X-Ray", icon='XRAY')

        # All edges and faces
        draw_flow_vertical_separator(flow)
        flow.label(text="Select all edges intersecting the selection region")
        row = flow.row(align=True)
        row.active = def_st_available
        row.prop(self, "me_select_all_edges", text="Select All Edges", icon='EDGESEL')
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_select_all_edges"

        flow.label(text="Select all faces intersecting the selection region")
        row = flow.row(align=True)
        row.active = def_st_available
        row.prop(self, "me_select_all_faces", text="Select All Faces", icon='FACESEL')
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_select_all_faces"

        flow.label(text="Select elements with normals pointing away from the view")
        row = flow.row(align=True)
        row.active = def_st_available
        row.prop(self, "me_select_backfacing", text="Select Backfacing", icon='NORMALS_FACE')
        row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_select_backfacing"

    # Directional toggles
    draw_flow_vertical_separator(flow)
    flow.label(text="Set tool behavior based on drag direction")
    split = flow.split(align=True)
    split.prop(self, "me_directional_box", text="Directional Box", icon='UV_SYNC_SELECT')
    row = split.row(align=True)
    row.prop(self, "me_directional_lasso", text="Directional Lasso", icon='UV_SYNC_SELECT')
    row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_drag_direction"

    # Modifiers
    draw_flow_vertical_separator(flow)
    flow.label(text="Temporarily hide these modifiers during selection")
    split = flow.split(align=True)
    if use_directional_props:
        split.active = rtl_st_available or ltr_st_available or def_st_available
    else:
        split.active = def_st_available
    split.prop(self, "me_hide_mirror", text="Hide Mirror", icon='MOD_MIRROR')
    row = split.row(align=True)
    row.prop(self, "me_hide_solidify", text="Hide Solidify", icon='MOD_SOLIDIFY')
    row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "me_hide_modifiers"

    # Gizmo
    draw_flow_vertical_separator(flow)
    flow.label(text="Temporarily hide the gizmo of the active tool")
    row = flow.row(align=True)
    row.prop(self, "me_hide_gizmo", text="Hide Gizmo", icon='GIZMO')
    row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "hide_gizmo"

    # Icon
    draw_flow_vertical_separator(flow)
    flow.label(text="Display the box tool crosshair or lasso tool icon")
    split = flow.split(align=True)
    split.prop(self, "me_show_crosshair", text="Show Crosshair", icon='RESTRICT_SELECT_OFF')
    row = split.row(align=True)
    row.prop(self, "me_show_lasso_icon", text="Show Lasso Icon", icon='RESTRICT_SELECT_OFF')
    row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "wait_for_input_cursor"

    # Startup
    draw_flow_vertical_separator(flow)
    flow.label(text="Automatically activate following tool at startup")
    flow.prop(self, "me_tool_to_activate", text="")

    # Group with builtin tools
    draw_flow_vertical_separator(flow)
    flow.label(text="Group with built-in selection tools in the toolbar")
    row = flow.row(align=True)
    row.prop(self, "me_group_with_builtins", text="Group with Builtins", icon='GROUP')
    row.operator("xraysel.show_info_popup", text="", icon='QUESTION').button = "group_with_builtins"
