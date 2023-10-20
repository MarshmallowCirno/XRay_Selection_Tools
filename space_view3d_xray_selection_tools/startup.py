import bpy

from bpy.app.handlers import persistent

from .functions.toolbar import set_tool_in_mode
from .preferences import get_preferences


def activate_tool():

    idname_by_enum = {
        'BOX': "select_box_xray",
        'CIRCLE': "select_circle_xray",
        'LASSO': "select_lasso_xray",
    }
    me_tool_to_activate = get_preferences().me_tool_to_activate
    ob_tool_to_activate = get_preferences().ob_tool_to_activate

    if me_tool_to_activate != 'NONE':
        set_tool_in_mode('EDIT_MESH', f"mesh_tool.{idname_by_enum[me_tool_to_activate]}")
    if ob_tool_to_activate != 'NONE':
        set_tool_in_mode('OBJECT', f"object_tool.{idname_by_enum[ob_tool_to_activate]}")

    if me_tool_to_activate != 'NONE' or ob_tool_to_activate != 'NONE':
        for workspace in bpy.data.workspaces:
            for screen in workspace.screens:
                for area in screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()


def activate_tool_on_startup(_):
    if activate_tool_on_startup in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(activate_tool_on_startup)

    activate_tool()


@persistent
def activate_tool_on_file_load(_):
    activate_tool()


def register():
    if not activate_tool_on_startup in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(activate_tool_on_startup)

    if not activate_tool_on_file_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(activate_tool_on_file_load)


def unregister():
    if activate_tool_on_startup in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(activate_tool_on_startup)

    if activate_tool_on_file_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(activate_tool_on_file_load)
