import bpy


class OBJECT_OT_select_lasso_xray(bpy.types.Operator):
    """Select items using lasso selection with x-ray"""
    bl_idname = "object.select_lasso_xray"
    bl_label = "Lasso Select X-Ray"
    bl_options = {'REGISTER'}

    mode: bpy.props.EnumProperty(
        name="Mode",
        items=[('SET', "Set", "Set a new selection", 'SELECT_SET', 1),
               ('ADD', "Extend", "Extend existing selection", 'SELECT_EXTEND', 2),
               ('SUB', "Subtract", "Subtract existing selection", 'SELECT_SUBTRACT', 3),
               ('XOR', "Difference", "Inverts existing selection", 'SELECT_DIFFERENCE', 4),
               ('AND', "Intersect", "Intersect existing selection", 'SELECT_INTERSECT', 5)
               ],
        default='SET'
    )
    wait_for_input: bpy.props.BoolProperty(
        name="Wait for input",
        description="Wait for mouse input or initialize lasso selection immediately "
                    "(enable when assigning the operator to a keyboard key)",
        default=False
    )
    show_xray: bpy.props.BoolProperty(
        name="Show X-Ray",
        description="Enable x-ray shading during selection",
        default=True
    )

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode == 'OBJECT'

    def __init__(self):
        self.override_wait_for_input = self.wait_for_input
        self.custom_wait_for_input_stage = False
        self.init_show_xray = None
        self.init_show_xray_wireframe = None

    def invoke(self, context, event):
        self.init_show_xray = context.space_data.shading.show_xray
        self.init_show_xray_wireframe = context.space_data.shading.show_xray_wireframe
        self.toggle_overlays(context)

        context.window_manager.modal_handler_add(self)

        if self.override_wait_for_input:
            self.custom_wait_for_input_stage = True
            context.window.cursor_modal_set('CROSSHAIR')
            context.workspace.status_text_set(text="RMB, ESC: Cancel  |  LMB: Begin")
        else:
            bpy.ops.view3d.select_lasso('INVOKE_DEFAULT', mode=self.mode)
        return {'RUNNING_MODAL'}

    def toggle_overlays(self, context):
        if self.show_xray:
            if context.space_data.shading.type in {'SOLID', 'MATERIAL', 'RENDERED'} and \
                    not self.init_show_xray:
                context.space_data.shading.show_xray = True
            elif context.space_data.shading.type == 'WIREFRAME' and \
                    not self.init_show_xray_wireframe:
                context.space_data.shading.show_xray_wireframe = True

    def modal(self, context, event):
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            self.finish_modal(context)
            return {'CANCELLED'}

        if self.custom_wait_for_input_stage:
            if event.value == 'PRESS' and event.type in {'LEFTMOUSE', 'MIDDLEMOUSE'}:
                self.custom_wait_for_input_stage = False
                if event.shift:
                    self.mode = 'SUB'
                bpy.ops.view3d.select_lasso('INVOKE_DEFAULT', mode=self.mode)
        else:
            # inbuilt select_lasso was finished, now finish modal
            if event.value == 'RELEASE':
                self.finish_modal(context)
                return {'FINISHED'}
        return {'RUNNING_MODAL'}

    def finish_modal(self, context):
        context.space_data.shading.show_xray = self.init_show_xray
        context.space_data.shading.show_xray_wireframe = self.init_show_xray_wireframe
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(text=None)


classes = (
    OBJECT_OT_select_lasso_xray,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
