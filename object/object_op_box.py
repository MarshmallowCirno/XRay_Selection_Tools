import bpy
from .. functions.object_modal import *
from .. preferences import get_preferences


class OBJECT_OT_select_box_xray(bpy.types.Operator):
    """Select items using box selection with x-ray"""
    bl_idname = "object.select_box_xray"
    bl_label = "Box Select X-Ray"
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
        description="Wait for mouse input or initialize box selection immediately "
                    "(enable when assigning the operator to a keyboard key)",
        default=False
    )
    show_xray: bpy.props.BoolProperty(
        name="Show X-Ray",
        description="Enable x-ray shading during selection",
        default=True
    )
    show_crosshair: bpy.props.BoolProperty(
        name="Show Crosshair",
        description="Show crosshair when wait_for_input is enabled",
        default=True
    )

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode == 'OBJECT'

    def __init__(self):
        self.override_wait_for_input = False
        self.custom_wait_for_input_stage = False
        self.init_overlays = None
        self.alter_mode_toggle_keys = get_alter_mode_toggle_keys()
        self.alter_mode_toggle_key = get_preferences().alter_mode_toggle_key
        self.alter_mode = get_preferences().alter_mode

    def invoke(self, context, event):
        self.override_wait_for_input = not self.show_crosshair

        self.init_overlays = gather_overlays(context)
        toggle_overlays(self, context)

        context.window_manager.modal_handler_add(self)

        if self.override_wait_for_input:
            self.begin_custom_wait_for_input_stage(context)
        else:
            self.invoke_inbuilt_box_select()
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        # cancel modal
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            restore_overlays(self, context)
            if self.custom_wait_for_input_stage:
                self.finish_custom_wait_for_input_stage(context)
            return {'CANCELLED'}

        if self.custom_wait_for_input_stage:
            # finish custom wait_for_input stage
            if event.value == 'PRESS' and event.type in {'LEFTMOUSE', 'MIDDLEMOUSE'}:
                self.custom_wait_for_input_stage = False
                self.finish_custom_wait_for_input_stage(context)
                toggle_alter_mode(self, event)
                self.invoke_inbuilt_box_select()
        else:
            # inbuilt box_select was finished, now finish modal
            if event.value == 'RELEASE':
                self.finish_modal(context)
                return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def begin_custom_wait_for_input_stage(self, context):
        self.custom_wait_for_input_stage = True
        context.window.cursor_modal_set('CROSSHAIR')
        status_text = "RMB, ESC: Cancel  |  LMB: ADD  |  %s+LMB: %s" \
                      % (self.alter_mode_toggle_key, self.alter_mode)
        context.workspace.status_text_set(text=status_text)

    def finish_custom_wait_for_input_stage(self, context):
        self.custom_wait_for_input_stage = False
        self.wait_for_input = False
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(text=None)

    def invoke_inbuilt_box_select(self):
        bpy.ops.view3d.select_box('INVOKE_DEFAULT', mode=self.mode,
                                  wait_for_input=self.wait_for_input)

    def finish_modal(self, context):
        restore_overlays(self, context)


classes = (
    OBJECT_OT_select_box_xray,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
