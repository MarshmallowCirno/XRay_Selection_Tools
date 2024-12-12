import ctypes
import time
from itertools import chain
from math import hypot

import bpy
import gpu
from bgl import (
    GL_ALWAYS,
    GL_BLEND,
    GL_EQUAL,
    GL_FALSE,
    GL_INVERT,
    GL_KEEP,
    GL_STENCIL_BUFFER_BIT,
    GL_STENCIL_TEST,
    GL_TRUE,
    glClear,
    glColorMask,
    glDisable,
    glEnable,
    glStencilFunc,
    glStencilMask,
    glStencilOp,
)
from gpu_extras.batch import batch_for_shader
from mathutils import geometry, Vector

from ...functions.geometry_tests import polygon_bbox
from ...functions.intersections.object_intersect import select_obs_in_lasso
from ...functions.modals.object_modal import (
    gather_overlays,
    get_xray_toggle_key_list,
    restore_overlays,
    set_properties,
    sync_properties,
    toggle_alt_mode,
    toggle_overlays,
)
from ...icon.lasso_cursor import lasso_cursor


# noinspection PyTypeChecker
class _UBO_struct(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ("u_X", ctypes.c_int),
        ("u_Y", ctypes.c_int),
        ("u_Scale", ctypes.c_float),
        ("u_Dashed", ctypes.c_bool),
        ("u_SegmentColor", 4 * ctypes.c_float),
        ("u_GapColor", 4 * ctypes.c_float),
        ("u_FillColor", 4 * ctypes.c_float),
        # ("_pad", ctypes.c_int * 1),
    ]


UBO_source = """
struct Data
{
  int u_X;
  int u_Y;
  float u_Scale;
  bool u_Dashed;
  vec4 u_SegmentColor;
  vec4 u_GapColor;
  vec4 u_FillColor;
};
"""

# Icon shader.
shader_info = gpu.types.GPUShaderCreateInfo()
shader_info.typedef_source(UBO_source)
shader_info.uniform_buf(0, "Data", "ub")
shader_info.push_constant('MAT4', "u_ViewProjectionMatrix")
shader_info.vertex_in(0, 'VEC2', "pos")

shader_info.vertex_source(
    """
    void main()
    {
      gl_Position = u_ViewProjectionMatrix * vec4(
        pos.x * ub.u_Scale + ub.u_X, pos.y * ub.u_Scale + ub.u_Y, 0.0f, 1.0f);
    }
    """
)
shader_info.fragment_out(0, 'VEC4', "FragColor")
shader_info.fragment_source(
    """
    void main()
    {
      FragColor = ub.u_SegmentColor;
    }
    """
)
ICON_SHADER = gpu.shader.create_from_info(shader_info)
del shader_info

# Fill shader.
shader_info = gpu.types.GPUShaderCreateInfo()
shader_info.typedef_source(UBO_source)
shader_info.uniform_buf(0, "Data", "ub")
shader_info.push_constant('MAT4', "u_ViewProjectionMatrix")
shader_info.vertex_in(0, 'VEC2', "pos")
shader_info.vertex_source(
    """
    void main()
    {
      gl_Position = u_ViewProjectionMatrix * vec4(pos.x, pos.y, 0.0f, 1.0f);
    }
    """
)
shader_info.fragment_out(0, 'VEC4', "FragColor")
shader_info.fragment_source(
    """
    void main()
    {
      FragColor = ub.u_FillColor;
    }
    """
)
FILL_SHADER = gpu.shader.create_from_info(shader_info)
del shader_info

# Border shader.
vert_out = gpu.types.GPUStageInterfaceInfo("my_interface")  # noqa
vert_out.smooth('FLOAT', "v_Len")

shader_info = gpu.types.GPUShaderCreateInfo()
shader_info.typedef_source(UBO_source)
shader_info.uniform_buf(0, "Data", "ub")
shader_info.push_constant('MAT4', "u_ViewProjectionMatrix")
shader_info.vertex_in(0, 'VEC2', "pos")
shader_info.vertex_in(1, 'FLOAT', "len")
shader_info.vertex_out(vert_out)
shader_info.vertex_source(
    """
    void main()
    {
      v_Len = len;
      gl_Position = u_ViewProjectionMatrix * vec4(pos.x, pos.y, 0.0f, 1.0f);
    }
    """
)
shader_info.fragment_out(0, 'VEC4', "FragColor")
shader_info.fragment_source(
    """
    void main()
    {
      float dash_size = 1;
      float gap_size = 1;
      vec4 col = ub.u_SegmentColor;
      if (ub.u_Dashed)
        if (fract(v_Len/(dash_size + gap_size)) > dash_size/(dash_size + gap_size))
          col = ub.u_GapColor;
        FragColor = col;
    }
    """
)
BORDER_SHADER = gpu.shader.create_from_info(shader_info)
del vert_out
del shader_info


# noinspection PyTypeChecker
class OBJECT_OT_select_lasso_xray(bpy.types.Operator):
    """Select items using lasso selection with x-ray"""

    bl_idname = "object.select_lasso_xray"
    bl_label = "Lasso Select X-Ray"
    bl_options = {'REGISTER'}

    mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ('SET', "Set", "Set a new selection", 'SELECT_SET', 1),
            ('ADD', "Extend", "Extend existing selection", 'SELECT_EXTEND', 2),
            ('SUB', "Subtract", "Subtract existing selection", 'SELECT_SUBTRACT', 3),
            ('XOR', "Difference", "Inverts existing selection", 'SELECT_DIFFERENCE', 4),
            ('AND', "Intersect", "Intersect existing selection", 'SELECT_INTERSECT', 5),
        ],
        default='SET',
        options={'SKIP_SAVE'},
    )
    alt_mode: bpy.props.EnumProperty(
        name="Alternate Mode",
        description="Alternate selection mode",
        items=[
            ('SET', "Select", "Set a new selection", 'SELECT_SET', 1),
            ('ADD', "Extend Selection", "Extend existing selection", 'SELECT_EXTEND', 2),
            ('SUB', "Deselect", "Subtract existing selection", 'SELECT_SUBTRACT', 3),
        ],
        default='SUB',
        options={'SKIP_SAVE'},
    )
    alt_mode_toggle_key: bpy.props.EnumProperty(
        name="Alternate Mode Toggle Key",
        description="Toggle selection mode by holding this key",
        items=[
            ('CTRL', "CTRL", ""),
            ('ALT', "ALT", ""),
            ('SHIFT', "SHIFT", ""),
        ],
        default='SHIFT',
        options={'SKIP_SAVE'},
    )
    wait_for_input: bpy.props.BoolProperty(
        name="Wait for input",
        description=(
            "Wait for mouse input or initialize lasso selection immediately "
            "(enable when assigning the operator to a keyboard key)"
        ),
        default=False,
    )
    override_global_props: bpy.props.BoolProperty(
        name="Override Global Properties",
        description="Use properties in this keymaps item instead of properties in the global addon settings",
        default=False,
        options={'SKIP_SAVE'},
    )
    show_xray: bpy.props.BoolProperty(
        name="Show X-Ray",
        description="Enable x-ray shading during selection",
        default=True,
        options={'SKIP_SAVE'},
    )
    xray_toggle_key: bpy.props.EnumProperty(
        name="X-Ray Toggle Key",
        description="Toggle x-ray by holding this key",
        items=[
            ('CTRL', "CTRL", ""),
            ('ALT', "ALT", ""),
            ('SHIFT', "SHIFT", ""),
            ('DISABLED', "DISABLED", ""),
        ],
        default='DISABLED',
        options={'SKIP_SAVE'},
    )
    xray_toggle_type: bpy.props.EnumProperty(
        name="Toggle X-Ray by Press or Hold",
        description="Toggle x-ray by holding or by pressing key",
        items=[
            ('HOLD', "Holding", ""),
            ('PRESS', "Pressing", ""),
        ],
        default='HOLD',
        options={'SKIP_SAVE'},
    )
    hide_gizmo: bpy.props.BoolProperty(
        name="Hide Gizmo",
        description="Temporary hide gizmo of the active tool",
        default=False,
        options={'SKIP_SAVE'},
    )
    show_lasso_icon: bpy.props.BoolProperty(
        name="Show Lasso Icon",
        description="Show lasso cursor icon when wait_for_input is enabled",
        default=True,
        options={'SKIP_SAVE'},
    )
    behavior: bpy.props.EnumProperty(
        name="Selection Behavior",
        description="Selection behavior",
        items=[
            ('ORIGIN', "Origin (Default)", "Select objects by origins", 'DOT', 1),
            ('CONTAIN', "Contain", "Select only the objects fully contained in lasso", 'STICKY_UVS_LOC', 2),
            ('OVERLAP', "Overlap", "Select objects overlapping lasso", 'SELECT_SUBTRACT', 3),
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

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode == 'OBJECT'

    def __init__(self, *args, **kwargs):
        if bpy.app.version >= (4, 4, 0):
            super().__init__(*args, **kwargs)

        self.path = None
        self.stage = None
        self.curr_mode = self.mode
        self.curr_behavior = self.behavior

        self.lasso_poly = []
        self.lasso_xmin = 0
        self.lasso_xmax = 0
        self.lasso_ymin = 0
        self.lasso_ymax = 0

        self.last_mouse_region_x = 0
        self.last_mouse_region_y = 0

        self.init_overlays = None

        self.override_wait_for_input = True
        self.override_selection = False
        self.override_intersect_tests = False

        self.xray_toggle_key_list = get_xray_toggle_key_list()

        self.handler = None
        self.icon_batch = None
        self.UBO_data = _UBO_struct()
        self.UBO = gpu.types.GPUUniformBuf(
            gpu.types.Buffer("UBYTE", ctypes.sizeof(self.UBO_data), self.UBO_data)  # noqa
        )

    def invoke(self, context, event):
        set_properties(self, tool='LASSO')

        self.override_intersect_tests = self.behavior != 'ORIGIN'

        self.override_selection = (
            self.xray_toggle_key != 'DISABLED'
            or self.alt_mode_toggle_key != 'SHIFT'
            or self.alt_mode != 'SUB'
            or self.override_intersect_tests
        )

        self.init_overlays = gather_overlays(context)  # save initial x-ray overlay states

        # Sync operator properties with current shading.
        sync_properties(self, context)

        # Enable x-ray overlays.
        toggle_overlays(self, context)

        context.window_manager.modal_handler_add(self)

        # Jump to.
        if self.wait_for_input and self.override_wait_for_input:
            self.begin_custom_wait_for_input_stage(context, event)
        elif self.override_selection:
            self.begin_custom_selection_stage(context, event)
        else:
            self.invoke_inbuilt_lasso_select()
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if self.stage == 'CUSTOM_WAIT_FOR_INPUT':
            # Update shader.
            if event.type == 'MOUSEMOVE':
                self.update_shader_position(context, event)

            # Toggle overlays.
            if event.type in self.xray_toggle_key_list:
                if (
                    event.value in {'PRESS', 'RELEASE'}
                    and self.xray_toggle_type == 'HOLD'
                    or event.value == 'PRESS'
                    and self.xray_toggle_type == 'PRESS'
                ):
                    self.show_xray = not self.show_xray
                    toggle_overlays(self, context)

            # Finish stage.
            if event.value == 'PRESS' and event.type in {'LEFTMOUSE', 'MIDDLEMOUSE'}:
                self.finish_custom_wait_for_input_stage(context)
                toggle_alt_mode(self, event)
                if self.override_selection:
                    self.begin_custom_selection_stage(context, event)
                else:
                    self.invoke_inbuilt_lasso_select()

        if self.stage == 'CUSTOM_SELECTION':
            if event.type == 'MOUSEMOVE':
                # To simplify path and improve performance
                # only append points with enough distance between them.
                if (
                    hypot(
                        event.mouse_region_x - self.last_mouse_region_x, event.mouse_region_y - self.last_mouse_region_y
                    )
                    > 10
                ):

                    # Append path point.
                    self.path.append(
                        {"name": "", "loc": (event.mouse_region_x, event.mouse_region_y), "time": time.time()}
                    )
                    self.lasso_poly.append((event.mouse_region_x, event.mouse_region_y))
                    self.lasso_xmin, self.lasso_xmax, self.lasso_ymin, self.lasso_ymax = polygon_bbox(self.lasso_poly)

                    self.update_directional_behavior()
                    self.update_shader_position(context, event)

            # Toggle overlays.
            if event.type in self.xray_toggle_key_list:
                if (
                    event.value in {'PRESS', 'RELEASE'}
                    and self.xray_toggle_type == 'HOLD'
                    or event.value == 'PRESS'
                    and self.xray_toggle_type == 'PRESS'
                ):
                    self.show_xray = not self.show_xray
                    toggle_overlays(self, context)

            # Finish stage.
            if event.value == 'RELEASE' and event.type in {'LEFTMOUSE', 'MIDDLEMOUSE', 'RIGHTMOUSE'}:
                self.finish_custom_selection_stage(context)
                if self.override_intersect_tests:
                    self.begin_custom_intersect_tests(context)
                    self.finish_modal(context)
                    bpy.ops.ed.undo_push(message="Lasso Select")
                    return {'FINISHED'}

                self.exec_inbuilt_lasso_select()
                self.finish_modal(context)
                bpy.ops.ed.undo_push(message="Lasso Select")
                return {'FINISHED'}

        if self.stage == 'INBUILT_OP':
            # Inbuilt op was finished, now finish modal.
            if event.type == 'MOUSEMOVE':
                self.finish_modal(context)
                return {'FINISHED'}

        # Cancel modal.
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            if self.stage == 'CUSTOM_WAIT_FOR_INPUT':
                self.finish_custom_wait_for_input_stage(context)
            elif self.stage == 'CUSTOM_SELECTION':
                self.finish_custom_selection_stage(context)
            self.finish_modal(context)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def begin_custom_wait_for_input_stage(self, context, event):
        """Set cursor and status text, draw wait_for_input shader."""
        self.stage = 'CUSTOM_WAIT_FOR_INPUT'
        context.window.cursor_modal_set('CROSSHAIR')
        enum_items = self.properties.bl_rna.properties["mode"].enum_items
        curr_mode_name = enum_items[self.curr_mode].name
        enum_items = self.properties.bl_rna.properties["alt_mode"].enum_items
        alt_mode_name = enum_items[self.alt_mode].name

        status_text = f"RMB, ESC: Cancel  |  LMB: {curr_mode_name}  |  {self.alt_mode_toggle_key}+LMB: {alt_mode_name}"
        if self.xray_toggle_key != 'DISABLED':
            status_text += f"  |  {self.xray_toggle_key}: Toggle X-Ray"
        context.workspace.status_text_set(text=status_text)

        if self.show_lasso_icon:
            self.build_icon_shader()
            self.handler = context.space_data.draw_handler_add(self.draw_icon_shader, (), 'WINDOW', 'POST_PIXEL')
            self.update_shader_position(context, event)

    def finish_custom_wait_for_input_stage(self, context):
        """Restore cursor and status text, remove wait_for_input shader."""
        self.wait_for_input = False
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(text=None)
        if self.show_lasso_icon:
            context.space_data.draw_handler_remove(self.handler, 'WINDOW')
            context.region.tag_redraw()

    def begin_custom_selection_stage(self, context, event):
        self.stage = 'CUSTOM_SELECTION'
        context.window.cursor_modal_set('CROSSHAIR')
        status_text = "RMB, ESC: Cancel"
        if self.xray_toggle_key != 'DISABLED':
            status_text += f"  |  {self.xray_toggle_key}: Toggle X-Ray"
        context.workspace.status_text_set(text=status_text)

        # Store initial path point.
        self.path = [{"name": "", "loc": (event.mouse_region_x, event.mouse_region_y), "time": time.time()}]
        self.lasso_poly = [(event.mouse_region_x, event.mouse_region_y)]
        # For hypot calculation.
        self.last_mouse_region_x = event.mouse_region_x
        self.last_mouse_region_y = event.mouse_region_y

        if bpy.app.version >= (4, 0, 0):
            self.handler = context.space_data.draw_handler_add(self.draw_lasso_shader, (), 'WINDOW', 'POST_PIXEL')
        else:
            self.handler = context.space_data.draw_handler_add(
                self.draw_lasso_shader_bgl, (context,), 'WINDOW', 'POST_PIXEL'
            )
        self.update_shader_position(context, event)

    def finish_custom_selection_stage(self, context):
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(text=None)
        context.space_data.draw_handler_remove(self.handler, 'WINDOW')
        context.region.tag_redraw()

    def invoke_inbuilt_lasso_select(self):
        self.stage = 'INBUILT_OP'
        bpy.ops.view3d.select_lasso('INVOKE_DEFAULT', mode=self.curr_mode)

    def exec_inbuilt_lasso_select(self):
        bpy.ops.view3d.select_lasso(path=self.path, mode=self.curr_mode)

    def begin_custom_intersect_tests(self, context):
        select_obs_in_lasso(context, mode=self.curr_mode, lasso_poly=self.lasso_poly, behavior=self.curr_behavior)

    def finish_modal(self, context):
        restore_overlays(self, context)

    def update_directional_behavior(self):
        if self.behavior in {'DIRECTIONAL', 'DIRECTIONAL_REVERSED'}:
            start_x = self.lasso_poly[0][0]
            right_to_left = abs(self.lasso_xmin - start_x) < abs(self.lasso_xmax - start_x)
            if (
                right_to_left
                and self.behavior == 'DIRECTIONAL'
                or not right_to_left
                and self.behavior == 'DIRECTIONAL_REVERSED'
            ):
                self.curr_behavior = 'OVERLAP'
            else:
                self.curr_behavior = 'CONTAIN'

    def update_ubo(self):
        self.UBO.update(gpu.types.Buffer("UBYTE", ctypes.sizeof(self.UBO_data), self.UBO_data))  # noqa

    def update_shader_position(self, context, event):
        self.last_mouse_region_x = event.mouse_region_x
        self.last_mouse_region_y = event.mouse_region_y
        context.region.tag_redraw()

    def build_icon_shader(self):
        vertices = lasso_cursor

        lengths = [0]
        for a, b in zip(vertices[:-1], vertices[1:]):
            lengths.append(lengths[-1] + (a - b).length)

        self.icon_batch = batch_for_shader(ICON_SHADER, 'LINES', {"pos": vertices})

    def draw_icon_shader(self):
        matrix = gpu.matrix.get_projection_matrix()
        segment_color = (1.0, 1.0, 1.0, 1.0)

        # UBO.
        self.UBO_data.u_X = self.last_mouse_region_x
        self.UBO_data.u_Y = self.last_mouse_region_y
        self.UBO_data.u_Scale = 25
        self.UBO_data.u_SegmentColor = segment_color
        self.update_ubo()

        # Icon.
        ICON_SHADER.bind()
        ICON_SHADER.uniform_block("ub", self.UBO)
        ICON_SHADER.uniform_float("u_ViewProjectionMatrix", matrix)
        self.icon_batch.draw(ICON_SHADER)

    def draw_lasso_shader_bgl(self, context):
        # Create batches.
        vertices = [Vector(v) for v in self.lasso_poly]
        vertices.append(Vector(self.lasso_poly[0]))

        lengths = [0]
        for a, b in zip(vertices[:-1], vertices[1:]):
            lengths.append(lengths[-1] + (a - b).length)

        bbox_vertices = (
            (self.lasso_xmin, self.lasso_ymax),
            (self.lasso_xmin, self.lasso_ymin),
            (self.lasso_xmax, self.lasso_ymin),
            (self.lasso_xmax, self.lasso_ymax),
        )

        fill_batch = batch_for_shader(FILL_SHADER, 'TRI_FAN', {"pos": vertices})
        border_batch = batch_for_shader(BORDER_SHADER, 'LINE_STRIP', {"pos": vertices, "len": lengths})
        stencil_batch = batch_for_shader(FILL_SHADER, 'TRI_FAN', {"pos": bbox_vertices})

        matrix = gpu.matrix.get_projection_matrix()
        segment_color = (1.0, 1.0, 1.0, 1.0)
        gap_color = (0.2, 0.2, 0.2, 1.0)
        shadow_color = (0.3, 0.3, 0.3, 1.0)
        fill_color = (1.0, 1.0, 1.0, 0.04)
        dashed = not self.curr_behavior == 'CONTAIN'

        # UBO.
        self.UBO_data.u_FillColor = fill_color
        self.UBO_data.u_Dashed = dashed
        self.UBO_data.u_GapColor = gap_color
        self.UBO_data.u_SegmentColor = segment_color
        self.update_ubo()

        # Stencil mask.
        # https://stackoverflow.com/a/25468363/5106051
        glClear(GL_STENCIL_BUFFER_BIT)
        glEnable(GL_STENCIL_TEST)
        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
        glStencilFunc(GL_ALWAYS, 0, 1)
        glStencilOp(GL_KEEP, GL_KEEP, GL_INVERT)
        glStencilMask(1)

        FILL_SHADER.bind()
        FILL_SHADER.uniform_block("ub", self.UBO)
        FILL_SHADER.uniform_float("u_ViewProjectionMatrix", matrix)
        fill_batch.draw(FILL_SHADER)

        if context.space_data.shading.type in {'MATERIAL', 'RENDERED'}:
            glStencilFunc(GL_EQUAL, 0, 1)
        else:
            glStencilFunc(GL_EQUAL, 1, 1)
        glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)

        # Fill.
        glEnable(GL_BLEND)
        stencil_batch.draw(FILL_SHADER)
        glDisable(GL_BLEND)

        # Border.
        if not dashed:
            # Solid border shadow.
            self.UBO_data.u_SegmentColor = shadow_color
            self.update_ubo()

            gpu.state.line_width_set(3)
            BORDER_SHADER.bind()
            BORDER_SHADER.uniform_block("ub", self.UBO)
            BORDER_SHADER.uniform_float("u_ViewProjectionMatrix", matrix)
            border_batch.draw(BORDER_SHADER)
            gpu.state.line_width_set(1)

            # Solid border.
            self.UBO_data.u_SegmentColor = segment_color
            self.update_ubo()

            glDisable(GL_STENCIL_TEST)
            BORDER_SHADER.uniform_block("ub", self.UBO)
            border_batch.draw(BORDER_SHADER)

        else:
            # Dashed border.
            glDisable(GL_STENCIL_TEST)
            BORDER_SHADER.bind()
            BORDER_SHADER.uniform_block("ub", self.UBO)
            BORDER_SHADER.uniform_float("u_ViewProjectionMatrix", matrix)
            border_batch.draw(BORDER_SHADER)

    def draw_lasso_shader(self):
        # Create batches.
        vertices = [Vector(v) for v in self.lasso_poly]
        vertices.append(Vector(self.lasso_poly[0]))

        indices = geometry.tessellate_polygon((self.lasso_poly,))
        triangles = [self.lasso_poly[i] for i in chain.from_iterable(indices)]

        lengths = [0]
        for a, b in zip(vertices[:-1], vertices[1:]):
            lengths.append(lengths[-1] + (a - b).length)

        fill_batch = batch_for_shader(FILL_SHADER, 'TRIS', {"pos": triangles})
        border_batch = batch_for_shader(BORDER_SHADER, 'LINE_STRIP', {"pos": vertices, "len": lengths})

        matrix = gpu.matrix.get_projection_matrix()
        segment_color = (1.0, 1.0, 1.0, 1.0)
        gap_color = (0.2, 0.2, 0.2, 1.0)
        shadow_color = (0.3, 0.3, 0.3, 1.0)
        fill_color = (1.0, 1.0, 1.0, 0.04)
        dashed = not self.curr_behavior == 'CONTAIN'

        # UBO.
        self.UBO_data.u_FillColor = fill_color
        self.UBO_data.u_Dashed = dashed
        self.UBO_data.u_GapColor = gap_color
        self.UBO_data.u_SegmentColor = segment_color
        self.update_ubo()

        # Fill.
        gpu.state.blend_set('ALPHA')
        FILL_SHADER.bind()
        FILL_SHADER.uniform_block("ub", self.UBO)
        FILL_SHADER.uniform_float("u_ViewProjectionMatrix", matrix)
        fill_batch.draw(FILL_SHADER)
        gpu.state.blend_set('NONE')

        # Border.
        if not dashed:
            # Solid border shadow.
            self.UBO_data.u_SegmentColor = shadow_color
            self.update_ubo()

            gpu.state.line_width_set(3)
            BORDER_SHADER.bind()
            BORDER_SHADER.uniform_block("ub", self.UBO)
            BORDER_SHADER.uniform_float("u_ViewProjectionMatrix", matrix)
            border_batch.draw(BORDER_SHADER)
            gpu.state.line_width_set(1)

            # Solid border.
            self.UBO_data.u_SegmentColor = segment_color
            self.update_ubo()

            BORDER_SHADER.uniform_block("ub", self.UBO)
            border_batch.draw(BORDER_SHADER)

        else:
            # Dashed border.
            BORDER_SHADER.bind()
            BORDER_SHADER.uniform_block("ub", self.UBO)
            BORDER_SHADER.uniform_float("u_ViewProjectionMatrix", matrix)
            border_batch.draw(BORDER_SHADER)
