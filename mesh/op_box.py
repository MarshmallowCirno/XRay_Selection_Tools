from struct import pack
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from .. functions.intersect import select_elems_in_rectangle
from .. functions.modal import *


class MESH_OT_select_box_xray(bpy.types.Operator):
    """Select items using box selection with x-ray"""
    bl_idname = "mesh.select_box_xray"
    bl_label = "Box Select X-Ray"
    bl_options = {'REGISTER', 'GRAB_CURSOR'}

    mode: bpy.props.EnumProperty(
        name="Mode",
        items=[('SET', "Set", "Set a new selection", 'SELECT_SET', 1),
               ('ADD', "Extend", "Extend existing selection", 'SELECT_EXTEND', 2),
               ('SUB', "Subtract", "Subtract existing selection", 'SELECT_SUBTRACT', 3),
               ('XOR', "Difference", "Inverts existing selection", 'SELECT_DIFFERENCE', 4),
               ('AND', "Intersect", "Intersect existing selection", 'SELECT_INTERSECT', 5)],
        default='SET'
    )
    wait_for_input: bpy.props.BoolProperty(
        name="Wait for input",
        description="Wait for mouse input or initialize box selection immediately "
                    "(enable when assigning the operator to a keyboard key)",
        default=False
    )
    select_all_faces: bpy.props.BoolProperty(
        name="Select All Faces",
        description="Additionally select faces that are partially inside the selection box, "
                    "not just the ones with centers inside the selection box. Works only in "
                    "select through mode",
        default=False
    )
    select_all_edges: bpy.props.BoolProperty(
        name="Select All Edges",
        description="Additionally select edges that are partially inside the selection box, "
                    "not just the ones completely inside the selection box. Works only in select "
                    "through mode",
        default=False
    )
    show_xray: bpy.props.BoolProperty(
        name="Show X-Ray",
        description="Enable x-ray shading during selection. Works only in select through mode",
        default=True
    )
    select_through: bpy.props.BoolProperty(
        name="Select Through",
        description="Select verts, faces and edges laying underneath",
        default=True
    )
    hide_modifiers: bpy.props.BoolProperty(
        name="Hide Modifiers",
        description="Hide mirror and solidify modifiers during selection. Works only in select "
                    "through mode",
        default=True
    )

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode == 'EDIT_MESH'

    def __init__(self):
        self.override_intersect_tests = False
        self.override_wait_for_input = False
        self.custom_wait_for_input_stage = False
        self.init_mods = None
        self.init_overlays = None
        self.handler = None
        self.shader = None
        self.batch = None
        self.unif_dash_color = None
        self.unif_gap_color = None
        self.init_mouse_x = 0  # initial mouse x coord during drawing box
        self.init_mouse_y = 0  # initial mouse y coord during drawing box
        self.curr_mouse_x = 0  # current mouse x coord during drawing box
        self.curr_mouse_y = 0  # current mouse y coord during drawing box
        self.disabled_inbuilt_box_select_confirmation = False
        self.init_gesture_box_keymaps = []
        self.new_gesture_box_keymaps = []
        self.select_through_toggle_keys = get_select_through_toggle_keys()
        self.alter_mode_toggle_keys = get_alter_mode_toggle_keys()
        self.select_through_toggle_key = get_preferences().select_through_toggle_key
        self.alter_mode_toggle_key = get_preferences().alter_mode_toggle_key
        self.alter_mode = get_preferences().alter_mode

        # https://docs.blender.org/api/blender2.8/gpu.html#custom-shader-for-dotted-3d-line
        # https://stackoverflow.com/questions/52928678/dashed-line-in-opengl3
        self.vertex_shader = '''
            in vec2 pos;
            in float len;
            out float v_Len;
            
            uniform mat4 u_ViewProjectionMatrix;
            uniform float u_X;
            uniform float u_Y;

            void main()
            {
                v_Len = len;
                gl_Position = u_ViewProjectionMatrix * vec4(pos.x + u_X, pos.y + u_Y, 0.0f, 1.0f);
            }
        '''
        self.fragment_shader = '''
            in float v_Len;
            out vec4 fragColor;
            
            uniform vec4 u_DashColor;
            uniform vec4 u_GapColor;
            
            float dash_size = 4;
            float gap_size = 4;
            vec4 col = u_DashColor;

            void main()
            {
                if (fract(v_Len/(dash_size + gap_size)) > dash_size/(dash_size + gap_size)) 
                    col = u_GapColor;
                    
                fragColor = col;
            }
        '''

    def invoke(self, context, event):
        # use custom wait_for_input if keyboard version of operator is used
        # and toggle key is set
        self.override_wait_for_input = \
            self.wait_for_input and (self.select_through_toggle_key != 'DISABLED' or
                                     self.alter_mode_toggle_key != 'SHIFT')

        # skip if overlays and modifiers visibility wouldn't be changed
        if self.select_through or self.override_wait_for_input:
            if self.hide_modifiers:
                self.init_mods = gather_modifiers(context)  # save initial modifier states
            self.init_overlays = gather_overlays(context)  # save initial x-ray overlay states
            # decide whether elements that can't be selected with the default box select
            # operator should be selected with custom intersection tests
            self.override_intersect_tests = \
                self.select_all_faces and context.tool_settings.mesh_select_mode[2] or \
                self.select_all_edges and context.tool_settings.mesh_select_mode[1]

        # hide modifiers and set x-ray overlay states to allow selecting through
        if self.select_through:
            toggle_overlays(self, context)
            toggle_modifiers(self)

        context.window_manager.modal_handler_add(self)

        if self.override_wait_for_input:
            self.begin_custom_wait_for_input_stage(context, event)
        else:
            self.invoke_inbuilt_box_select(context, event)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        # cancel modal
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            restore_overlays(self, context)
            restore_modifiers(self)

            if self.custom_wait_for_input_stage:
                self.finish_custom_wait_for_input_stage(context)

            if self.disabled_inbuilt_box_select_confirmation:
                self.restore_inbuilt_box_select_confirmation(context)
            return {'CANCELLED'}

        if self.custom_wait_for_input_stage:
            # update wait_for_input shader
            if event.type == 'MOUSEMOVE':
                self.curr_mouse_x = event.mouse_region_x
                self.curr_mouse_y = event.mouse_region_y
                context.region.tag_redraw()

            # finish custom wait_for_input stage
            if event.value == 'PRESS' and event.type in {'LEFTMOUSE', 'MIDDLEMOUSE'}:
                # restore cursor and status text, remove crossed lines shader
                self.finish_custom_wait_for_input_stage(context)
                toggle_alter_mode(self, event)
                self.invoke_inbuilt_box_select(context, event)

            # toggle select_through and update overlays and modifiers state
            if event.value in {'PRESS', 'RELEASE'} and \
                    event.type in self.select_through_toggle_keys:
                self.select_through = not self.select_through
                toggle_overlays(self, context)
                toggle_modifiers(self)
        else:
            # inbuilt box_select was finished, now finish modal
            if event.value == 'RELEASE':
                self.finish_modal(context, event)
                return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def begin_custom_wait_for_input_stage(self, context, event):
        """Set cursor and status text, draw wait_for_input shader"""
        self.custom_wait_for_input_stage = True
        context.window.cursor_modal_set('CROSSHAIR')
        status_text = "RMB, ESC: Cancel  |  LMB: ADD  |  %s+LMB: %s" \
                      % (self.alter_mode_toggle_key, self.alter_mode)
        if self.select_through_toggle_key != 'DISABLED':
            status_text += "  |  %s: Toggle Select Through" % self.select_through_toggle_key
        context.workspace.status_text_set(text=status_text)
        sync_select_through(self, context)

        self.build_crosshair_shader(context)
        self.curr_mouse_x = event.mouse_region_x
        self.curr_mouse_y = event.mouse_region_y
        self.handler = context.space_data.draw_handler_add(
            self.draw_crosshair_shader, (), 'WINDOW', 'POST_PIXEL')
        context.region.tag_redraw()

    def finish_custom_wait_for_input_stage(self, context):
        """Restore cursor and status text, remove shader"""
        self.custom_wait_for_input_stage = False
        self.wait_for_input = False
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(text=None)
        context.space_data.draw_handler_remove(self.handler, 'WINDOW')
        context.region.tag_redraw()

    def invoke_inbuilt_box_select(self, context, event):
        # if custom intersection tests will be used prepare for them
        # they could be used only in select through mode
        if self.override_intersect_tests and self.select_through:
            # save initial mouse location to calculate box position in intersection tests
            self.init_mouse_x = event.mouse_region_x
            self.init_mouse_y = event.mouse_region_y
            # disable default box_select operator
            self.disable_inbuilt_box_select_confirmation(context)

        bpy.ops.view3d.select_box('INVOKE_DEFAULT', mode=self.mode,
                                  wait_for_input=self.wait_for_input)

    def disable_inbuilt_box_select_confirmation(self, context):
        """Temporary disable a default "box select" tool confirmation by adding the "cancel"
        keys to its modal keymap and deactivating default confirmation keymap items, since actual
        selection will be made with the addon and the default "box select" operator only needed for
        drawing a fast rectangle shader"""
        kc = context.window_manager.keyconfigs.user
        # save a default keymap item states and deactivate them
        km = kc.keymaps["Gesture Box"]
        for kmi in km.keymap_items:
            if kmi.propvalue != 'BEGIN':
                self.init_gesture_box_keymaps.append((kmi.id, kmi.active))
                kmi.active = False

        self.disabled_inbuilt_box_select_confirmation = True

        # add the new cancel keymap items
        km = kc.keymaps.new(name="Gesture Box", space_type='EMPTY', region_type='WINDOW',
                            modal=True)
        kmi = km.keymap_items.new_modal('CANCEL', 'LEFTMOUSE', 'RELEASE', any=True)
        self.new_gesture_box_keymaps.append(kmi.id)
        kmi = km.keymap_items.new_modal('CANCEL', 'RIGHTMOUSE', 'RELEASE', any=True)
        self.new_gesture_box_keymaps.append(kmi.id)
        kmi = km.keymap_items.new_modal('CANCEL', 'MIDDLEMOUSE', 'RELEASE', any=True)
        self.new_gesture_box_keymaps.append(kmi.id)

    def restore_inbuilt_box_select_confirmation(self, context):
        """Restore initial "box select" keymap items"""
        kc = context.window_manager.keyconfigs.user
        km = kc.keymaps["Gesture Box"]

        for id, active in self.init_gesture_box_keymaps:
            kmi = km.keymap_items.from_id(id)
            kmi.active = active

        for id in self.new_gesture_box_keymaps:
            kmi = km.keymap_items.from_id(id)
            km.keymap_items.remove(kmi)

        self.disabled_inbuilt_box_select_confirmation = False

    def finish_modal(self, context, event):
        # default "box select" wasn't used, select with custom intersection tests
        if self.select_through and self.override_intersect_tests:
            # restore default box select confirmation
            if self.disabled_inbuilt_box_select_confirmation:
                self.restore_inbuilt_box_select_confirmation(context)
            # get selection rectangle coordinates
            xmin = min(self.init_mouse_x, event.mouse_region_x)
            xmax = max(self.init_mouse_x, event.mouse_region_x)
            ymin = min(self.init_mouse_y, event.mouse_region_y)
            ymax = max(self.init_mouse_y, event.mouse_region_y)
            # do selection
            select_elems_in_rectangle(context, mode=self.mode,
                                      select_all_edges=self.select_all_edges,
                                      select_all_faces=self.select_all_faces,
                                      xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)
            bpy.ops.ed.undo_push(message="Box Select")

        restore_overlays(self, context)
        restore_modifiers(self)

    def build_crosshair_shader(self, context):
        width = context.region.width
        height = context.region.height

        vertices = ((0, -height),
                    (0, height),
                    (-width, 0),
                    (width, 0))
        lengths = (0, 2*height, 0, 2*width)

        self.shader = gpu.types.GPUShader(self.vertex_shader, self.fragment_shader)
        self.batch = batch_for_shader(self.shader, 'LINES', {"pos": vertices, "len": lengths})
        self.unif_dash_color = self.shader.uniform_from_name("u_DashColor")
        self.unif_gap_color = self.shader.uniform_from_name("u_GapColor")

    def draw_crosshair_shader(self):
        matrix = gpu.matrix.get_projection_matrix()
        dash_color = (1.0, 1.0, 1.0, 1.0)
        gap_color = (0.5, 0.5, 0.5, 1.0)

        self.shader.bind()
        self.shader.uniform_float("u_ViewProjectionMatrix", matrix)
        self.shader.uniform_float("u_X", self.curr_mouse_x)
        self.shader.uniform_float("u_Y", self.curr_mouse_y)
        self.shader.uniform_vector_float(self.unif_dash_color, pack("4f", *dash_color), 4)
        self.shader.uniform_vector_float(self.unif_gap_color, pack("4f", *gap_color), 4)
        self.batch.draw(self.shader)


classes = (
    MESH_OT_select_box_xray,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
