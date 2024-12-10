import itertools

import bpy

from .tools_keymap import (
    add_fallback_keymap,
    add_fallback_keymap_items,
    DUMMY_FALLBACK_KEYMAP_DICT,
    get_tool_keymap_from_preferences,
    remove_fallback_keymap_items,
)
from .tools_utils import EDIT_GPENCIL, fix_ordering, ICON_PATH
from ..preferences import get_preferences


# Box Tools


class ToolSelectBoxXrayTemplate(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode: str

    bl_idname: str
    bl_label = "Select Box X-Ray"
    bl_description = "Select items using box selection"
    bl_icon = str(ICON_PATH / "addon.select_box_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_box"
    bl_keymap: tuple

    # noinspection PyMethodMayBeStatic, PyMethodParameters
    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_box")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True, icon_only=True)


class ToolSelectBoxXrayCurve(ToolSelectBoxXrayTemplate):
    bl_context_mode = 'EDIT_CURVE'
    bl_idname = "curve_tool.select_box_xray"


class ToolSelectBoxXrayArmature(ToolSelectBoxXrayTemplate):
    bl_context_mode = 'EDIT_ARMATURE'
    bl_idname = "armature_tool.select_box_xray"


class ToolSelectBoxXrayMetaball(ToolSelectBoxXrayTemplate):
    bl_context_mode = 'EDIT_METABALL'
    bl_idname = "metaball_tool.select_box_xray"


class ToolSelectBoxXrayLattice(ToolSelectBoxXrayTemplate):
    bl_context_mode = 'EDIT_LATTICE'
    bl_idname = "lattice_tool.select_box_xray"


class ToolSelectBoxXrayPose(ToolSelectBoxXrayTemplate):
    bl_context_mode = 'POSE'
    bl_idname = "pose_tool.select_box_xray"


class ToolSelectBoxXrayGrease(ToolSelectBoxXrayTemplate):
    bl_context_mode = EDIT_GPENCIL
    bl_idname = "grease_tool.select_box_xray"


# Circle Tools


class ToolSelectCircleXrayTemplate(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode: str

    bl_idname: str
    bl_label = "Select Circle X-Ray"
    bl_description = "Select items using circle selection"
    bl_icon = str(ICON_PATH / "addon.select_circle_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_circle"
    bl_keymap: tuple

    # noinspection PyMethodMayBeStatic, PyMethodParameters
    def draw_cursor(context, tool, xy):
        from gpu_extras.presets import draw_circle_2d

        props = tool.operator_properties("view3d.select_circle")
        radius = props.radius
        draw_circle_2d(xy, (1.0,) * 4, radius, segments=32)

    # noinspection PyMethodMayBeStatic, PyMethodParameters
    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_circle")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True, icon_only=True)

        layout.prop(tool.operator_properties("view3d.select_circle"), "radius")


class ToolSelectCircleXrayCurve(ToolSelectCircleXrayTemplate):
    bl_context_mode = 'EDIT_CURVE'
    bl_idname = "curve_tool.select_circle_xray"


class ToolSelectCircleXrayArmature(ToolSelectCircleXrayTemplate):
    bl_context_mode = 'EDIT_ARMATURE'
    bl_idname = "armature_tool.select_circle_xray"


class ToolSelectCircleXrayMetaball(ToolSelectCircleXrayTemplate):
    bl_context_mode = 'EDIT_METABALL'
    bl_idname = "metaball_tool.select_circle_xray"


class ToolSelectCircleXrayLattice(ToolSelectCircleXrayTemplate):
    bl_context_mode = 'EDIT_LATTICE'
    bl_idname = "lattice_tool.select_circle_xray"


class ToolSelectCircleXrayPose(ToolSelectCircleXrayTemplate):
    bl_context_mode = 'POSE'
    bl_idname = "pose_tool.select_circle_xray"


class ToolSelectCircleXrayGrease(ToolSelectCircleXrayTemplate):
    bl_context_mode = EDIT_GPENCIL
    bl_idname = "grease_tool.select_circle_xray"


# Lasso Tools


class ToolSelectLassoXrayTemplate(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode: str

    bl_idname: str
    bl_label = "Select Lasso X-Ray"
    bl_description = "Select items using lasso selection"
    bl_icon = str(ICON_PATH / "addon.select_lasso_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_lasso"
    bl_keymap = tuple

    # noinspection PyMethodMayBeStatic, PyMethodParameters
    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_lasso")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True, icon_only=True)


class ToolSelectLassoXrayCurve(ToolSelectLassoXrayTemplate):
    bl_context_mode = 'EDIT_CURVE'
    bl_idname = "curve_tool.select_lasso_xray"


class ToolSelectLassoXrayArmature(ToolSelectLassoXrayTemplate):
    bl_context_mode = 'EDIT_ARMATURE'
    bl_idname = "armature_tool.select_lasso_xray"


class ToolSelectLassoXrayMetaball(ToolSelectLassoXrayTemplate):
    bl_context_mode = 'EDIT_METABALL'
    bl_idname = "metaball_tool.select_lasso_xray"


class ToolSelectLassoXrayLattice(ToolSelectLassoXrayTemplate):
    bl_context_mode = 'EDIT_LATTICE'
    bl_idname = "lattice_tool.select_lasso_xray"


class ToolSelectLassoXrayPose(ToolSelectLassoXrayTemplate):
    bl_context_mode = 'POSE'
    bl_idname = "pose_tool.select_lasso_xray"


class ToolSelectLassoXrayGrease(ToolSelectLassoXrayTemplate):
    bl_context_mode = EDIT_GPENCIL
    bl_idname = "grease_tool.select_lasso_xray"


box_tools = (
    ToolSelectBoxXrayCurve,
    ToolSelectBoxXrayArmature,
    ToolSelectBoxXrayMetaball,
    ToolSelectBoxXrayLattice,
    ToolSelectBoxXrayPose,
    ToolSelectBoxXrayGrease,
)
circle_tools = (
    ToolSelectCircleXrayCurve,
    ToolSelectCircleXrayArmature,
    ToolSelectCircleXrayMetaball,
    ToolSelectCircleXrayLattice,
    ToolSelectCircleXrayPose,
    ToolSelectCircleXrayGrease,
)
lasso_tools = (
    ToolSelectLassoXrayCurve,
    ToolSelectLassoXrayArmature,
    ToolSelectLassoXrayMetaball,
    ToolSelectLassoXrayLattice,
    ToolSelectLassoXrayPose,
    ToolSelectLassoXrayGrease,
)


def register() -> None:
    # Set tool keymap to match the add-on preferences adv. keymap tab
    box_tool_keymap = get_tool_keymap_from_preferences("view3d.select_box")
    for tool in box_tools:
        tool.bl_keymap = box_tool_keymap

    circle_tool_keymap = get_tool_keymap_from_preferences("view3d.select_box")
    for tool in circle_tools:
        tool.bl_keymap = circle_tool_keymap

    lasso_tool_keymap = get_tool_keymap_from_preferences("view3d.select_lasso")
    for tool in lasso_tools:
        tool.bl_keymap = lasso_tool_keymap

    # Add to the builtin selection tool group
    if get_preferences().me_group_with_builtins:
        for tool in box_tools:
            bpy.utils.register_tool(tool, after={"builtin.select_box"})
        for tool in circle_tools:
            bpy.utils.register_tool(tool, after={"builtin.select_circle"})
        for tool in lasso_tools:
            bpy.utils.register_tool(tool, after={"builtin.select_lasso"})
    # Create a new selection tool group
    else:
        for box_tool, circle_tool, lasso_tool in zip(box_tools, circle_tools, lasso_tools):
            bpy.utils.register_tool(box_tool, after={"builtin.select"}, group=True)
            bpy.utils.register_tool(circle_tool, after={box_tool.bl_idname})
            bpy.utils.register_tool(lasso_tool, after={circle_tool.bl_idname})

            # Fixing order
            fix_ordering(box_tool.bl_context_mode)

    # Fallback keymap - keymap for tool used as fallback tool
    add_fallback_keymap(DUMMY_FALLBACK_KEYMAP_DICT)
    add_fallback_keymap_items(DUMMY_FALLBACK_KEYMAP_DICT)


def unregister() -> None:
    remove_fallback_keymap_items(DUMMY_FALLBACK_KEYMAP_DICT)

    for tool in itertools.chain(box_tools, circle_tools, lasso_tools):
        bpy.utils.unregister_tool(tool)
