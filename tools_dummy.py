import bpy
import os
from .functions.legacy_tool_registration import register_tool_legacy, unregister_tool_legacy
from .tools_keymap import get_keymap_of_tool_from_prefs


icon_dir = os.path.join(os.path.dirname(__file__), "icon")


class ToolSelectBoxXrayCurve(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_CURVE'

    bl_idname = "curve_tool.select_box_xray"
    bl_label = "Select Box X-Ray"
    bl_description = "Select items using box selection"
    bl_icon = os.path.join(icon_dir, "addon.select_box_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_box"
    bl_keymap = (
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
            {"properties": [("mode", 'AND')]}),
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
            {"properties": [("mode", 'SUB')]}),
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
            {"properties": [("mode", 'ADD')]}),
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY'},
            {})
    )

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_box")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True, icon_only=True)


class ToolSelectBoxXrayArmature(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_ARMATURE'

    bl_idname = "armature_tool.select_box_xray"
    bl_label = "Select Box X-Ray"
    bl_description = "Select items using box selection"
    bl_icon = os.path.join(icon_dir, "addon.select_box_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_box"
    bl_keymap = (
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
            {"properties": [("mode", 'AND')]}),
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
            {"properties": [("mode", 'SUB')]}),
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
            {"properties": [("mode", 'ADD')]}),
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY'},
            {})
    )

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_box")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True, icon_only=True)


class ToolSelectBoxXrayMetaball(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_METABALL'

    bl_idname = "metaball_tool.select_box_xray"
    bl_label = "Select Box X-Ray"
    bl_description = "Select items using box selection"
    bl_icon = os.path.join(icon_dir, "addon.select_box_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_box"
    bl_keymap = (
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
            {"properties": [("mode", 'AND')]}),
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
            {"properties": [("mode", 'SUB')]}),
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
            {"properties": [("mode", 'ADD')]}),
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY'},
            {})
    )

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_box")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True, icon_only=True)


class ToolSelectBoxXrayLattice(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_LATTICE'

    bl_idname = "lattice_tool.select_box_xray"
    bl_label = "Select Box X-Ray"
    bl_description = "Select items using box selection"
    bl_icon = os.path.join(icon_dir, "addon.select_box_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_box"
    bl_keymap = (
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
            {"properties": [("mode", 'AND')]}),
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
            {"properties": [("mode", 'SUB')]}),
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
            {"properties": [("mode", 'ADD')]}),
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY'},
            {})
    )

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_box")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True, icon_only=True)


class ToolSelectBoxXrayPose(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'POSE'

    bl_idname = "pose_tool.select_box_xray"
    bl_label = "Select Box X-Ray"
    bl_description = "Select items using box selection"
    bl_icon = os.path.join(icon_dir, "addon.select_box_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_box"
    bl_keymap = (
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
            {"properties": [("mode", 'AND')]}),
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
            {"properties": [("mode", 'SUB')]}),
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
            {"properties": [("mode", 'ADD')]}),
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY'},
            {})
    )

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_box")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True, icon_only=True)


class ToolSelectBoxXrayGrease(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_GPENCIL'

    bl_idname = "grease_tool.select_box_xray"
    bl_label = "Select Box X-Ray"
    bl_description = "Select items using box selection"
    bl_icon = os.path.join(icon_dir, "addon.select_box_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_box"
    bl_keymap = (
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
            {"properties": [("mode", 'AND')]}),
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
            {"properties": [("mode", 'SUB')]}),
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
            {"properties": [("mode", 'ADD')]}),
        (
            "view3d.select_box",
            {"type": 'EVT_TWEAK_L', "value": 'ANY'},
            {})
    )

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_box")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True, icon_only=True)


class ToolSelectCircleXrayCurve(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_CURVE'

    bl_idname = "curve_tool.select_circle_xray"
    bl_label = "Select Circle X-Ray"
    bl_description = "Select items using circle selection"
    bl_icon = os.path.join(icon_dir, "addon.select_circle_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_circle"
    bl_keymap = (
        (
            "view3d.select_circle",
            {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
            {"properties": [("mode", 'SUB')]}),
        (
            "view3d.select_circle",
            {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
            {"properties": [("mode", 'ADD')]}),
        (
            "view3d.select_circle",
            {"type": 'LEFTMOUSE', "value": 'PRESS'},
            {})
    )

    def draw_cursor(context, tool, xy):
        from gpu_extras.presets import draw_circle_2d
        props = tool.operator_properties("view3d.select_circle")
        radius = props.radius
        draw_circle_2d(xy, (1.0,) * 4, radius, 32)

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_circle")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True, icon_only=True)

        layout.prop(tool.operator_properties("view3d.select_circle"), "radius")


class ToolSelectCircleXrayArmature(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_ARMATURE'

    bl_idname = "armature_tool.select_circle_xray"
    bl_label = "Select Circle X-Ray"
    bl_description = "Select items using circle selection"
    bl_icon = os.path.join(icon_dir, "addon.select_circle_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_circle"
    bl_keymap = (
        (
            "view3d.select_circle",
            {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
            {"properties": [("mode", 'SUB')]}),
        (
            "view3d.select_circle",
            {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
            {"properties": [("mode", 'ADD')]}),
        (
            "view3d.select_circle",
            {"type": 'LEFTMOUSE', "value": 'PRESS'},
            {})
    )

    def draw_cursor(context, tool, xy):
        from gpu_extras.presets import draw_circle_2d
        props = tool.operator_properties("view3d.select_circle")
        radius = props.radius
        draw_circle_2d(xy, (1.0,) * 4, radius, 32)

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_circle")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True, icon_only=True)

        layout.prop(tool.operator_properties("view3d.select_circle"), "radius")


class ToolSelectCircleXrayMetaball(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_METABALL'

    bl_idname = "metaball_tool.select_circle_xray"
    bl_label = "Select Circle X-Ray"
    bl_description = "Select items using circle selection"
    bl_icon = os.path.join(icon_dir, "addon.select_circle_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_circle"
    bl_keymap = (
        (
            "view3d.select_circle",
            {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
            {"properties": [("mode", 'SUB')]}),
        (
            "view3d.select_circle",
            {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
            {"properties": [("mode", 'ADD')]}),
        (
            "view3d.select_circle",
            {"type": 'LEFTMOUSE', "value": 'PRESS'},
            {})
    )

    def draw_cursor(context, tool, xy):
        from gpu_extras.presets import draw_circle_2d
        props = tool.operator_properties("view3d.select_circle")
        radius = props.radius
        draw_circle_2d(xy, (1.0,) * 4, radius, 32)

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_circle")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True, icon_only=True)

        layout.prop(tool.operator_properties("view3d.select_circle"), "radius")


class ToolSelectCircleXrayLattice(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_LATTICE'

    bl_idname = "lattice_tool.select_circle_xray"
    bl_label = "Select Circle X-Ray"
    bl_description = "Select items using circle selection"
    bl_icon = os.path.join(icon_dir, "addon.select_circle_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_circle"
    bl_keymap = (
        (
            "view3d.select_circle",
            {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
            {"properties": [("mode", 'SUB')]}),
        (
            "view3d.select_circle",
            {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
            {"properties": [("mode", 'ADD')]}),
        (
            "view3d.select_circle",
            {"type": 'LEFTMOUSE', "value": 'PRESS'},
            {})
    )

    def draw_cursor(context, tool, xy):
        from gpu_extras.presets import draw_circle_2d
        props = tool.operator_properties("view3d.select_circle")
        radius = props.radius
        draw_circle_2d(xy, (1.0,) * 4, radius, 32)

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_circle")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True, icon_only=True)

        layout.prop(tool.operator_properties("view3d.select_circle"), "radius")


class ToolSelectCircleXrayPose(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'POSE'

    bl_idname = "pose_tool.select_circle_xray"
    bl_label = "Select Circle X-Ray"
    bl_description = "Select items using circle selection"
    bl_icon = os.path.join(icon_dir, "addon.select_circle_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_circle"
    bl_keymap = (
        (
            "view3d.select_circle",
            {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
            {"properties": [("mode", 'SUB')]}),
        (
            "view3d.select_circle",
            {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
            {"properties": [("mode", 'ADD')]}),
        (
            "view3d.select_circle",
            {"type": 'LEFTMOUSE', "value": 'PRESS'},
            {})
    )

    def draw_cursor(context, tool, xy):
        from gpu_extras.presets import draw_circle_2d
        props = tool.operator_properties("view3d.select_circle")
        radius = props.radius
        draw_circle_2d(xy, (1.0,) * 4, radius, 32)

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_circle")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True, icon_only=True)

        layout.prop(tool.operator_properties("view3d.select_circle"), "radius")


class ToolSelectCircleXrayGrease(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_GPENCIL'

    bl_idname = "grease_tool.select_circle_xray"
    bl_label = "Select Circle X-Ray"
    bl_description = "Select items using circle selection"
    bl_icon = os.path.join(icon_dir, "addon.select_circle_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_circle"
    bl_keymap = (
        (
            "view3d.select_circle",
            {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
            {"properties": [("mode", 'SUB')]}),
        (
            "view3d.select_circle",
            {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
            {"properties": [("mode", 'ADD')]}),
        (
            "view3d.select_circle",
            {"type": 'LEFTMOUSE', "value": 'PRESS'},
            {})
    )

    def draw_cursor(context, tool, xy):
        from gpu_extras.presets import draw_circle_2d
        props = tool.operator_properties("view3d.select_circle")
        radius = props.radius
        draw_circle_2d(xy, (1.0,) * 4, radius, 32)

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_circle")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True, icon_only=True)

        layout.prop(tool.operator_properties("view3d.select_circle"), "radius")


class ToolSelectLassoXrayCurve(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_CURVE'

    bl_idname = "curve_tool.select_lasso_xray"
    bl_label = "Select Lasso X-Ray"
    bl_description = "Select items using lasso selection"
    bl_icon = os.path.join(icon_dir, "addon.select_lasso_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_lasso"
    bl_keymap = (
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
            {"properties": [("mode", 'AND')]}),
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
            {"properties": [("mode", 'SUB')]}),
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
            {"properties": [("mode", 'ADD')]}),
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY'},
            {})
    )

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_lasso")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True, icon_only=True)


class ToolSelectLassoXrayArmature(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_ARMATURE'

    bl_idname = "armature_tool.select_lasso_xray"
    bl_label = "Select Lasso X-Ray"
    bl_description = "Select items using lasso selection"
    bl_icon = os.path.join(icon_dir, "addon.select_lasso_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_lasso"
    bl_keymap = (
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
            {"properties": [("mode", 'AND')]}),
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
            {"properties": [("mode", 'SUB')]}),
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
            {"properties": [("mode", 'ADD')]}),
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY'},
            {})
    )

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_lasso")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True, icon_only=True)


class ToolSelectLassoXrayMetaball(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_METABALL'

    bl_idname = "metaball_tool.select_lasso_xray"
    bl_label = "Select Lasso X-Ray"
    bl_description = "Select items using lasso selection"
    bl_icon = os.path.join(icon_dir, "addon.select_lasso_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_lasso"
    bl_keymap = (
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
            {"properties": [("mode", 'AND')]}),
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
            {"properties": [("mode", 'SUB')]}),
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
            {"properties": [("mode", 'ADD')]}),
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY'},
            {})
    )

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_lasso")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True, icon_only=True)


class ToolSelectLassoXrayLattice(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_LATTICE'

    bl_idname = "lattice_tool.select_lasso_xray"
    bl_label = "Select Lasso X-Ray"
    bl_description = "Select items using lasso selection"
    bl_icon = os.path.join(icon_dir, "addon.select_lasso_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_lasso"
    bl_keymap = (
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
            {"properties": [("mode", 'AND')]}),
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
            {"properties": [("mode", 'SUB')]}),
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
            {"properties": [("mode", 'ADD')]}),
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY'},
            {})
    )

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_lasso")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True, icon_only=True)


class ToolSelectLassoXrayPose(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'POSE'

    bl_idname = "pose_tool.select_lasso_xray"
    bl_label = "Select Lasso X-Ray"
    bl_description = "Select items using lasso selection"
    bl_icon = os.path.join(icon_dir, "addon.select_lasso_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_lasso"
    bl_keymap = (
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
            {"properties": [("mode", 'AND')]}),
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
            {"properties": [("mode", 'SUB')]}),
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
            {"properties": [("mode", 'ADD')]}),
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY'},
            {})
    )

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_lasso")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True, icon_only=True)


class ToolSelectLassoXrayGrease(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_GPENCIL'

    bl_idname = "grease_tool.select_lasso_xray"
    bl_label = "Select Lasso X-Ray"
    bl_description = "Select items using lasso selection"
    bl_icon = os.path.join(icon_dir, "addon.select_lasso_xray_icon")
    bl_widget = None
    bl_operator = "view3d.select_lasso"
    bl_keymap = (
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
            {"properties": [("mode", 'AND')]}),
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
            {"properties": [("mode", 'SUB')]}),
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
            {"properties": [("mode", 'ADD')]}),
        (
            "view3d.select_lasso",
            {"type": 'EVT_TWEAK_L', "value": 'ANY'},
            {})
    )

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_lasso")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True, icon_only=True)


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
    ToolSelectCircleXrayGrease
)
lasso_tools = (
    ToolSelectLassoXrayCurve,
    ToolSelectLassoXrayArmature,
    ToolSelectLassoXrayMetaball,
    ToolSelectLassoXrayLattice,
    ToolSelectLassoXrayPose,
    ToolSelectLassoXrayGrease
)


def register():
    for tool in box_tools:
        tool.bl_keymap = get_keymap_of_tool_from_prefs("view3d.select_box")
    for tool in circle_tools:
        tool.bl_keymap = get_keymap_of_tool_from_prefs("view3d.select_circle")
    for tool in lasso_tools:
        tool.bl_keymap = get_keymap_of_tool_from_prefs("view3d.select_lasso")

    if bpy.app.version < (2, 83, 0):
        for tool in box_tools:
            register_tool_legacy(tool, after={"builtin.select_box"},
                                 separator=False, group=False)
        for tool in circle_tools:
            register_tool_legacy(tool, after={"builtin.select_circle"},
                                 separator=False, group=False)
        for tool in lasso_tools:
            register_tool_legacy(tool, after={"builtin.select_lasso"},
                                 separator=False, group=False)
    else:
        for tool in box_tools:
            bpy.utils.register_tool(tool, after={"builtin.select_box"},
                                    separator=False, group=False)
        for tool in circle_tools:
            bpy.utils.register_tool(tool, after={"builtin.select_circle"},
                                    separator=False, group=False)
        for tool in lasso_tools:
            bpy.utils.register_tool(tool, after={"builtin.select_lasso"},
                                    separator=False, group=False)


def unregister():
    import itertools

    if bpy.app.version < (2, 83, 0):
        for tool in itertools.chain(box_tools, circle_tools, lasso_tools):
            unregister_tool_legacy(tool)
    else:
        for tool in itertools.chain(box_tools, circle_tools, lasso_tools):
            bpy.utils.unregister_tool(tool)
