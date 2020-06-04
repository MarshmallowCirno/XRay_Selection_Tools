from struct import pack
import bpy
import gpu
import numpy as np
from gpu_extras.batch import batch_for_shader
from bgl import glEnable, glDisable, GL_BLEND
from mathutils import Vector
from ..functions.modal import *
from ..preferences import get_preferences


class MESH_OT_select_circle_xray(bpy.types.Operator):
    """Select items using circle selection with x-ray"""
    bl_idname = "mesh.select_circle_xray"
    bl_label = "Circle Select X-Ray"
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
    radius: bpy.props.IntProperty(
        name="Radius",
        description="Radius",
        default=25,
        min=1
    )
    wait_for_input: bpy.props.BoolProperty(
        name="Wait for input",
        description="Wait for mouse input or initialize box selection immediately "
                    "(enable when assigning the operator to a keyboard key)",
        default=True
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
        self.override_wait_for_input = False
        self.custom_wait_for_input_stage = False
        self.init_mods = None
        self.init_overlays = None
        self.handler = None
        self.border_shader = None
        self.border_batch = None
        self.inner_shader = None
        self.inner_batch = None
        self.unif_dash_color = None
        self.unif_gap_color = None
        self.unif_inner_color = None
        self.init_mouse_x = 0  # initial mouse x coord during drawing box
        self.init_mouse_y = 0  # initial mouse y coord during drawing box
        self.curr_mouse_x = 0  # current mouse x coord during drawing box
        self.curr_mouse_y = 0  # current mouse y coord during drawing box
        self.select_through_toggle_keys = get_select_through_toggle_keys()
        self.alter_mode_toggle_keys = get_alter_mode_toggle_keys()
        self.select_through_toggle_key = get_preferences().select_through_toggle_key
        self.alter_mode_toggle_key = get_preferences().alter_mode_toggle_key
        self.alter_mode = get_preferences().alter_mode

        self.border_vertex_shader = '''
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
        self.border_fragment_shader = '''
            in float v_Len;
            out vec4 fragColor;
        
            uniform vec4 u_DashColor;
            uniform vec4 u_GapColor;
            
            float dash_size = 2;
            float gap_size = 2;
            vec4 col = u_DashColor;
            
            void main()
            {
                if (fract(v_Len/(dash_size + gap_size)) > dash_size/(dash_size + gap_size)) 
                    col = u_GapColor;
                    
                fragColor = col;
            }
        '''

        self.inner_vertex_shader = '''
            in vec2 pos;

            uniform mat4 u_ViewProjectionMatrix;
            uniform float u_X;
            uniform float u_Y;

            void main()
            {
                gl_Position = u_ViewProjectionMatrix * vec4(pos.x + u_X, pos.y + u_Y, 0.0f, 1.0f);
            }
        '''
        self.inner_fragment_shader = '''
            out vec4 fragColor;

            uniform vec4 u_Color;
            
            void main()
            {
                fragColor = u_Color;
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

        # hide modifiers and set x-ray overlay states to allow selecting through
        if self.select_through:
            toggle_overlays(self, context)
            toggle_modifiers(self)

        context.window_manager.modal_handler_add(self)

        if self.override_wait_for_input:
            self.begin_custom_wait_for_input_stage(context, event)
        else:
            self.invoke_inbuilt_circle_select(context, event)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        # cancel modal
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            restore_overlays(self, context)
            restore_modifiers(self)

            if self.custom_wait_for_input_stage:
                self.finish_custom_wait_for_input_stage(context)
            return {'CANCELLED'}

        if self.custom_wait_for_input_stage:
            # update wait_for_input shader
            if event.type == 'MOUSEMOVE':
                self.curr_mouse_x = event.mouse_region_x
                self.curr_mouse_y = event.mouse_region_y
                context.region.tag_redraw()

            # finish custom wait_for_input stage
            if event.value == 'PRESS':
                if event.type in {'LEFTMOUSE', 'MIDDLEMOUSE'}:
                    # restore cursor and status text, remove circle shader
                    self.finish_custom_wait_for_input_stage(context)
                    toggle_alter_mode(self, event)
                    self.invoke_inbuilt_circle_select(context, event)

                elif event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE',
                                    'NUMPAD_MINUS', 'NUMPAD_PLUS'}:
                    self.update_radius(context, event)

            # toggle select_through and update overlays and modifiers state
            if event.value in {'PRESS', 'RELEASE'} and \
                    event.type in self.select_through_toggle_keys:
                self.select_through = not self.select_through
                toggle_overlays(self, context)
                toggle_modifiers(self)
        else:
            # inbuilt select_circle was finished, now finish modal
            if event.value == 'RELEASE':
                self.finish_modal(context)
                return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def begin_custom_wait_for_input_stage(self, context, event):
        """Set cursor and status text, draw wait_for_input shader"""
        self.custom_wait_for_input_stage = True
        context.window.cursor_modal_set('CROSSHAIR')
        status_text = "RMB, ESC: Cancel  |  WhDown/Pad+: Add  |  WhUp/Pad-: Subtract  |  " \
                      "LMB: ADD  |  %s+LMB: %s" % (self.alter_mode_toggle_key, self.alter_mode)
        if self.select_through_toggle_key != 'DISABLED':
            status_text += "  |  %s: Toggle Select Through" % self.select_through_toggle_key
        context.workspace.status_text_set(text=status_text)

        sync_select_through(self, context)

        self.build_circle_shader()
        self.curr_mouse_x = event.mouse_region_x
        self.curr_mouse_y = event.mouse_region_y
        self.handler = context.space_data.draw_handler_add(
            self.draw_circle_shader, (), 'WINDOW', 'POST_PIXEL')
        context.region.tag_redraw()

    def update_radius(self, context, event):
        if event.type in {'WHEELUPMOUSE', 'NUMPAD_MINUS'}:
            self.radius -= 10
        elif event.type in {'WHEELDOWNMOUSE', 'NUMPAD_PLUS'}:
            self.radius += 10
        self.build_circle_shader()
        context.region.tag_redraw()

    def finish_custom_wait_for_input_stage(self, context):
        """Restore cursor and status text, remove shader"""
        self.custom_wait_for_input_stage = False
        self.wait_for_input = False
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(text=None)
        context.space_data.draw_handler_remove(self.handler, 'WINDOW')
        context.region.tag_redraw()

    def invoke_inbuilt_circle_select(self, context, event):
        bpy.ops.view3d.select_circle('INVOKE_DEFAULT', mode=self.mode,
                                     wait_for_input=self.wait_for_input, radius=self.radius)

    def finish_modal(self, context):
        restore_overlays(self, context)
        restore_modifiers(self)
        # store view3d.select_circle radius in the current operator properties
        # to use it in the next invoke
        sc = context.window_manager.operator_properties_last("view3d.select_circle")
        self.radius = sc.radius

    def build_circle_shader(self):
        sides = 40
        radius = self.radius
        # https://stackoverflow.com/questions/17258546/opengl-creating-a-circle-change-radius
        counts = np.arange(sides, dtype=np.float16)
        angles = np.multiply(counts, 2 * np.pi / sides)
        arr_x = np.multiply(np.cos(angles), radius)
        arr_y = np.multiply(np.sin(angles), radius)
        arr_xy = np.empty((sides * 2,), dtype=np.float16)
        arr_xy[0::2] = arr_x
        arr_xy[1::2] = arr_y
        arr_co = arr_xy.reshape((sides, 2))
        vertices = list(map(tuple, arr_co))

        segment = (Vector(vertices[0]) - Vector(vertices[1])).length
        lengths = [segment * i for i in range(40)]

        self.border_shader = gpu.types.GPUShader(self.border_vertex_shader,
                                                 self.border_fragment_shader)
        self.border_batch = batch_for_shader(self.border_shader, 'LINE_LOOP', {"pos": vertices,
                                                                               "len": lengths})
        self.unif_dash_color = self.border_shader.uniform_from_name("u_DashColor")
        self.unif_gap_color = self.border_shader.uniform_from_name("u_GapColor")

        vertices.append(vertices[0])  # ending triangle
        vertices.insert(0, (0, 0))  # starting vert of triangle fan
        self.inner_shader = gpu.types.GPUShader(self.inner_vertex_shader,
                                                self.inner_fragment_shader)
        self.inner_batch = batch_for_shader(self.inner_shader, 'TRI_FAN', {"pos": vertices})
        self.unif_inner_color = self.inner_shader.uniform_from_name("u_Color")

    def draw_circle_shader(self):
        matrix = gpu.matrix.get_projection_matrix()
        dash_color = (1.0, 1.0, 1.0, 1.0)
        gap_color = (0.5, 0.5, 0.5, 1.0)
        inner_color = (1.0, 1.0, 1.0, 0.05)

        self.border_shader.bind()
        self.border_shader.uniform_float("u_ViewProjectionMatrix", matrix)
        self.border_shader.uniform_float("u_X", self.curr_mouse_x)
        self.border_shader.uniform_float("u_Y", self.curr_mouse_y)
        self.border_shader.uniform_vector_float(self.unif_dash_color, pack("4f", *dash_color), 4)
        self.border_shader.uniform_vector_float(self.unif_gap_color, pack("4f", *gap_color), 4)
        self.border_batch.draw(self.border_shader)

        glEnable(GL_BLEND)
        self.inner_shader.bind()
        self.inner_shader.uniform_float("u_ViewProjectionMatrix", matrix)
        self.inner_shader.uniform_float("u_X", self.curr_mouse_x)
        self.inner_shader.uniform_float("u_Y", self.curr_mouse_y)
        self.inner_shader.uniform_vector_float(self.unif_inner_color, pack("4f", *inner_color), 4)
        self.inner_batch.draw(self.inner_shader)
        glDisable(GL_BLEND)


classes = (
    MESH_OT_select_circle_xray,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
