import bpy

from bl_ui.space_toolsystem_common import activate_by_id


def make_func_dict(d=None, **kwargs):
    if d is None:
        d = {}

    def func_dict(d=d, **kwargs):
        func_dict.__dict__.update(d)
        func_dict.__dict__.update(kwargs)
        return func_dict.__dict__

    func_dict(d, **kwargs)
    return func_dict


def set_tool_in_mode(mode, idname) -> None:
    for workspace in bpy.data.workspaces:
        # active_tool = workspace.tools.from_space_view3d_mode(mode)
        # as_fallback = False
        # if active_tool:
        #     if active_tool.idname in {"builtin.move", "bultin.rotate", "builtin.scale", "builtin.transform"}:
        #         as_fallback = True

        context_override = {"workspace": workspace, "mode": mode}
        context_override = make_func_dict(context_override)
        activate_by_id(context_override, space_type='VIEW_3D', idname=idname, as_fallback=False)
