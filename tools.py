import bpy, os
from .utils import register_tool_fixed, unregister_tool_fixed


icon_dir = os.path.join(os.path.dirname(__file__), "icon")


class ToolSelectBoxXrayMesh(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_MESH'

    bl_idname = "mesh_tool.select_box_xray"
    bl_label = "Select Box X-Ray"
    bl_description = ("Select items using box selection with x-ray")
    bl_icon = os.path.join(icon_dir, "addon.select_box_xray_icon")
    bl_widget = None
    bl_operator = "mesh.select_box_xray"
    bl_keymap = (
        ("mesh.select_box_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY'}, {}),
        ("mesh.select_box_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True}, {"properties": [("mode", 'ADD')]}),
        ("mesh.select_box_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True}, {"properties": [("mode", 'SUB')]}),
        ("mesh.select_box_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True} , {"properties": [("mode", 'AND')]})
    )

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("mesh.select_box_xray")
        
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True , icon_only=True)
        row.prop(props, "select_through", icon='XRAY', toggle=True)

        col = layout.column()
        if props.select_through:
            col.prop(props, "show_xray")
            col = layout.column()
            col.prop(props, "hide_modifiers")
            col.label(text="Slow on highpoly mesh:")

            col.prop(props, "select_all_edges")
            col.prop(props, "select_all_faces")
        
        
class ToolSelectBoxXrayObject(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'

    bl_idname = "object_tool.select_box_xray"
    bl_label = "Select Box X-Ray"
    bl_description = ("Select items using box selection with x-ray")
    bl_icon = os.path.join(icon_dir, "addon.select_box_xray_icon")
    bl_widget = None
    bl_operator = "object.select_box_xray"
    bl_keymap = (
        ("object.select_box_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY'}, {}),
        ("object.select_box_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True}, {"properties": [("mode", 'ADD')]}),
        ("object.select_box_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True}, {"properties": [("mode", 'SUB')]}),
        ("object.select_box_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True} , {"properties": [("mode", 'AND')]})
    )

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("object.select_box_xray")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True , icon_only=True)
        
        layout.prop(props, "show_xray")


class ToolSelectLassoXrayMesh(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_MESH'

    bl_idname = "mesh_tool.select_lasso_xray"
    bl_label = "Select Lasso X-Ray"
    bl_description = ("Select items using lasso selection with x-ray")
    bl_icon = os.path.join(icon_dir, "addon.select_lasso_xray_icon")
    bl_widget = None
    bl_operator = "mesh.select_lasso_xray"
    bl_keymap = (
        ("mesh.select_lasso_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY'}, {}),
        ("mesh.select_lasso_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True}, {"properties": [("mode", 'ADD')]}),
        ("mesh.select_lasso_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True}, {"properties": [("mode", 'SUB')]}),
        ("mesh.select_lasso_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True} , {"properties": [("mode", 'AND')]})
    )

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("mesh.select_lasso_xray")
        
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True , icon_only=True)
        row.prop(props, "select_through", icon='XRAY', toggle=True)

        col = layout.column()
        if props.select_through:
            col.prop(props, "show_xray")
            col = layout.column()
            col.prop(props, "hide_modifiers")
        
        
class ToolSelectLassoXrayObject(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'

    bl_idname = "object_tool.select_lasso_xray"
    bl_label = "Select Lasso X-Ray"
    bl_description = ("Select items using lasso selection with x-ray")
    bl_icon = os.path.join(icon_dir, "addon.select_lasso_xray_icon")
    bl_widget = None
    bl_operator = "object.select_lasso_xray"
    bl_keymap = (
        ("object.select_lasso_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY'}, {}),
        ("object.select_lasso_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True}, {"properties": [("mode", 'ADD')]}),
        ("object.select_lasso_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True}, {"properties": [("mode", 'SUB')]}),
        ("object.select_lasso_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True} , {"properties": [("mode", 'AND')]})
    )

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("object.select_lasso_xray")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True , icon_only=True)
        
        layout.prop(props, "show_xray")
        
        
class ToolSelectBoxXrayObject(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'

    bl_idname = "object_tool.select_box_xray"
    bl_label = "Select Box X-Ray"
    bl_description = ("Select items using box selection with x-ray")
    bl_icon = os.path.join(icon_dir, "addon.select_box_xray_icon")
    bl_widget = None
    bl_operator = "object.select_box_xray"
    bl_keymap = (
        ("object.select_box_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY'}, {}),
        ("object.select_box_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True}, {"properties": [("mode", 'ADD')]}),
        ("object.select_box_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True}, {"properties": [("mode", 'SUB')]}),
        ("object.select_box_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True} , {"properties": [("mode", 'AND')]})
    )

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("object.select_box_xray")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True , icon_only=True)
        
        layout.prop(props, "show_xray")


class ToolSelectCircleXrayMesh(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_MESH'

    bl_idname = "mesh_tool.select_circle_xray"
    bl_label = "Select Circle X-Ray"
    bl_description = ("Select items using circle selection with x-ray")
    bl_icon = os.path.join(icon_dir, "addon.select_circle_xray_icon")
    bl_widget = None
    bl_operator = "mesh.select_lasso_xray"
    bl_keymap = (
        ("mesh.select_circle_xray", {"type": 'LEFTMOUSE', "value": 'PRESS'}, {"properties": [("wait_for_input", False)]}),
        ("mesh.select_circle_xray", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True}, {"properties": [("mode", 'ADD'), ("wait_for_input", False)]}),
        ("mesh.select_circle_xray", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True}, {"properties": [("mode", 'SUB'), ("wait_for_input", False)]})
    )
    
    def draw_cursor(_context, tool, xy):
        from gpu_extras.presets import draw_circle_2d
        props = tool.operator_properties("view3d.select_circle")
        radius = props.radius
        draw_circle_2d(xy, (1.0,) * 4, radius, 32)

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("mesh.select_circle_xray")
        
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True , icon_only=True)
        row.prop(props, "select_through", icon='XRAY', toggle=True)
        
        layout.prop(tool.operator_properties("view3d.select_circle"), "radius")

        col = layout.column()
        if props.select_through:
            col.prop(props, "show_xray")
            col = layout.column()
            col.prop(props, "hide_modifiers")
        
        
class ToolSelectCircleXrayObject(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'

    bl_idname = "object_tool.select_circle_xray"
    bl_label = "Select Circle X-Ray"
    bl_description = ("Select items using circle selection with x-ray")
    bl_icon = os.path.join(icon_dir, "addon.select_circle_xray_icon")
    bl_widget = None
    bl_operator = "object.select_circle_xray"
    bl_keymap = (
        ("object.select_circle_xray", {"type": 'LEFTMOUSE', "value": 'PRESS'}, {"properties": [("wait_for_input", False)]}),
        ("object.select_circle_xray", {"type": 'LEFTMOUSE', "value": 'PRESS', "shift": True}, {"properties": [("mode", 'ADD'), ("wait_for_input", False)]}),
        ("object.select_circle_xray", {"type": 'LEFTMOUSE', "value": 'PRESS', "ctrl": True}, {"properties": [("mode", 'SUB'), ("wait_for_input", False)]})
    )

    def draw_cursor(_context, tool, xy):
        from gpu_extras.presets import draw_circle_2d
        props = tool.operator_properties("view3d.select_circle")
        radius = props.radius
        draw_circle_2d(xy, (1.0,) * 4, radius, 32)

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("object.select_circle_xray")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True , icon_only=True)
        
        layout.prop(tool.operator_properties("view3d.select_circle"), "radius")
        layout.prop(props, "show_xray")


class ToolSelectLassoXrayMesh(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'EDIT_MESH'

    bl_idname = "mesh_tool.select_lasso_xray"
    bl_label = "Select Lasso X-Ray"
    bl_description = ("Select items using lasso selection with x-ray")
    bl_icon = os.path.join(icon_dir, "addon.select_lasso_xray_icon")
    bl_widget = None
    bl_operator = "mesh.select_lasso_xray"
    bl_keymap = (
        ("mesh.select_lasso_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY'}, {}),
        ("mesh.select_lasso_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True}, {"properties": [("mode", 'ADD')]}),
        ("mesh.select_lasso_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True}, {"properties": [("mode", 'SUB')]}),
        ("mesh.select_lasso_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True} , {"properties": [("mode", 'AND')]})
    )

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("mesh.select_lasso_xray")
        
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True , icon_only=True)
        row.prop(props, "select_through", icon='XRAY', toggle=True)

        col = layout.column()
        if props.select_through:
            col.prop(props, "show_xray")
            col = layout.column()
            col.prop(props, "hide_modifiers")
        
        
class ToolSelectLassoXrayObject(bpy.types.WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'

    bl_idname = "object_tool.select_lasso_xray"
    bl_label = "Select Lasso X-Ray"
    bl_description = ("Select items using lasso selection with x-ray")
    bl_icon = os.path.join(icon_dir, "addon.select_lasso_xray_icon")
    bl_widget = None
    bl_operator = "object.select_lasso_xray"
    bl_keymap = (
        ("object.select_lasso_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY'}, {}),
        ("object.select_lasso_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True}, {"properties": [("mode", 'ADD')]}),
        ("object.select_lasso_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY', "ctrl": True}, {"properties": [("mode", 'SUB')]}),
        ("object.select_lasso_xray", {"type": 'EVT_TWEAK_L', "value": 'ANY', "shift": True, "ctrl": True} , {"properties": [("mode", 'AND')]})
    )

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("object.select_lasso_xray")
        row = layout.row()
        row.use_property_split = False
        row.prop(props, "mode", text="", expand=True , icon_only=True)
        
        layout.prop(props, "show_xray")


def register():
    if bpy.app.version < (2, 83, 11):
        register_tool_fixed(ToolSelectBoxXrayMesh, after={"builtin.select_box"}, separator=False, group=False)
        register_tool_fixed(ToolSelectBoxXrayObject, after={"builtin.select_box"}, separator=False, group=False)
        register_tool_fixed(ToolSelectCircleXrayMesh, after={"builtin.select_circle"}, separator=False, group=False)
        register_tool_fixed(ToolSelectCircleXrayObject, after={"builtin.select_circle"}, separator=False, group=False)
        register_tool_fixed(ToolSelectLassoXrayMesh, after={"builtin.select_lasso"}, separator=False, group=False)
        register_tool_fixed(ToolSelectLassoXrayObject, after={"builtin.select_lasso"}, separator=False, group=False)
    else:
        bpy.utils.register_tool(ToolSelectBoxXrayMesh, after={"builtin.select_box"}, separator=False, group=False)
        bpy.utils.register_tool(ToolSelectBoxXrayObject, after={"builtin.select_box"}, separator=False, group=False)
        bpy.utils.register_tool(ToolSelectCircleXrayMesh, after={"builtin.select_circle"}, separator=False, group=False)
        bpy.utils.register_tool(ToolSelectCircleXrayObject, after={"builtin.select_circle"}, separator=False, group=False)
        bpy.utils.register_tool(ToolSelectLassoXrayMesh, after={"builtin.select_lasso"}, separator=False, group=False)
        bpy.utils.register_tool(ToolSelectLassoXrayObject, after={"builtin.select_lasso"}, separator=False, group=False)


def unregister():
    if bpy.app.version < (2, 83, 11):
        unregister_tool_fixed(ToolSelectBoxXrayMesh)
        unregister_tool_fixed(ToolSelectBoxXrayObject)
        unregister_tool_fixed(ToolSelectCircleXrayMesh)
        unregister_tool_fixed(ToolSelectCircleXrayObject)
        unregister_tool_fixed(ToolSelectLassoXrayMesh)
        unregister_tool_fixed(ToolSelectLassoXrayObject)
    else:
        bpy.utils.unregister_tool(ToolSelectBoxXrayMesh)
        bpy.utils.unregister_tool(ToolSelectBoxXrayObject)
        bpy.utils.unregister_tool(ToolSelectCircleXrayMesh)
        bpy.utils.unregister_tool(ToolSelectCircleXrayObject)
        bpy.utils.unregister_tool(ToolSelectLassoXrayMesh)
        bpy.utils.unregister_tool(ToolSelectLassoXrayObject)
