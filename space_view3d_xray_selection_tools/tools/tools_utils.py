import pathlib
from types import SimpleNamespace
from typing import cast

import bpy
from bl_ui import space_toolsystem_common, space_toolsystem_toolbar

# Constants
ICON_PATH = pathlib.Path(__file__).parent.parent / "icon"
EDIT_GPENCIL = 'EDIT_GREASE_PENCIL' if bpy.app.version >= (4, 3, 0) else 'EDIT_GPENCIL'
_TOOLS_CONTEXT_MODES = (
    'OBJECT',
    'EDIT_MESH',
    'EDIT_CURVE',
    'EDIT_ARMATURE',
    'EDIT_METABALL',
    'EDIT_LATTICE',
    EDIT_GPENCIL,
    'POSE',
)


def fix_ordering(bl_context_mode: str) -> None:
    """
    For some reason addon tool group is placed after cursor tool. So swap them.
    """
    # noinspection PyProtectedMember
    cls = cast(
        space_toolsystem_toolbar.VIEW3D_PT_tools_active | None,
        space_toolsystem_common.ToolSelectPanelHelper._tool_class_from_space_type('VIEW_3D'),  # pyright: ignore [reportAttributeAccessIssue]
    )
    if cls is None:
        return
    tools = cast(
        list[space_toolsystem_common.ToolDef | tuple[space_toolsystem_common.ToolDef, ...] | None],
        cls._tools[bl_context_mode],  # pyright: ignore [reportAttributeAccessIssue]
    )

    # Toolbar has enough tools
    if len(tools) < 2:
        return
    # Item #1 is the cursor tool
    if not isinstance(tools[1], space_toolsystem_common.ToolDef) or tools[1].idname != "builtin.cursor":
        return
    # Item #2 is non-empty tool group
    if not isinstance(tools[2], tuple) or len(tools[2]) == 0:
        return
    # Item #2 has xray selection tools
    if not tools[2][0].idname.endswith("_box_xray"):
        return
    tools[1], tools[2] = tools[2], tools[1]


def reset_active_tool() -> None:
    """
    Resets the active tool to the default 'builtin.select' for all used modes.
    """
    for mode in _TOOLS_CONTEXT_MODES:
        set_tool_in_mode(mode, "bultin.select")

    # Fallback.
    # noinspection PyProtectedMember
    cls = cast(
        space_toolsystem_toolbar.VIEW3D_PT_tools_active | None,
        space_toolsystem_common.ToolSelectPanelHelper._tool_class_from_space_type('VIEW_3D'),  # pyright: ignore[reportAttributeAccessIssue]
    )
    if cls is None:
        return
    cls._tool_group_active = {"bultin.select": 1}  # pyright: ignore[reportAttributeAccessIssue]


def set_tool_in_mode(mode: str, idname: str) -> None:
    for workspace in bpy.data.workspaces:
        # active_tool = workspace.tools.from_space_view3d_mode(mode)
        # as_fallback = False
        # if active_tool:
        #     if active_tool.idname in {"builtin.move", "bultin.rotate", "builtin.scale", "builtin.transform"}:
        #         as_fallback = True

        data = {"workspace": workspace, "mode": mode}
        context_override = SimpleNamespace(**data)
        space_toolsystem_common.activate_by_id(context_override, space_type='VIEW_3D', idname=idname, as_fallback=False)
