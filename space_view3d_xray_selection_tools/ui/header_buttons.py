from typing import cast

import bpy
from bl_ui import space_toolsystem_common

from .. import addon_info


def _draw_func(self: bpy.types.Menu, context: bpy.types.Context):

    if not self.layout:
        return

    space_type = context.space_data.type
    if space_type != 'VIEW_3D':
        return

    # Disabled in preferences.
    if not (
        context.mode == 'EDIT_MESH'
        and addon_info.get_preferences().mesh_tools.display_header_buttons
        or context.mode == 'OBJECT'
        and addon_info.get_preferences().object_tools.display_header_buttons
    ):
        return

    idnames_by_mode = {
        'EDIT_MESH': ("mesh_tool.select_box_xray", "mesh_tool.select_circle_xray", "mesh_tool.select_lasso_xray"),
        'OBJECT': ("object_tool.select_box_xray", "object_tool.select_circle_xray", "object_tool.select_lasso_xray"),
    }

    # noinspection PyNoneFunctionAssignment
    item_group = [
        cast(
            space_toolsystem_common.ToolDef | None,
            space_toolsystem_common.item_from_id(context, space_type, idname),
        )
        for idname in idnames_by_mode[context.mode]
    ]

    if not any(item_group):
        return

    label_by_idname = {
        "mesh_tool.select_box_xray": "Box",
        "mesh_tool.select_circle_xray": "Circle",
        "mesh_tool.select_lasso_xray": "Lasso",
        "object_tool.select_box_xray": "Box",
        "object_tool.select_circle_xray": "Circle",
        "object_tool.select_lasso_xray": "Lasso",
    }

    active_tool = context.workspace.tools.from_space_view3d_mode(context.mode)

    self.layout.separator()
    self.layout.separator_spacer()
    row = self.layout.row(align=True)
    row.scale_x = 1.2

    for sub_item in item_group:
        if not sub_item:
            continue

        is_active = active_tool.idname == sub_item.idname
        icon_value = cast(
            int,
            space_toolsystem_common.ToolSelectPanelHelper._icon_value_from_icon_handle(sub_item.icon),  # pyright: ignore[reportAttributeAccessIssue]
        )

        label = label_by_idname[sub_item.idname]
        props = row.operator("wm.tool_set_by_id", text=label, depress=is_active, icon_value=icon_value)
        props.name = sub_item.idname
        props.space_type = space_type


def register():
    bpy.types.VIEW3D_MT_editor_menus.append(_draw_func)


def unregister():
    bpy.types.VIEW3D_MT_editor_menus.remove(_draw_func)
