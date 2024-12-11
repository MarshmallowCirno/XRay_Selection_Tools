import itertools

import bpy

from .tools_keymap import (
    add_fallback_keymap,
    add_fallback_keymap_items,
    FALLBACK_KEYMAP_DICT,
    get_tool_keymap_from_preferences,
    remove_fallback_keymap_items,
)
from .tools_utils import fix_ordering, ICON_PATH
from ..addon_info import get_preferences


# Box Tools


class ToolSelectBoxXrayMesh(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_MESH'

    bl_idname = "mesh_tool.select_box_xray"
    bl_label = "Select Box X-Ray"
    bl_description = "Select items using box selection with x-ray"
    bl_icon = str(ICON_PATH / "addon.select_box_xray_icon")
    bl_widget = None
    bl_operator = "mesh.select_box_xray"
    bl_keymap: tuple

    # noinspection PyMethodMayBeStatic, PyMethodParameters
    def draw_settings(context, layout, tool):
        tool_props = tool.operator_properties("mesh.select_box_xray")
        global_props = get_preferences()

        row = layout.row()
        row.use_property_split = False
        row.prop(tool_props, "mode", text="", expand=True, icon_only=True)

        sub = row.row(align=True)
        sub.prop(global_props, "me_select_through", icon='XRAY', toggle=True)
        sub = sub.row(align=True)
        sub.active = global_props.me_select_through
        sub.prop(global_props, "me_select_backfacing", icon='NORMALS_FACE', toggle=True)


class ToolSelectBoxXrayObject(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'

    bl_idname = "object_tool.select_box_xray"
    bl_label = "Select Box X-Ray"
    bl_description = "Select items using box selection with x-ray"
    bl_icon = str(ICON_PATH / "addon.select_box_xray_icon")
    bl_widget = None
    bl_operator = "object.select_box_xray"
    bl_keymap: tuple

    # noinspection PyMethodMayBeStatic, PyMethodParameters
    def draw_settings(context, layout, tool):
        tool_props = tool.operator_properties("object.select_box_xray")

        row = layout.row()
        row.use_property_split = False
        row.prop(tool_props, "mode", text="", expand=True, icon_only=True)


# Circle Tools


class ToolSelectCircleXrayMesh(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_MESH'

    bl_idname = "mesh_tool.select_circle_xray"
    bl_label = "Select Circle X-Ray"
    bl_description = "Select items using circle selection with x-ray"
    bl_icon = str(ICON_PATH / "addon.select_circle_xray_icon")
    bl_widget = None
    bl_operator = "mesh.select_lasso_xray"
    bl_keymap: tuple

    # noinspection PyMethodMayBeStatic, PyMethodParameters
    def draw_cursor(context, tool, xy):
        from gpu_extras.presets import draw_circle_2d

        props = tool.operator_properties("mesh.select_circle_xray")
        radius = props.radius
        draw_circle_2d(xy, (1.0,) * 4, radius, segments=32)

    # noinspection PyMethodMayBeStatic, PyMethodParameters
    def draw_settings(context, layout, tool):
        tool_props = tool.operator_properties("mesh.select_circle_xray")
        global_props = get_preferences()

        row = layout.row()
        row.use_property_split = False
        row.prop(tool_props, "mode", text="", expand=True, icon_only=True)

        sub = row.row(align=True)
        sub.prop(global_props, "me_select_through", icon='XRAY', toggle=True)
        sub = sub.row(align=True)
        sub.active = global_props.me_select_through
        sub.prop(global_props, "me_select_backfacing", icon='NORMALS_FACE', toggle=True)

        layout.prop(tool_props, "radius")


class ToolSelectCircleXrayObject(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'

    bl_idname = "object_tool.select_circle_xray"
    bl_label = "Select Circle X-Ray"
    bl_description = "Select items using circle selection with x-ray"
    bl_icon = str(ICON_PATH / "addon.select_circle_xray_icon")
    bl_widget = None
    bl_operator = "object.select_circle_xray"
    bl_keymap: tuple

    # noinspection PyMethodMayBeStatic, PyMethodParameters
    def draw_cursor(context, tool, xy):
        from gpu_extras.presets import draw_circle_2d

        props = tool.operator_properties("object.select_circle_xray")
        radius = props.radius
        draw_circle_2d(xy, (1.0,) * 4, radius, segments=32)

    # noinspection PyMethodMayBeStatic, PyMethodParameters
    def draw_settings(context, layout, tool):
        tool_props = tool.operator_properties("object.select_circle_xray")

        row = layout.row()
        row.use_property_split = False
        row.prop(tool_props, "mode", text="", expand=True, icon_only=True)

        layout.prop(tool_props, "radius")


# Lasso Tools


class ToolSelectLassoXrayMesh(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_MESH'

    bl_idname = "mesh_tool.select_lasso_xray"
    bl_label = "Select Lasso X-Ray"
    bl_description = "Select items using lasso selection with x-ray"
    bl_icon = str(ICON_PATH / "addon.select_lasso_xray_icon")
    bl_widget = None
    bl_operator = "mesh.select_lasso_xray"
    bl_keymap: tuple

    # noinspection PyMethodMayBeStatic, PyMethodParameters
    def draw_settings(context, layout, tool):
        tool_props = tool.operator_properties("mesh.select_lasso_xray")
        global_props = get_preferences()

        row = layout.row()
        row.use_property_split = False
        row.prop(tool_props, "mode", text="", expand=True, icon_only=True)

        sub = row.row(align=True)
        sub.prop(global_props, "me_select_through", icon='XRAY', toggle=True)
        sub = sub.row(align=True)
        sub.active = global_props.me_select_through
        sub.prop(global_props, "me_select_backfacing", icon='NORMALS_FACE', toggle=True)


class ToolSelectLassoXrayObject(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'

    bl_idname = "object_tool.select_lasso_xray"
    bl_label = "Select Lasso X-Ray"
    bl_description = "Select items using lasso selection with x-ray"
    bl_icon = str(ICON_PATH / "addon.select_lasso_xray_icon")
    bl_widget = None
    bl_operator = "object.select_lasso_xray"
    bl_keymap: tuple

    # noinspection PyMethodMayBeStatic, PyMethodParameters
    def draw_settings(context, layout, tool):
        tool_props = tool.operator_properties("object.select_lasso_xray")

        row = layout.row()
        row.use_property_split = False
        row.prop(tool_props, "mode", text="", expand=True, icon_only=True)


BOX_TOOLS = (ToolSelectBoxXrayMesh, ToolSelectBoxXrayObject)
CIRCLE_TOOLS = (ToolSelectCircleXrayMesh, ToolSelectCircleXrayObject)
LASSO_TOOLS = (ToolSelectLassoXrayMesh, ToolSelectLassoXrayObject)


def register() -> None:
    # Set tool keymap to match the add-on preferences adv. keymap tab
    ToolSelectBoxXrayMesh.bl_keymap = get_tool_keymap_from_preferences("mesh.select_box_xray")
    ToolSelectBoxXrayObject.bl_keymap = get_tool_keymap_from_preferences("object.select_box_xray")

    ToolSelectCircleXrayMesh.bl_keymap = get_tool_keymap_from_preferences("mesh.select_circle_xray")
    ToolSelectCircleXrayObject.bl_keymap = get_tool_keymap_from_preferences("object.select_circle_xray")

    ToolSelectLassoXrayMesh.bl_keymap = get_tool_keymap_from_preferences("mesh.select_lasso_xray")
    ToolSelectLassoXrayObject.bl_keymap = get_tool_keymap_from_preferences("object.select_lasso_xray")

    for box_tool, circle_tool, lasso_tool, use_builtins in zip(
        BOX_TOOLS,
        CIRCLE_TOOLS,
        LASSO_TOOLS,
        (get_preferences().me_group_with_builtins, get_preferences().ob_group_with_builtins),
    ):
        # Add to the builtin selection tool group
        if use_builtins:
            bpy.utils.register_tool(box_tool, after={"builtin.select_box"})
            bpy.utils.register_tool(circle_tool, after={"builtin.select_circle"})
            bpy.utils.register_tool(lasso_tool, after={"builtin.select_lasso"})
        # Create a new selection tool group
        else:
            bpy.utils.register_tool(box_tool, after={"builtin.select"}, group=True)
            bpy.utils.register_tool(circle_tool, after={box_tool.bl_idname})
            bpy.utils.register_tool(lasso_tool, after={circle_tool.bl_idname})

            # Fixing order
            fix_ordering(box_tool.bl_context_mode)

    # Fallback keymap - keymap for tool used as fallback tool
    add_fallback_keymap(FALLBACK_KEYMAP_DICT)
    add_fallback_keymap_items(FALLBACK_KEYMAP_DICT)


def unregister() -> None:
    remove_fallback_keymap_items(FALLBACK_KEYMAP_DICT)

    for tool in itertools.chain(BOX_TOOLS, CIRCLE_TOOLS, LASSO_TOOLS):
        bpy.utils.unregister_tool(tool)
