import bpy
import os
from .utils import register_tool_fixed, unregister_tool_fixed


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
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
         {"properties": [("mode", 'AND')]}),
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
         {"properties": [("mode", 'SUB')]}),
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
         {"properties": [("mode", 'ADD')]}),
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY'}, {})
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
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
         {"properties": [("mode", 'AND')]}),
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
         {"properties": [("mode", 'SUB')]}),
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
         {"properties": [("mode", 'ADD')]}),
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY'}, {})
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
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
         {"properties": [("mode", 'AND')]}),
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
         {"properties": [("mode", 'SUB')]}),
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
         {"properties": [("mode", 'ADD')]}),
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY'}, {})
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
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
         {"properties": [("mode", 'AND')]}),
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
         {"properties": [("mode", 'SUB')]}),
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
         {"properties": [("mode", 'ADD')]}),
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY'}, {})
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
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
         {"properties": [("mode", 'AND')]}),
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
         {"properties": [("mode", 'SUB')]}),
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
         {"properties": [("mode", 'ADD')]}),
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY'}, {})
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
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
         {"properties": [("mode", 'AND')]}),
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
         {"properties": [("mode", 'SUB')]}),
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
         {"properties": [("mode", 'ADD')]}),
        ("view3d.select_box", {"type": 'EVT_TWEAK_L', "value": 'ANY'}, {})
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
        ("view3d.select_circle", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("mode", 'SUB'), ("wait_for_input", False)]}),
        ("view3d.select_circle", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
         {"properties": [("mode", 'ADD'), ("wait_for_input", False)]}),
        ("view3d.select_circle", {"type": 'LEFTMOUSE', "value": 'PRESS'},
         {"properties": [("wait_for_input", False)]})
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
        ("view3d.select_circle", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("mode", 'SUB'), ("wait_for_input", False)]}),
        ("view3d.select_circle", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
         {"properties": [("mode", 'ADD'), ("wait_for_input", False)]}),
        ("view3d.select_circle", {"type": 'LEFTMOUSE', "value": 'PRESS'},
         {"properties": [("wait_for_input", False)]})
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
        ("view3d.select_circle", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("mode", 'SUB'), ("wait_for_input", False)]}),
        ("view3d.select_circle", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
         {"properties": [("mode", 'ADD'), ("wait_for_input", False)]}),
        ("view3d.select_circle", {"type": 'LEFTMOUSE', "value": 'PRESS'},
         {"properties": [("wait_for_input", False)]})
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
        ("view3d.select_circle", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("mode", 'SUB'), ("wait_for_input", False)]}),
        ("view3d.select_circle", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
         {"properties": [("mode", 'ADD'), ("wait_for_input", False)]}),
        ("view3d.select_circle", {"type": 'LEFTMOUSE', "value": 'PRESS'},
         {"properties": [("wait_for_input", False)]})
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
        ("view3d.select_circle", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("mode", 'SUB'), ("wait_for_input", False)]}),
        ("view3d.select_circle", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
         {"properties": [("mode", 'ADD'), ("wait_for_input", False)]}),
        ("view3d.select_circle", {"type": 'LEFTMOUSE', "value": 'PRESS'},
         {"properties": [("wait_for_input", False)]})
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
        ("view3d.select_circle", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True},
         {"properties": [("mode", 'SUB'), ("wait_for_input", False)]}),
        ("view3d.select_circle", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True},
         {"properties": [("mode", 'ADD'), ("wait_for_input", False)]}),
        ("view3d.select_circle", {"type": 'LEFTMOUSE', "value": 'PRESS'},
         {"properties": [("wait_for_input", False)]})
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
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
         {"properties": [("mode", 'AND')]}),
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
         {"properties": [("mode", 'SUB')]}),
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
         {"properties": [("mode", 'ADD')]}),
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY'}, {})
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
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
         {"properties": [("mode", 'AND')]}),
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
         {"properties": [("mode", 'SUB')]}),
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
         {"properties": [("mode", 'ADD')]}),
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY'}, {})
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
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
         {"properties": [("mode", 'AND')]}),
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
         {"properties": [("mode", 'SUB')]}),
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
         {"properties": [("mode", 'ADD')]}),
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY'}, {})
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
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
         {"properties": [("mode", 'AND')]}),
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
         {"properties": [("mode", 'SUB')]}),
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
         {"properties": [("mode", 'ADD')]}),
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY'}, {})
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
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
         {"properties": [("mode", 'AND')]}),
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
         {"properties": [("mode", 'SUB')]}),
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
         {"properties": [("mode", 'ADD')]}),
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY'}, {})
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
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True},
         {"properties": [("mode", 'AND')]}),
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True},
         {"properties": [("mode", 'SUB')]}),
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True},
         {"properties": [("mode", 'ADD')]}),
        ("view3d.select_lasso", {"type": 'EVT_TWEAK_L', "value": 'ANY'}, {})
    )

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("view3d.select_lasso")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True, icon_only=True)


def register():
    if bpy.app.version < (2, 83, 0):
        register_tool_fixed(ToolSelectBoxXrayCurve,
                            after={"builtin.select_box"}, separator=False, group=False)
        register_tool_fixed(ToolSelectBoxXrayArmature,
                            after={"builtin.select_box"}, separator=False, group=False)
        register_tool_fixed(ToolSelectBoxXrayMetaball,
                            after={"builtin.select_box"}, separator=False, group=False)
        register_tool_fixed(ToolSelectBoxXrayLattice,
                            after={"builtin.select_box"}, separator=False, group=False)
        register_tool_fixed(ToolSelectBoxXrayPose,
                            after={"builtin.select_box"}, separator=False, group=False)
        register_tool_fixed(ToolSelectBoxXrayGrease,
                            after={"builtin.select_box"}, separator=False, group=False)
        
        register_tool_fixed(ToolSelectCircleXrayCurve,
                            after={"builtin.select_circle"}, separator=False, group=False)
        register_tool_fixed(ToolSelectCircleXrayArmature,
                            after={"builtin.select_circle"}, separator=False, group=False)
        register_tool_fixed(ToolSelectCircleXrayMetaball,
                            after={"builtin.select_circle"}, separator=False, group=False)
        register_tool_fixed(ToolSelectCircleXrayLattice,
                            after={"builtin.select_circle"}, separator=False, group=False)
        register_tool_fixed(ToolSelectCircleXrayPose,
                            after={"builtin.select_circle"}, separator=False, group=False)
        register_tool_fixed(ToolSelectCircleXrayGrease,
                            after={"builtin.select_box"}, separator=False, group=False)
        
        register_tool_fixed(ToolSelectLassoXrayCurve,
                            after={"builtin.select_lasso"}, separator=False, group=False)
        register_tool_fixed(ToolSelectLassoXrayArmature,
                            after={"builtin.select_lasso"}, separator=False, group=False)
        register_tool_fixed(ToolSelectLassoXrayMetaball,
                            after={"builtin.select_lasso"}, separator=False, group=False)
        register_tool_fixed(ToolSelectLassoXrayLattice,
                            after={"builtin.select_lasso"}, separator=False, group=False)
        register_tool_fixed(ToolSelectLassoXrayPose,
                            after={"builtin.select_lasso"}, separator=False, group=False)
        register_tool_fixed(ToolSelectLassoXrayGrease,
                            after={"builtin.select_lasso"}, separator=False, group=False)
    else:
        bpy.utils.register_tool(ToolSelectBoxXrayCurve,
                                after={"builtin.select_box"}, separator=False, group=False)
        bpy.utils.register_tool(ToolSelectBoxXrayArmature,
                                after={"builtin.select_box"}, separator=False, group=False)
        bpy.utils.register_tool(ToolSelectBoxXrayMetaball,
                                after={"builtin.select_box"}, separator=False, group=False)
        bpy.utils.register_tool(ToolSelectBoxXrayLattice,
                                after={"builtin.select_box"}, separator=False, group=False)
        bpy.utils.register_tool(ToolSelectBoxXrayPose,
                                after={"builtin.select_box"}, separator=False, group=False)
        bpy.utils.register_tool(ToolSelectBoxXrayGrease,
                                after={"builtin.select_box"}, separator=False, group=False)
        
        bpy.utils.register_tool(ToolSelectCircleXrayCurve,
                                after={"builtin.select_circle"}, separator=False, group=False)
        bpy.utils.register_tool(ToolSelectCircleXrayArmature,
                                after={"builtin.select_circle"}, separator=False, group=False)
        bpy.utils.register_tool(ToolSelectCircleXrayMetaball,
                                after={"builtin.select_circle"}, separator=False, group=False)
        bpy.utils.register_tool(ToolSelectCircleXrayLattice,
                                after={"builtin.select_circle"}, separator=False, group=False)
        bpy.utils.register_tool(ToolSelectCircleXrayPose,
                                after={"builtin.select_circle"}, separator=False, group=False)
        bpy.utils.register_tool(ToolSelectCircleXrayGrease,
                                after={"builtin.select_circle"}, separator=False, group=False)
        
        bpy.utils.register_tool(ToolSelectLassoXrayCurve,
                                after={"builtin.select_lasso"}, separator=False, group=False)
        bpy.utils.register_tool(ToolSelectLassoXrayArmature,
                                after={"builtin.select_lasso"}, separator=False, group=False)
        bpy.utils.register_tool(ToolSelectLassoXrayMetaball,
                                after={"builtin.select_lasso"}, separator=False, group=False)
        bpy.utils.register_tool(ToolSelectLassoXrayLattice,
                                after={"builtin.select_lasso"}, separator=False, group=False)
        bpy.utils.register_tool(ToolSelectLassoXrayPose,
                                after={"builtin.select_lasso"}, separator=False, group=False)
        bpy.utils.register_tool(ToolSelectLassoXrayGrease,
                                after={"builtin.select_lasso"}, separator=False, group=False)


def unregister():          
    if bpy.app.version < (2, 83, 0):
        unregister_tool_fixed(ToolSelectBoxXrayCurve)
        unregister_tool_fixed(ToolSelectBoxXrayArmature)
        unregister_tool_fixed(ToolSelectBoxXrayMetaball)        
        unregister_tool_fixed(ToolSelectBoxXrayLattice)
        unregister_tool_fixed(ToolSelectBoxXrayPose)
        unregister_tool_fixed(ToolSelectBoxXrayGrease)
        
        unregister_tool_fixed(ToolSelectCircleXrayCurve)
        unregister_tool_fixed(ToolSelectCircleXrayArmature)
        unregister_tool_fixed(ToolSelectCircleXrayMetaball)
        unregister_tool_fixed(ToolSelectCircleXrayLattice)
        unregister_tool_fixed(ToolSelectCircleXrayPose)
        unregister_tool_fixed(ToolSelectCircleXrayGrease)
        
        unregister_tool_fixed(ToolSelectLassoXrayCurve)
        unregister_tool_fixed(ToolSelectLassoXrayArmature)
        unregister_tool_fixed(ToolSelectLassoXrayMetaball)
        unregister_tool_fixed(ToolSelectLassoXrayLattice)
        unregister_tool_fixed(ToolSelectLassoXrayPose)
        unregister_tool_fixed(ToolSelectLassoXrayGrease)
    else:
        bpy.utils.unregister_tool(ToolSelectBoxXrayCurve)
        bpy.utils.unregister_tool(ToolSelectBoxXrayArmature)
        bpy.utils.unregister_tool(ToolSelectBoxXrayMetaball)        
        bpy.utils.unregister_tool(ToolSelectBoxXrayLattice)
        bpy.utils.unregister_tool(ToolSelectBoxXrayPose)
        bpy.utils.unregister_tool(ToolSelectBoxXrayGrease)
        
        bpy.utils.unregister_tool(ToolSelectCircleXrayCurve)
        bpy.utils.unregister_tool(ToolSelectCircleXrayArmature)
        bpy.utils.unregister_tool(ToolSelectCircleXrayMetaball)
        bpy.utils.unregister_tool(ToolSelectCircleXrayLattice)
        bpy.utils.unregister_tool(ToolSelectCircleXrayPose)
        bpy.utils.unregister_tool(ToolSelectCircleXrayGrease)
        
        bpy.utils.unregister_tool(ToolSelectLassoXrayCurve)
        bpy.utils.unregister_tool(ToolSelectLassoXrayArmature)
        bpy.utils.unregister_tool(ToolSelectLassoXrayMetaball)
        bpy.utils.unregister_tool(ToolSelectLassoXrayLattice)
        bpy.utils.unregister_tool(ToolSelectLassoXrayPose)
        bpy.utils.unregister_tool(ToolSelectLassoXrayGrease)
