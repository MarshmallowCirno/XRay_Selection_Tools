from typing import TYPE_CHECKING, Literal

import bpy

from ... import tools


class ToolsSharedPreferences:
    if TYPE_CHECKING:
        hide_gizmo: bool
        show_crosshair: bool
        show_lasso_icon: bool
        tool_to_activate: Literal['NONE', 'BOX', 'CIRCLE', 'LASSO']
        group_with_builtins: bool
    else:
        hide_gizmo: bpy.props.BoolProperty(
            name="Hide Gizmo",
            description="Temporarily hide the gizmo of the active tool during selection",
            default=False,
        )

        show_crosshair: bpy.props.BoolProperty(
            name="Show Crosshair",
            description="Display the crosshair when wait_for_input is enabled",
            default=True,
        )
        show_lasso_icon: bpy.props.BoolProperty(
            name="Show Lasso Cursor",
            description="Display the lasso cursor icon when wait_for_input is enabled",
            default=True,
        )
        tool_to_activate: bpy.props.EnumProperty(
            name="Activate automatically at startup",
            description="Set this tool as active in toolbar automatically when you start blender or load a save file",
            items=[
                ('NONE', "None", ""),
                ('BOX', "Select Box X-Ray", ""),
                ('CIRCLE', "Select Circle X-Ray", ""),
                ('LASSO', "Select Lasso X-Ray", ""),
            ],
            default='NONE',
        )
        group_with_builtins: bpy.props.BoolProperty(
            name="Directional Box Behavior",
            description="Set tool behavior based on drag direction",
            default=True,
            update=tools.reload_tools,
        )


class XRAYSELToolMeDirectionProps(bpy.types.PropertyGroup):
    """Properties of the mesh tools linked to drag direction."""

    if TYPE_CHECKING:
        select_through: bool
        default_color: tuple[float, float, float]
        select_through_color: tuple[float, float, float]
        directional_lasso_tool: bool
        show_xray: bool
        select_all_edges: bool
        select_all_faces: bool
        select_backfacing: bool
    else:
        select_through: bpy.props.BoolProperty(
            name="Select Through",
            description="Select vertices, faces, and edges laying underneath",
            default=True,
        )
        default_color: bpy.props.FloatVectorProperty(
            name="Default Color",
            description="Color of the selection frame when selecting through",
            subtype='COLOR',
            soft_min=0.0,
            soft_max=1.0,
            size=3,
            default=(1.0, 1.0, 1.0),
        )
        select_through_color: bpy.props.FloatVectorProperty(
            name="Select Through Color",
            description="Color of the selection frame when not selecting through",
            subtype='COLOR',
            soft_min=0.0,
            soft_max=1.0,
            size=3,
            default=(1.0, 1.0, 1.0),
        )
        show_xray: bpy.props.BoolProperty(
            name="Show X-Ray",
            description="Enable X-Ray shading during selection",
            default=True,
        )
        select_all_edges: bpy.props.BoolProperty(
            name="Select All Edges",
            description=(
                "Include edges partially within the selection area, not just those fully enclosed. Works only "
                "in \"Select Through\" mode"
            ),
            default=False,
        )
        select_all_faces: bpy.props.BoolProperty(
            name="Select All Faces",
            description=(
                "Include faces partially within the selection borders, not just those whose centers are inside. "
                "Works only in \"Select Through\" mode"
            ),
            default=False,
        )
        select_backfacing: bpy.props.BoolProperty(
            name="Select Backfacing",
            description="Select elements with normals pointing away from the view. Works only in \"Select Through\" mode",
            default=True,
        )


class XRAYSELMeshToolsPreferencesPG(ToolsSharedPreferences, XRAYSELToolMeDirectionProps):
    """Properties of the mesh tools."""

    if TYPE_CHECKING:
        direction_properties: bpy.types.bpy_prop_collection_idprop[XRAYSELToolMeDirectionProps]
        directional_box_tool: bool
        directional_lasso_tool: bool
        select_through_toggle_key: Literal['CTRL', 'ALT', 'SHIFT', 'OSKEY', 'DISABLED']
        select_through_toggle_type: Literal['HOLD', 'PRESS']
        hide_mirror: bool
        hide_solidify: bool
    else:
        direction_properties: bpy.props.CollectionProperty(
            type=XRAYSELToolMeDirectionProps,
            name="Mesh Direction Props",
        )
        directional_box_tool: bpy.props.BoolProperty(
            name="Directional Box Behavior",
            description="Configure behavior separately for dragging directions",
            default=False,
        )
        directional_lasso_tool: bpy.props.BoolProperty(
            name="Directional Lasso Behavior",
            description="Configure behavior separately for dragging directions",
            default=False,
        )
        select_through_toggle_key: bpy.props.EnumProperty(
            name="Selection Through Toggle Key",
            description="Toggle selection through with this key",
            items=[
                ('CTRL', "CTRL", ""),
                ('ALT', "ALT", ""),
                ('SHIFT', "SHIFT", ""),
                ('OSKEY', "CMD", ""),
                ('DISABLED', "DISABLED", ""),
            ],
            default='DISABLED',
        )
        select_through_toggle_type: bpy.props.EnumProperty(
            name="Toggle Selection Through by Press or Hold",
            description="Toggle selection through by holding or by pressing a key",
            items=[
                ('HOLD', "Holding", ""),
                ('PRESS', "Pressing", ""),
            ],
            default='HOLD',
        )
        hide_mirror: bpy.props.BoolProperty(
            name="Hide Mirror",
            description="Temporarily hide mirror modifiers during selection",
            default=True,
        )
        hide_solidify: bpy.props.BoolProperty(
            name="Hide Solidify",
            description="Temporarily hide solidify modifiers during selection",
            default=True,
        )


class XRAYSELObjectToolsPreferencesPG(bpy.types.PropertyGroup, ToolsSharedPreferences):
    """Properties of the object tools."""

    if TYPE_CHECKING:
        show_xray: bool
        xray_toggle_key: Literal['CTRL', 'ALT', 'SHIFT', 'OSKEY', 'DISABLED']
        xray_toggle_type: Literal['HOLD', 'PRESS']
        box_select_behavior: Literal['ORIGIN', 'CONTAIN', 'OVERLAP', 'DIRECTIONAL', 'DIRECTIONAL_REVERSED']
        circle_select_behavior: Literal['ORIGIN', 'CONTAIN', 'OVERLAP']
        lasso_select_behavior: Literal['ORIGIN', 'CONTAIN', 'OVERLAP', 'DIRECTIONAL', 'DIRECTIONAL_REVERSED']
    else:
        show_xray: bpy.props.BoolProperty(
            name="Show X-Ray",
            description="Enable X-Ray shading during selection",
            default=True,
        )
        xray_toggle_key: bpy.props.EnumProperty(
            name="X-Ray Toggle Key",
            description="Toggle X-Ray with this key",
            items=[
                ('CTRL', "CTRL", ""),
                ('ALT', "ALT", ""),
                ('SHIFT', "SHIFT", ""),
                ('OSKEY', "CMD", ""),
                ('DISABLED', "DISABLED", ""),
            ],
            default='DISABLED',
        )
        xray_toggle_type: bpy.props.EnumProperty(
            name="Toggle X-Ray by Press or Hold",
            description="Toggle X-Ray by holding or by pressing a key",
            items=[
                ('HOLD', "Holding", ""),
                ('PRESS', "Pressing", ""),
            ],
            default='HOLD',
        )
        box_select_behavior: bpy.props.EnumProperty(
            name="Box Select Behavior",
            description="Selection behavior",
            items=[
                (
                    'ORIGIN',
                    "Origin",
                    "Select objects by origins",
                    'DOT',
                    1,
                ),
                (
                    'CONTAIN',
                    "Contain",
                    "Select only the objects fully contained in box",
                    'STICKY_UVS_LOC',
                    2,
                ),
                (
                    'OVERLAP',
                    "Overlap (Default)",
                    "Select objects overlapping box",
                    'SELECT_SUBTRACT',
                    3,
                ),
                (
                    'DIRECTIONAL',
                    "Directional",
                    "Dragging left to right select contained, right to left select overlapped",
                    'UV_SYNC_SELECT',
                    4,
                ),
                (
                    'DIRECTIONAL_REVERSED',
                    "Directional Reversed",
                    "Dragging left to right select overlapped, right to left select contained",
                    'UV_SYNC_SELECT',
                    5,
                ),
            ],
            default='OVERLAP',
        )
        circle_select_behavior: bpy.props.EnumProperty(
            name="Circle Select Behavior",
            description="Selection behavior",
            items=[
                (
                    'ORIGIN',
                    "Origin (Default)",
                    "Select objects by origins",
                    'DOT',
                    1,
                ),
                (
                    'CONTAIN',
                    "Contain",
                    "Select only the objects fully contained in circle",
                    'STICKY_UVS_LOC',
                    2,
                ),
                (
                    'OVERLAP',
                    "Overlap",
                    "Select objects overlapping circle",
                    'SELECT_SUBTRACT',
                    3,
                ),
            ],
            default='ORIGIN',
        )
        lasso_select_behavior: bpy.props.EnumProperty(
            name="Lasso Select Behavior",
            description="Selection behavior",
            items=[
                (
                    'ORIGIN',
                    "Origin (Default)",
                    "Select objects by origins",
                    'DOT',
                    1,
                ),
                (
                    'CONTAIN',
                    "Contain",
                    "Select only the objects fully contained in lasso",
                    'STICKY_UVS_LOC',
                    2,
                ),
                (
                    'OVERLAP',
                    "Overlap",
                    "Select objects overlapping lasso",
                    'SELECT_SUBTRACT',
                    3,
                ),
                (
                    'DIRECTIONAL',
                    "Directional",
                    "Dragging left to right select contained, right to left select overlapped",
                    'UV_SYNC_SELECT',
                    4,
                ),
                (
                    'DIRECTIONAL_REVERSED',
                    "Directional Reversed",
                    "Dragging left to right select overlapped, right to left select contained",
                    'UV_SYNC_SELECT',
                    5,
                ),
            ],
            default='ORIGIN',
        )
