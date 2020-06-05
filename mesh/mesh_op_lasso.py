import bpy
from .. functions.mesh_modal import *
from .. preferences import get_preferences

class MESH_OT_select_lasso_xray(bpy.types.Operator):
    """Select items using lasso selection with x-ray"""
    bl_idname = "mesh.select_lasso_xray"
    bl_label = "Lasso Select X-Ray"
    bl_options = {'REGISTER', 'GRAB_CURSOR'}

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
    select_through: bpy.props.BoolProperty(
        name="Select Through",
        description="Select verts, faces and edges laying underneath",
        default=True
    )
    hide_modifiers: bpy.props.BoolProperty(
        name="Hide Modifiers",
        description="Hide mirror and solidify modifiers during selection",
        default=True
    )

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode == 'EDIT_MESH'

    def __init__(self):
        self.override_intersect_tests = False
        self.override_wait_for_input = self.wait_for_input
        self.custom_wait_for_input_stage = False
        self.init_mods = None
        self.init_overlays = None
        self.select_through_toggle_keys = get_select_through_toggle_keys()
        self.alter_mode_toggle_keys = get_alter_mode_toggle_keys()
        self.select_through_toggle_key = get_preferences().select_through_toggle_key
        self.alter_mode_toggle_key = get_preferences().alter_mode_toggle_key
        self.alter_mode = get_preferences().alter_mode

    def invoke(self, context, event):
        # skip if overlays and modifiers visibility wouldn't be changed
        if self.select_through or self.override_wait_for_input:
            if self.hide_modifiers:
                self.init_mods = gather_modifiers(context)  # save initial modifier states
            self.init_overlays = gather_overlays(context)  # save initial x-ray overlay states

        # hide modifiers and set x-ray overlay states to allow selecting through
        if self.select_through:
            toggle_overlays(self, context)
            toggle_modifiers(self)

        context.window_manager.modal_handler_add(self)

        if self.override_wait_for_input:
            self.begin_custom_wait_for_input_stage(context)
        else:
            self.invoke_inbuilt_lasso_select(context, event)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        # cancel modal
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            restore_overlays(self, context)
            restore_modifiers(self)

            if self.custom_wait_for_input_stage:
                self.finish_custom_wait_for_input_stage(context)
            return {'CANCELLED'}

        # finish custom wait_for_input stage
        if self.custom_wait_for_input_stage:
            # finish custom wait_for_input stage
            if event.value == 'PRESS' and event.type in {'LEFTMOUSE', 'MIDDLEMOUSE'}:
                # restore cursor and status text
                self.finish_custom_wait_for_input_stage(context)
                toggle_alter_mode(self, event)
                self.invoke_inbuilt_lasso_select(context, event)

            # toggle select through and update overlays and modifiers state
            if event.value in {'PRESS', 'RELEASE'} and \
                    event.type in self.select_through_toggle_keys:
                self.select_through = not self.select_through
                toggle_overlays(self, context)
                toggle_modifiers(self)
        else:
            # inbuilt lasso_select was finished, now finish modal
            if event.value == 'RELEASE':
                self.finish_modal(context)
                return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def begin_custom_wait_for_input_stage(self, context):
        self.custom_wait_for_input_stage = True
        context.window.cursor_modal_set('CROSSHAIR')
        status_text = "RMB, ESC: Cancel  |  LMB: ADD  |  %s+LMB: %s" \
                      % (self.alter_mode_toggle_key, self.alter_mode)
        if self.select_through_toggle_key != 'DISABLED':
            status_text += "  |  %s: Toggle Select Through" % self.select_through_toggle_key
        context.workspace.status_text_set(text=status_text)
        sync_select_through(self, context)

    def finish_custom_wait_for_input_stage(self, context):
        """Restore cursor and status text"""
        self.custom_wait_for_input_stage = False
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(text=None)

    def invoke_inbuilt_lasso_select(self, context, event):
        bpy.ops.view3d.select_lasso('INVOKE_DEFAULT', mode=self.mode)

    def finish_modal(self, context):
        restore_overlays(self, context)
        restore_modifiers(self)


classes = (
    MESH_OT_select_lasso_xray,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
