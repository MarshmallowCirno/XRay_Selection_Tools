from pathlib import Path

import bpy
from bl_ui.space_toolsystem_common import activate_by_id, ToolDef, ToolSelectPanelHelper

# Constants
ICON_PATH = Path(__file__).parent.parent / "icon"
EDIT_GPENCIL = 'EDIT_GREASE_PENCIL' if bpy.app.version >= (4, 3, 0) else 'EDIT_GPENCIL'
EDIT_MODES = [
    'EDIT_MESH',
    'OBJECT',
    'EDIT_CURVE',
    'EDIT_ARMATURE',
    'EDIT_METABALL',
    'EDIT_LATTICE',
    'POSE',
    EDIT_GPENCIL,
]


def fix_ordering(bl_context_mode: str) -> None:
    """
    For some reason addon tool group is placed after cursor tool. So swap them.
    """
    # noinspection PyProtectedMember, PyUnresolvedReferences
    cls = ToolSelectPanelHelper._tool_class_from_space_type('VIEW_3D')
    tools = cls._tools[bl_context_mode]

    has_enough_tools = len(tools) >= 2
    item1_is_tool = isinstance(tools[1], ToolDef) and tools[1].idname == "builtin.cursor"
    item2_is_group = hasattr(tools[2], '__len__') and len(tools[2]) >= 1
    item2_subitem_is_tool = isinstance(tools[2][0], ToolDef) and tools[2][0].idname.endswith("_box_xray")

    if has_enough_tools and item1_is_tool and item2_is_group and item2_subitem_is_tool:
        tools[1], tools[2] = tools[2], tools[1]


def reset_active_tool() -> None:
    """
    Resets the active tool to the default 'builtin.select' for all used modes.
    """
    for mode in EDIT_MODES:
        set_tool_in_mode(mode, "bultin.select")

    # Fallback.
    # noinspection PyProtectedMember, PyUnresolvedReferences
    cls = ToolSelectPanelHelper._tool_class_from_space_type('VIEW_3D')
    cls._tool_group_active = {"bultin.select": 1}


def set_tool_in_mode(mode, idname) -> None:

    def _make_func_dict(d=None, **kwargs):
        if d is None:
            d = {}

        def func_dict(d=d, **kwargs):
            func_dict.__dict__.update(d)
            func_dict.__dict__.update(kwargs)
            return func_dict.__dict__

        func_dict(d, **kwargs)
        return func_dict

    for workspace in bpy.data.workspaces:
        # active_tool = workspace.tools.from_space_view3d_mode(mode)
        # as_fallback = False
        # if active_tool:
        #     if active_tool.idname in {"builtin.move", "bultin.rotate", "builtin.scale", "builtin.transform"}:
        #         as_fallback = True

        context_override = {"workspace": workspace, "mode": mode}
        context_override = _make_func_dict(context_override)
        activate_by_id(context_override, space_type='VIEW_3D', idname=idname, as_fallback=False)
