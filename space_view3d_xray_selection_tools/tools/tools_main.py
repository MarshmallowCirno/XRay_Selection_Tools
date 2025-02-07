import itertools

import bpy

from .. import addon_info
from . import tools_keymap, tools_utils

# Box Tools


class ToolSelectBoxXrayMesh(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_MESH'

    bl_idname = "mesh_tool.select_box_xray"
    bl_label = "Select Box X-Ray"
    bl_description = "Select items using box selection with x-ray"
    bl_icon = str(tools_utils.ICON_PATH / "addon.select_box_xray_icon")
    bl_widget = None
    bl_operator = "mesh.select_box_xray"
    bl_keymap: tuple

    # noinspection PyMethodMayBeStatic, PyMethodParameters
    def draw_settings(context, layout, tool):
        cur_tool_props = tool.operator_properties("mesh.select_box_xray")
        global_tools_props = addon_info.get_preferences().mesh_tools

        row = layout.row()
        row.use_property_split = False
        row.prop(cur_tool_props, "mode", text="", expand=True, icon_only=True)

        sub = row.row(align=True)
        sub.prop(global_tools_props, "select_through", icon='XRAY', toggle=True)
        sub = sub.row(align=True)
        sub.active = global_tools_props.select_through
        sub.prop(global_tools_props, "select_backfacing", icon='NORMALS_FACE', toggle=True)


class ToolSelectBoxXrayObject(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'

    bl_idname = "object_tool.select_box_xray"
    bl_label = "Select Box X-Ray"
    bl_description = "Select items using box selection with x-ray"
    bl_icon = str(tools_utils.ICON_PATH / "addon.select_box_xray_icon")
    bl_widget = None
    bl_operator = "object.select_box_xray"
    bl_keymap: tuple

    # noinspection PyMethodMayBeStatic, PyMethodParameters
    def draw_settings(context, layout, tool):
        cur_tool_props = tool.operator_properties("object.select_box_xray")

        row = layout.row()
        row.use_property_split = False
        row.prop(cur_tool_props, "mode", text="", expand=True, icon_only=True)


# Circle Tools


class ToolSelectCircleXrayMesh(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_MESH'

    bl_idname = "mesh_tool.select_circle_xray"
    bl_label = "Select Circle X-Ray"
    bl_description = "Select items using circle selection with x-ray"
    bl_icon = str(tools_utils.ICON_PATH / "addon.select_circle_xray_icon")
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
        cur_tool_props = tool.operator_properties("mesh.select_circle_xray")
        global_tools_props = addon_info.get_preferences().mesh_tools

        row = layout.row()
        row.use_property_split = False
        row.prop(global_tools_props, "mode", text="", expand=True, icon_only=True)

        sub = row.row(align=True)
        sub.prop(global_tools_props, "select_through", icon='XRAY', toggle=True)
        sub = sub.row(align=True)
        sub.active = global_tools_props.select_through
        sub.prop(global_tools_props, "select_backfacing", icon='NORMALS_FACE', toggle=True)

        layout.prop(cur_tool_props, "radius")


class ToolSelectCircleXrayObject(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'

    bl_idname = "object_tool.select_circle_xray"
    bl_label = "Select Circle X-Ray"
    bl_description = "Select items using circle selection with x-ray"
    bl_icon = str(tools_utils.ICON_PATH / "addon.select_circle_xray_icon")
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
        cur_tool_props = tool.operator_properties("object.select_circle_xray")

        row = layout.row()
        row.use_property_split = False
        row.prop(cur_tool_props, "mode", text="", expand=True, icon_only=True)

        layout.prop(cur_tool_props, "radius")


# Lasso Tools


class ToolSelectLassoXrayMesh(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_MESH'

    bl_idname = "mesh_tool.select_lasso_xray"
    bl_label = "Select Lasso X-Ray"
    bl_description = "Select items using lasso selection with x-ray"
    bl_icon = str(tools_utils.ICON_PATH / "addon.select_lasso_xray_icon")
    bl_widget = None
    bl_operator = "mesh.select_lasso_xray"
    bl_keymap: tuple

    # noinspection PyMethodMayBeStatic, PyMethodParameters
    def draw_settings(context, layout, tool):
        cur_tool_props = tool.operator_properties("mesh.select_lasso_xray")
        global_tools_props = addon_info.get_preferences().mesh_tools

        row = layout.row()
        row.use_property_split = False
        row.prop(cur_tool_props, "mode", text="", expand=True, icon_only=True)

        sub = row.row(align=True)
        sub.prop(global_tools_props, "select_through", icon='XRAY', toggle=True)
        sub = sub.row(align=True)
        sub.active = global_tools_props.select_through
        sub.prop(global_tools_props, "select_backfacing", icon='NORMALS_FACE', toggle=True)


class ToolSelectLassoXrayObject(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'

    bl_idname = "object_tool.select_lasso_xray"
    bl_label = "Select Lasso X-Ray"
    bl_description = "Select items using lasso selection with x-ray"
    bl_icon = str(tools_utils.ICON_PATH / "addon.select_lasso_xray_icon")
    bl_widget = None
    bl_operator = "object.select_lasso_xray"
    bl_keymap: tuple

    # noinspection PyMethodMayBeStatic, PyMethodParameters
    def draw_settings(context, layout, tool):
        cur_tool_props = tool.operator_properties("object.select_lasso_xray")

        row = layout.row()
        row.use_property_split = False
        row.prop(cur_tool_props, "mode", text="", expand=True, icon_only=True)


_BOX_TOOLS = (ToolSelectBoxXrayMesh, ToolSelectBoxXrayObject)
_CIRCLE_TOOLS = (ToolSelectCircleXrayMesh, ToolSelectCircleXrayObject)
_LASSO_TOOLS = (ToolSelectLassoXrayMesh, ToolSelectLassoXrayObject)


def register() -> None:
    # Set tool keymap to match the add-on preferences adv. keymap tab
    ToolSelectBoxXrayMesh.bl_keymap = tools_keymap.get_tool_keymap_from_preferences("mesh.select_box_xray")
    ToolSelectBoxXrayObject.bl_keymap = tools_keymap.get_tool_keymap_from_preferences("object.select_box_xray")

    ToolSelectCircleXrayMesh.bl_keymap = tools_keymap.get_tool_keymap_from_preferences("mesh.select_circle_xray")
    ToolSelectCircleXrayObject.bl_keymap = tools_keymap.get_tool_keymap_from_preferences("object.select_circle_xray")

    ToolSelectLassoXrayMesh.bl_keymap = tools_keymap.get_tool_keymap_from_preferences("mesh.select_lasso_xray")
    ToolSelectLassoXrayObject.bl_keymap = tools_keymap.get_tool_keymap_from_preferences("object.select_lasso_xray")

    for box_tool, circle_tool, lasso_tool, use_builtins in zip(
        _BOX_TOOLS,
        _CIRCLE_TOOLS,
        _LASSO_TOOLS,
        (
            addon_info.get_preferences().mesh_tools.group_with_builtins,
            addon_info.get_preferences().object_tools.group_with_builtins,
        ),
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
            tools_utils.fix_ordering(box_tool.bl_context_mode)

    # Fallback keymap - keymap for tool used as fallback tool
    tools_keymap.add_fallback_keymap(tools_keymap.FALLBACK_KEYMAP_DICT)
    tools_keymap.add_fallback_keymap_items(tools_keymap.FALLBACK_KEYMAP_DICT)


def unregister() -> None:
    tools_keymap.remove_fallback_keymap_items(tools_keymap.FALLBACK_KEYMAP_DICT)

    for tool in itertools.chain(_BOX_TOOLS, _CIRCLE_TOOLS, _LASSO_TOOLS):
        bpy.utils.unregister_tool(tool)
