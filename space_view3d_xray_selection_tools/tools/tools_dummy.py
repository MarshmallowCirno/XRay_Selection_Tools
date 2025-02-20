from collections.abc import Sequence
from typing import cast

import bpy

from .. import addon_info
from . import tools_keymap, tools_utils

# Box Tools


class _ToolSelectBoxXrayTemplate(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode: str

    bl_idname: str
    bl_label = "Select Box X-Ray"
    bl_description = "Select items using box selection"
    bl_icon = str(tools_utils.ICON_PATH / "addon.select_box_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_box"
    bl_keymap: tuple[tools_keymap.WorkSpaceToolKeyMapItem, ...]

    @staticmethod
    def draw_settings(_context: bpy.types.Context, layout: bpy.types.UILayout, tool: bpy.types.WorkSpaceTool) -> None:
        cur_tool_props = tool.operator_properties("view3d.select_box")
        row = layout.row()
        row.use_property_split = False
        row.prop(cur_tool_props, "mode", text="", expand=True, icon_only=True)


class ToolSelectBoxXrayCurve(_ToolSelectBoxXrayTemplate):
    bl_context_mode = 'EDIT_CURVE'
    bl_idname = "curve_tool.select_box_xray"


class ToolSelectBoxXrayArmature(_ToolSelectBoxXrayTemplate):
    bl_context_mode = 'EDIT_ARMATURE'
    bl_idname = "armature_tool.select_box_xray"


class ToolSelectBoxXrayMetaball(_ToolSelectBoxXrayTemplate):
    bl_context_mode = 'EDIT_METABALL'
    bl_idname = "metaball_tool.select_box_xray"


class ToolSelectBoxXrayLattice(_ToolSelectBoxXrayTemplate):
    bl_context_mode = 'EDIT_LATTICE'
    bl_idname = "lattice_tool.select_box_xray"


class ToolSelectBoxXrayPose(_ToolSelectBoxXrayTemplate):
    bl_context_mode = 'POSE'
    bl_idname = "pose_tool.select_box_xray"


class ToolSelectBoxXrayGrease(_ToolSelectBoxXrayTemplate):
    bl_context_mode = tools_utils.EDIT_GPENCIL
    bl_idname = "grease_tool.select_box_xray"


# Circle Tools


class _ToolSelectCircleXrayTemplate(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode: str

    bl_idname: str
    bl_label = "Select Circle X-Ray"
    bl_description = "Select items using circle selection"
    bl_icon = str(tools_utils.ICON_PATH / "addon.select_circle_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_circle"
    bl_keymap: tuple[tools_keymap.WorkSpaceToolKeyMapItem, ...]

    @staticmethod
    def draw_cursor(_context: bpy.types.Context, tool: bpy.types.WorkSpaceTool, xy: Sequence[float]) -> None:
        from gpu_extras.presets import draw_circle_2d  # pyright: ignore[reportUnknownVariableType]

        op_props = tool.operator_properties("view3d.select_circle")
        radius = cast(int, op_props.radius)  # pyright: ignore[reportAttributeAccessIssue]
        draw_circle_2d(xy, (1.0,) * 4, radius, segments=32)

    @staticmethod
    def draw_settings(_context: bpy.types.Context, layout: bpy.types.UILayout, tool: bpy.types.WorkSpaceTool) -> None:
        op_props = tool.operator_properties("view3d.select_circle")

        row = layout.row()
        row.use_property_split = False
        row.prop(op_props, "mode", text="", expand=True, icon_only=True)

        layout.prop(op_props, "radius")


class ToolSelectCircleXrayCurve(_ToolSelectCircleXrayTemplate):
    bl_context_mode = 'EDIT_CURVE'
    bl_idname = "curve_tool.select_circle_xray"


class ToolSelectCircleXrayArmature(_ToolSelectCircleXrayTemplate):
    bl_context_mode = 'EDIT_ARMATURE'
    bl_idname = "armature_tool.select_circle_xray"


class ToolSelectCircleXrayMetaball(_ToolSelectCircleXrayTemplate):
    bl_context_mode = 'EDIT_METABALL'
    bl_idname = "metaball_tool.select_circle_xray"


class ToolSelectCircleXrayLattice(_ToolSelectCircleXrayTemplate):
    bl_context_mode = 'EDIT_LATTICE'
    bl_idname = "lattice_tool.select_circle_xray"


class ToolSelectCircleXrayPose(_ToolSelectCircleXrayTemplate):
    bl_context_mode = 'POSE'
    bl_idname = "pose_tool.select_circle_xray"


class ToolSelectCircleXrayGrease(_ToolSelectCircleXrayTemplate):
    bl_context_mode = tools_utils.EDIT_GPENCIL
    bl_idname = "grease_tool.select_circle_xray"


# Lasso Tools


class _ToolSelectLassoXrayTemplate(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode: str

    bl_idname: str
    bl_label = "Select Lasso X-Ray"
    bl_description = "Select items using lasso selection"
    bl_icon = str(tools_utils.ICON_PATH / "addon.select_lasso_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_lasso"
    bl_keymap: tuple[tools_keymap.WorkSpaceToolKeyMapItem, ...]

    @staticmethod
    def draw_settings(_context: bpy.types.Context, layout: bpy.types.UILayout, tool: bpy.types.WorkSpaceTool) -> None:
        op_props = tool.operator_properties("view3d.select_lasso")

        row = layout.row()
        row.use_property_split = False
        row.prop(op_props, "mode", text="", expand=True, icon_only=True)


class ToolSelectLassoXrayCurve(_ToolSelectLassoXrayTemplate):
    bl_context_mode = 'EDIT_CURVE'
    bl_idname = "curve_tool.select_lasso_xray"


class ToolSelectLassoXrayArmature(_ToolSelectLassoXrayTemplate):
    bl_context_mode = 'EDIT_ARMATURE'
    bl_idname = "armature_tool.select_lasso_xray"


class ToolSelectLassoXrayMetaball(_ToolSelectLassoXrayTemplate):
    bl_context_mode = 'EDIT_METABALL'
    bl_idname = "metaball_tool.select_lasso_xray"


class ToolSelectLassoXrayLattice(_ToolSelectLassoXrayTemplate):
    bl_context_mode = 'EDIT_LATTICE'
    bl_idname = "lattice_tool.select_lasso_xray"


class ToolSelectLassoXrayPose(_ToolSelectLassoXrayTemplate):
    bl_context_mode = 'POSE'
    bl_idname = "pose_tool.select_lasso_xray"


class ToolSelectLassoXrayGrease(_ToolSelectLassoXrayTemplate):
    bl_context_mode = tools_utils.EDIT_GPENCIL
    bl_idname = "grease_tool.select_lasso_xray"


_box_tools = (
    ToolSelectBoxXrayCurve,
    ToolSelectBoxXrayArmature,
    ToolSelectBoxXrayMetaball,
    ToolSelectBoxXrayLattice,
    ToolSelectBoxXrayPose,
    ToolSelectBoxXrayGrease,
)
_circle_tools = (
    ToolSelectCircleXrayCurve,
    ToolSelectCircleXrayArmature,
    ToolSelectCircleXrayMetaball,
    ToolSelectCircleXrayLattice,
    ToolSelectCircleXrayPose,
    ToolSelectCircleXrayGrease,
)
_lasso_tools = (
    ToolSelectLassoXrayCurve,
    ToolSelectLassoXrayArmature,
    ToolSelectLassoXrayMetaball,
    ToolSelectLassoXrayLattice,
    ToolSelectLassoXrayPose,
    ToolSelectLassoXrayGrease,
)


def register() -> None:
    # Set tool keymap to match the add-on preferences adv. keymap tab
    box_tool_keymap = tools_keymap.keymap_from_addon_preferences("view3d.select_box")
    for tool in _box_tools:
        tool.bl_keymap = box_tool_keymap

    circle_tool_keymap = tools_keymap.keymap_from_addon_preferences("view3d.select_circle")
    for tool in _circle_tools:
        tool.bl_keymap = circle_tool_keymap

    lasso_tool_keymap = tools_keymap.keymap_from_addon_preferences("view3d.select_lasso")
    for tool in _lasso_tools:
        tool.bl_keymap = lasso_tool_keymap

    # Add to the builtin selection tool group
    if addon_info.get_preferences().mesh_tools.group_with_builtins:
        for tool in _box_tools:
            bpy.utils.register_tool(tool, after=("builtin.select_box",))
        for tool in _circle_tools:
            bpy.utils.register_tool(tool, after=("builtin.select_circle",))
        for tool in _lasso_tools:
            bpy.utils.register_tool(tool, after=("builtin.select_lasso",))
    # Create a new selection tool group
    else:
        for box_tool, circle_tool, lasso_tool in zip(_box_tools, _circle_tools, _lasso_tools):
            bpy.utils.register_tool(box_tool, after=("builtin.select",), group=True)
            bpy.utils.register_tool(circle_tool, after=(box_tool.bl_idname,))
            bpy.utils.register_tool(lasso_tool, after=(circle_tool.bl_idname,))

            # Fixing order
            tools_utils.fix_ordering(box_tool.bl_context_mode)

    # Fallback keymap - keymap for tool used as fallback tool
    tools_keymap.add_fallback_keymaps(tools_keymap.DUMMY_FALLBACK_KEYMAP_TEMPLATES)
    tools_keymap.add_fallback_keymap_items(tools_keymap.DUMMY_FALLBACK_KEYMAP_TEMPLATES)


def unregister() -> None:
    tools_keymap.clear_fallback_keymaps(tools_keymap.DUMMY_FALLBACK_KEYMAP_TEMPLATES)

    for tool in (*_box_tools, *_circle_tools, *_lasso_tools):
        bpy.utils.unregister_tool(tool)
