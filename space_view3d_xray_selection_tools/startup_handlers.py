import bpy

from . import addon_info
from .tools import tools_utils


def _activate_tool():
    idname_by_enum = {
        'BOX': "select_box_xray",
        'CIRCLE': "select_circle_xray",
        'LASSO': "select_lasso_xray",
    }
    me_tool_to_activate = addon_info.get_preferences().mesh_tools.tool_to_activate
    ob_tool_to_activate = addon_info.get_preferences().object_tools.tool_to_activate

    if me_tool_to_activate != 'NONE':
        tools_utils.set_tool_in_mode('EDIT_MESH', f"mesh_tool.{idname_by_enum[me_tool_to_activate]}")
    if ob_tool_to_activate != 'NONE':
        tools_utils.set_tool_in_mode('OBJECT', f"object_tool.{idname_by_enum[ob_tool_to_activate]}")

    if me_tool_to_activate != 'NONE' or ob_tool_to_activate != 'NONE':
        for workspace in bpy.data.workspaces:
            for screen in workspace.screens:
                for area in screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()


def _activate_tool_on_startup(_):
    if _activate_tool_on_startup in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(_activate_tool_on_startup)

    _activate_tool()


@bpy.app.handlers.persistent
def _activate_tool_on_file_load(_) -> None:
    _activate_tool()


def register():
    if not _activate_tool_on_startup in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(_activate_tool_on_startup)

    if not _activate_tool_on_file_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_activate_tool_on_file_load)


def unregister():
    if _activate_tool_on_startup in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(_activate_tool_on_startup)

    if _activate_tool_on_file_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_activate_tool_on_file_load)
