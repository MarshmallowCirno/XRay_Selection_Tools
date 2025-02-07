import ctypes
import itertools
import math
import time

import bgl
import bpy
import gpu
import mathutils
from gpu_extras import batch

from ... import addon_info
from ...functions import geometry_tests
from ...functions.intersections import mesh_intersect
from ...functions.modals import mesh_modal
from ...icon import lasso_cursor


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


_UBO_source = """
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
_shader_info = gpu.types.GPUShaderCreateInfo()
_shader_info.typedef_source(_UBO_source)
_shader_info.uniform_buf(0, "Data", "ub")
_shader_info.push_constant('MAT4', "u_ViewProjectionMatrix")
_shader_info.vertex_in(0, 'VEC2', "pos")

_shader_info.vertex_source(
    """
    void main()
    {
      gl_Position = u_ViewProjectionMatrix * vec4(
        pos.x * ub.u_Scale + ub.u_X, pos.y * ub.u_Scale + ub.u_Y, 0.0f, 1.0f);
    }
    """
)
_shader_info.fragment_out(0, 'VEC4', "FragColor")
_shader_info.fragment_source(
    """
    void main()
    {
      FragColor = ub.u_SegmentColor;
    }
    """
)
_ICON_SHADER = gpu.shader.create_from_info(_shader_info)
del _shader_info

# Fill shader.
_shader_info = gpu.types.GPUShaderCreateInfo()
_shader_info.typedef_source(_UBO_source)
_shader_info.uniform_buf(0, "Data", "ub")
_shader_info.push_constant('MAT4', "u_ViewProjectionMatrix")
_shader_info.vertex_in(0, 'VEC2', "pos")
_shader_info.vertex_source(
    """
    void main()
    {
      gl_Position = u_ViewProjectionMatrix * vec4(pos.x, pos.y, 0.0f, 1.0f);
    }
    """
)
_shader_info.fragment_out(0, 'VEC4', "FragColor")
_shader_info.fragment_source(
    """
    void main()
    {
      FragColor = ub.u_FillColor;
    }
    """
)
_FILL_SHADER = gpu.shader.create_from_info(_shader_info)
del _shader_info

# Border shader.
_vert_out = gpu.types.GPUStageInterfaceInfo("my_interface")  # noqa
_vert_out.smooth('FLOAT', "v_Len")

_shader_info = gpu.types.GPUShaderCreateInfo()
_shader_info.typedef_source(_UBO_source)
_shader_info.uniform_buf(0, "Data", "ub")
_shader_info.push_constant('MAT4', "u_ViewProjectionMatrix")
_shader_info.vertex_in(0, 'VEC2', "pos")
_shader_info.vertex_in(1, 'FLOAT', "len")
_shader_info.vertex_out(_vert_out)
_shader_info.vertex_source(
    """
    void main()
    {
      v_Len = len;
      gl_Position = u_ViewProjectionMatrix * vec4(pos.x, pos.y, 0.0f, 1.0f);
    }
    """
)
_shader_info.fragment_out(0, 'VEC4', "FragColor")
_shader_info.fragment_source(
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
_BORDER_SHADER = gpu.shader.create_from_info(_shader_info)
del _vert_out
del _shader_info


# noinspection PyTypeChecker
class MESH_OT_select_lasso_xray(bpy.types.Operator):
    """Select items using lasso selection with x-ray"""

    bl_idname = "mesh.select_lasso_xray"
    bl_label = "Lasso Select X-Ray"
    bl_options = {'REGISTER', 'GRAB_CURSOR'}

    mode: bpy.props.EnumProperty(
        name="Mode",
        description="Default selection mode",
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
        name="Wait for Input",
        description=(
            "Wait for mouse input or initialize lasso selection immediately (usually you "
            "should enable it when you assign the operator to a keyboard key)"
        ),
        default=False,
        options={'SKIP_SAVE'},
    )
    override_global_props: bpy.props.BoolProperty(
        name="Override Global Properties",
        description="Use properties in this keymaps item instead of properties in the global addon settings",
        default=False,
        options={'SKIP_SAVE'},
    )
    select_through: bpy.props.BoolProperty(
        name="Select Through",
        description="Select verts, faces and edges laying underneath",
        default=True,
        options={'SKIP_SAVE'},
    )
    select_through_toggle_key: bpy.props.EnumProperty(
        name="Selection Through Toggle Key",
        description="Toggle selection through by holding this key",
        items=[
            ('CTRL', "CTRL", ""),
            ('ALT', "ALT", ""),
            ('SHIFT', "SHIFT", ""),
            ('DISABLED', "DISABLED", ""),
        ],
        default='DISABLED',
        options={'SKIP_SAVE'},
    )
    select_through_toggle_type: bpy.props.EnumProperty(
        name="Selection Through Toggle Press / Hold",
        description="Toggle selection through by holding or by pressing key",
        items=[
            ('HOLD', "Holding", ""),
            ('PRESS', "Pressing", ""),
        ],
        default='HOLD',
        options={'SKIP_SAVE'},
    )
    default_color: bpy.props.FloatVectorProperty(
        name="Default Color",
        description="Tool color when disabled selection through",
        subtype='COLOR',
        soft_min=0.0,
        soft_max=1.0,
        size=3,
        default=(1.0, 1.0, 1.0),
        options={'SKIP_SAVE'},
    )
    select_through_color: bpy.props.FloatVectorProperty(
        name="Select Through Color",
        description="Tool color when enabled selection through",
        subtype='COLOR',
        soft_min=0.0,
        soft_max=1.0,
        size=3,
        default=(1.0, 1.0, 1.0),
        options={'SKIP_SAVE'},
    )
    show_xray: bpy.props.BoolProperty(
        name="Show X-Ray",
        description="Enable x-ray shading during selection",
        default=True,
        options={'SKIP_SAVE'},
    )
    select_all_edges: bpy.props.BoolProperty(
        name="Select All Edges",
        description=(
            "Additionally select edges that are partially inside the selection lasso, "
            "not just the ones completely inside the selection lasso. Works only in "
            "select through mode"
        ),
        default=False,
        options={'SKIP_SAVE'},
    )
    select_all_faces: bpy.props.BoolProperty(
        name="Select All Faces",
        description=(
            "Additionally select faces that are partially inside the selection lasso, "
            "not just the ones with centers inside the selection lasso. Works only in "
            "select through mode"
        ),
        default=False,
        options={'SKIP_SAVE'},
    )
    select_backfacing: bpy.props.BoolProperty(
        name="Select Backfacing",
        description="Select elements with normals facing away from you. Works only in select through mode",
        default=True,
        options={'SKIP_SAVE'},
    )
    hide_mirror: bpy.props.BoolProperty(
        name="Hide Mirror",
        description="Hide mirror modifiers during selection",
        default=True,
        options={'SKIP_SAVE'},
    )
    hide_solidify: bpy.props.BoolProperty(
        name="Hide Solidify",
        description="Hide solidify modifiers during selection",
        default=True,
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

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode == 'EDIT_MESH'

    def __init__(self, *args, **kwargs):
        if bpy.app.version >= (4, 4, 0):
            super().__init__(*args, **kwargs)

        self.path = None
        self.stage = None
        self.curr_mode = self.mode
        self.directional = (
            addon_info.get_preferences().mesh_tools.directional_lasso_tool and not self.override_global_props
        )
        self.direction = None

        self.lasso_poly = []
        self.lasso_xmin = 0
        self.lasso_xmax = 0
        self.lasso_ymin = 0
        self.lasso_ymax = 0

        self.last_mouse_region_x = 0
        self.last_mouse_region_y = 0

        self.init_mods = None
        self.init_overlays = None

        self.override_wait_for_input = True
        self.override_selection = False
        self.override_intersect_tests = False

        self.invert_select_through = False
        self.select_through_toggle_key_list = mesh_modal.get_select_through_toggle_key_list()

        self.handler = None
        self.icon_batch = None
        self.UBO_data = _UBO_struct()
        self.UBO = gpu.types.GPUUniformBuf(
            gpu.types.Buffer("UBYTE", ctypes.sizeof(self.UBO_data), self.UBO_data)  # noqa
        )

    def invoke(self, context, event):
        # Set operator properties from addon preferences.
        mesh_modal.set_properties_from_preferences(self, tool='LASSO')

        self.override_intersect_tests = (
            self.select_all_faces
            and context.tool_settings.mesh_select_mode[2]
            or self.select_all_edges
            and context.tool_settings.mesh_select_mode[1]
            or not self.select_backfacing
            or bpy.app.version >= (4, 1, 0)
            and self.select_through
            and not self.show_xray
        )

        self.override_selection = (
            self.select_through_toggle_key != 'DISABLED'
            or self.alt_mode_toggle_key != 'SHIFT'
            or self.alt_mode != 'SUB'
            or not self.select_through
            and self.default_color[:] != (1.0, 1.0, 1.0)
            or self.select_through
            and self.select_through_color[:] != (1.0, 1.0, 1.0)
            or self.directional
            or self.override_intersect_tests
        )

        self.init_mods = mesh_modal.gather_modifiers(self, context)  # save initial modifier states
        self.init_overlays = mesh_modal.gather_overlays(context)  # save initial x-ray overlay states

        # Set x-ray overlays and modifiers.
        mesh_modal.initialize_shading_from_properties(self, context)
        mesh_modal.set_modifiers_from_properties(self)

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

            # Toggle modifiers and overlays.
            if event.type in self.select_through_toggle_key_list:
                if (
                    event.value in {'PRESS', 'RELEASE'}
                    and self.select_through_toggle_type == 'HOLD'
                    or event.value == 'PRESS'
                    and self.select_through_toggle_type == 'PRESS'
                ):
                    self.invert_select_through = not self.invert_select_through
                    mesh_modal.set_shading_from_properties(self, context)
                    mesh_modal.update_shader_color(self, context)

            # Finish stage.
            if event.value == 'PRESS' and event.type in {'LEFTMOUSE', 'MIDDLEMOUSE'}:
                self.finish_custom_wait_for_input_stage(context)
                mesh_modal.toggle_alt_mode(self, event)
                if self.override_selection:
                    self.begin_custom_selection_stage(context, event)
                else:
                    self.invoke_inbuilt_lasso_select()

        if self.stage == 'CUSTOM_SELECTION':
            if event.type == 'MOUSEMOVE':
                # To simplify path and improve performance
                # only append points with enough distance between them.
                if (
                    math.hypot(
                        event.mouse_region_x - self.last_mouse_region_x, event.mouse_region_y - self.last_mouse_region_y
                    )
                    > 10
                ):
                    # Append path point.
                    self.path.append(
                        {"name": "", "loc": (event.mouse_region_x, event.mouse_region_y), "time": time.time()}
                    )
                    self.lasso_poly.append((event.mouse_region_x, event.mouse_region_y))
                    self.lasso_xmin, self.lasso_xmax, self.lasso_ymin, self.lasso_ymax = geometry_tests.polygon_bbox(
                        tuple(self.lasso_poly)
                    )
                    self.update_direction_and_properties(context)
                    self.update_shader_position(context, event)

            # Toggle modifiers and overlays.
            if event.type in self.select_through_toggle_key_list:
                if (
                    event.value in {'PRESS', 'RELEASE'}
                    and self.select_through_toggle_type == 'HOLD'
                    or event.value == 'PRESS'
                    and self.select_through_toggle_type == 'PRESS'
                ):
                    self.invert_select_through = not self.invert_select_through
                    mesh_modal.set_shading_from_properties(self, context)
                    mesh_modal.update_shader_color(self, context)

            # Finish stage.
            if event.value == 'RELEASE' and event.type in {'LEFTMOUSE', 'MIDDLEMOUSE', 'RIGHTMOUSE'}:
                self.finish_custom_selection_stage(context)
                if self.override_intersect_tests and (
                    self.select_through
                    and not self.invert_select_through
                    or not self.select_through
                    and self.invert_select_through
                ):
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
        """Set status text, draw wait_for_input shader."""
        self.stage = 'CUSTOM_WAIT_FOR_INPUT'
        enum_items = self.properties.bl_rna.properties["mode"].enum_items
        curr_mode_name = enum_items[self.curr_mode].name
        enum_items = self.properties.bl_rna.properties["alt_mode"].enum_items
        alt_mode_name = enum_items[self.alt_mode].name

        status_text = f"RMB, ESC: Cancel  |  LMB: {curr_mode_name}  |  {self.alt_mode_toggle_key}+LMB: {alt_mode_name}"
        if self.select_through_toggle_key != 'DISABLED' and not self.directional:
            status_text += f"  |  {self.select_through_toggle_key}: Toggle Select Through"
        context.workspace.status_text_set(text=status_text)

        if self.show_lasso_icon:
            self.build_icon_shader()
            self.handler = context.space_data.draw_handler_add(self.draw_icon_shader, (), 'WINDOW', 'POST_PIXEL')
            self.update_shader_position(context, event)

    def finish_custom_wait_for_input_stage(self, context):
        """Restore status text, remove wait_for_input shader."""
        self.wait_for_input = False
        context.workspace.status_text_set(text=None)
        if self.show_lasso_icon:
            context.space_data.draw_handler_remove(self.handler, 'WINDOW')
            context.region.tag_redraw()

    def begin_custom_selection_stage(self, context, event):
        self.stage = 'CUSTOM_SELECTION'

        status_text = "RMB, ESC: Cancel"
        if self.select_through_toggle_key != 'DISABLED':
            status_text += f"  |  {self.select_through_toggle_key}: Toggle Select Through"
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
        context.workspace.status_text_set(text=None)
        context.space_data.draw_handler_remove(self.handler, 'WINDOW')
        context.region.tag_redraw()

    def invoke_inbuilt_lasso_select(self):
        self.stage = 'INBUILT_OP'
        bpy.ops.view3d.select_lasso('INVOKE_DEFAULT', mode=self.curr_mode)

    def exec_inbuilt_lasso_select(self):
        bpy.ops.view3d.select_lasso(path=self.path, mode=self.curr_mode)

    def begin_custom_intersect_tests(self, context):
        mesh_intersect.select_mesh_elements(
            context,
            mode=self.curr_mode,
            tool='LASSO',
            tool_co_kwargs={"lasso_poly": tuple(self.lasso_poly)},
            select_all_edges=self.select_all_edges,
            select_all_faces=self.select_all_faces,
            select_backfacing=self.select_backfacing,
        )

    def finish_modal(self, context):
        mesh_modal.restore_overlays(self, context)
        mesh_modal.restore_modifiers(self)

    def update_direction_and_properties(self, context):
        start_x = self.lasso_poly[0][0]
        if self.directional and self.last_mouse_region_x != start_x:
            if abs(self.lasso_xmin - start_x) < abs(self.lasso_xmax - start_x):
                direction = "LEFT_TO_RIGHT"
            else:
                direction = "RIGHT_TO_LEFT"

            if direction != self.direction:
                self.direction = direction
                mesh_modal.set_properties_from_direction(self, self.direction)
                self.override_intersect_tests = (
                    self.select_all_faces
                    and context.tool_settings.mesh_select_mode[2]
                    or self.select_all_edges
                    and context.tool_settings.mesh_select_mode[1]
                    or not self.select_backfacing
                    or bpy.app.version >= (4, 1, 0)
                    and self.select_through
                    and not self.show_xray
                )
                mesh_modal.set_shading_from_properties(self, context)

    def update_ubo(self):
        self.UBO.update(gpu.types.Buffer("UBYTE", ctypes.sizeof(self.UBO_data), self.UBO_data))  # noqa

    def update_shader_position(self, context, event):
        self.last_mouse_region_x = event.mouse_region_x
        self.last_mouse_region_y = event.mouse_region_y
        context.region.tag_redraw()

    def build_icon_shader(self):
        vertices = lasso_cursor.lasso_cursor

        lengths = [0]
        for a, b in zip(vertices[:-1], vertices[1:]):
            lengths.append(lengths[-1] + (a - b).length)

        self.icon_batch = batch.batch_for_shader(_ICON_SHADER, 'LINES', {"pos": vertices})

    def draw_icon_shader(self):
        matrix = gpu.matrix.get_projection_matrix()
        if (
            self.select_through
            and not self.invert_select_through
            or not self.select_through
            and self.invert_select_through
        ):
            segment_color = (*self.select_through_color, 1)
        else:
            segment_color = (*self.default_color, 1)

        # UBO.
        self.UBO_data.u_X = self.last_mouse_region_x
        self.UBO_data.u_Y = self.last_mouse_region_y
        self.UBO_data.u_Scale = 25
        self.UBO_data.u_SegmentColor = segment_color
        self.update_ubo()

        # Icon.
        _ICON_SHADER.bind()
        _ICON_SHADER.uniform_block("ub", self.UBO)
        _ICON_SHADER.uniform_float("u_ViewProjectionMatrix", matrix)
        self.icon_batch.draw(_ICON_SHADER)

    def draw_lasso_shader_bgl(self, context):
        # Create batches.
        vertices = [mathutils.Vector(v) for v in self.lasso_poly]
        vertices.append(mathutils.Vector(self.lasso_poly[0]))

        lengths = [0]
        for a, b in zip(vertices[:-1], vertices[1:]):
            lengths.append(lengths[-1] + (a - b).length)

        bbox_vertices = (
            (self.lasso_xmin, self.lasso_ymax),
            (self.lasso_xmin, self.lasso_ymin),
            (self.lasso_xmax, self.lasso_ymin),
            (self.lasso_xmax, self.lasso_ymax),
        )

        border_batch = batch.batch_for_shader(_BORDER_SHADER, 'LINE_STRIP', {"pos": vertices, "len": lengths})
        fill_batch = batch.batch_for_shader(_FILL_SHADER, 'TRI_FAN', {"pos": vertices})
        stencil_batch = batch.batch_for_shader(_FILL_SHADER, 'TRI_FAN', {"pos": bbox_vertices})

        matrix = gpu.matrix.get_projection_matrix()
        if (
            self.select_through
            and not self.invert_select_through
            or not self.select_through
            and self.invert_select_through
        ):
            segment_color = (*self.select_through_color, 1)
            fill_color = (*self.select_through_color, 0.04)
        else:
            segment_color = (*self.default_color, 1)
            fill_color = (*self.default_color, 0.04)
        gap_color = (0.0, 0.0, 0.0, 1.0)
        shadow_color = (0.3, 0.3, 0.3, 1.0)
        dashed = not self.direction == "RIGHT_TO_LEFT"

        # UBO.
        self.UBO_data.u_FillColor = fill_color
        self.UBO_data.u_Dashed = dashed
        self.UBO_data.u_GapColor = gap_color
        self.UBO_data.u_SegmentColor = segment_color
        self.update_ubo()

        # Stencil mask.
        # https://stackoverflow.com/a/25468363/5106051
        bgl.glClear(bgl.GL_STENCIL_BUFFER_BIT)
        bgl.glEnable(bgl.GL_STENCIL_TEST)
        bgl.glColorMask(bgl.GL_FALSE, bgl.GL_FALSE, bgl.GL_FALSE, bgl.GL_FALSE)
        bgl.glStencilFunc(bgl.GL_ALWAYS, 0, 1)
        bgl.glStencilOp(bgl.GL_KEEP, bgl.GL_KEEP, bgl.GL_INVERT)
        bgl.glStencilMask(1)

        _FILL_SHADER.bind()
        _FILL_SHADER.uniform_block("ub", self.UBO)
        _FILL_SHADER.uniform_float("u_ViewProjectionMatrix", matrix)
        fill_batch.draw(_FILL_SHADER)

        if context.space_data.shading.type in {'MATERIAL', 'RENDERED'}:
            bgl.glStencilFunc(bgl.GL_EQUAL, 0, 1)
        else:
            bgl.glStencilFunc(bgl.GL_EQUAL, 1, 1)
        bgl.glStencilOp(bgl.GL_KEEP, bgl.GL_KEEP, bgl.GL_KEEP)
        bgl.glColorMask(bgl.GL_TRUE, bgl.GL_TRUE, bgl.GL_TRUE, bgl.GL_TRUE)

        # Fill.
        bgl.glEnable(bgl.GL_BLEND)
        stencil_batch.draw(_FILL_SHADER)
        bgl.glDisable(bgl.GL_BLEND)

        # Border.
        if not dashed:
            # Solid border shadow.
            self.UBO_data.u_SegmentColor = shadow_color
            self.update_ubo()

            gpu.state.line_width_set(3)
            _BORDER_SHADER.bind()
            _BORDER_SHADER.uniform_block("ub", self.UBO)
            _BORDER_SHADER.uniform_float("u_ViewProjectionMatrix", matrix)
            border_batch.draw(_BORDER_SHADER)
            gpu.state.line_width_set(1)

            # Solid border.
            self.UBO_data.u_SegmentColor = segment_color
            self.update_ubo()

            bgl.glDisable(bgl.GL_STENCIL_TEST)
            _BORDER_SHADER.uniform_block("ub", self.UBO)
            border_batch.draw(_BORDER_SHADER)

        else:
            # Dashed border.
            bgl.glDisable(bgl.GL_STENCIL_TEST)
            _BORDER_SHADER.bind()
            _BORDER_SHADER.uniform_block("ub", self.UBO)
            _BORDER_SHADER.uniform_float("u_ViewProjectionMatrix", matrix)
            border_batch.draw(_BORDER_SHADER)

    def draw_lasso_shader(self):
        # Create batches.
        vertices = [mathutils.Vector(v) for v in self.lasso_poly]
        vertices.append(mathutils.Vector(self.lasso_poly[0]))

        indices = mathutils.geometry.tessellate_polygon((self.lasso_poly,))
        triangles = [self.lasso_poly[i] for i in itertools.chain.from_iterable(indices)]

        lengths = [0]
        for a, b in zip(vertices[:-1], vertices[1:]):
            lengths.append(lengths[-1] + (a - b).length)

        fill_batch = batch.batch_for_shader(_FILL_SHADER, 'TRIS', {"pos": triangles})
        border_batch = batch.batch_for_shader(_BORDER_SHADER, 'LINE_STRIP', {"pos": vertices, "len": lengths})

        matrix = gpu.matrix.get_projection_matrix()
        if (
            self.select_through
            and not self.invert_select_through
            or not self.select_through
            and self.invert_select_through
        ):
            segment_color = (*self.select_through_color, 1)
            fill_color = (*self.select_through_color, 0.04)
        else:
            segment_color = (*self.default_color, 1)
            fill_color = (*self.default_color, 0.04)
        gap_color = (0.0, 0.0, 0.0, 1.0)
        shadow_color = (0.3, 0.3, 0.3, 1.0)
        dashed = not self.direction == "RIGHT_TO_LEFT"

        # UBO.
        self.UBO_data.u_FillColor = fill_color
        self.UBO_data.u_Dashed = dashed
        self.UBO_data.u_GapColor = gap_color
        self.UBO_data.u_SegmentColor = segment_color
        self.update_ubo()

        # Fill.
        gpu.state.blend_set('ALPHA')
        _FILL_SHADER.bind()
        _FILL_SHADER.uniform_block("ub", self.UBO)
        _FILL_SHADER.uniform_float("u_ViewProjectionMatrix", matrix)
        fill_batch.draw(_FILL_SHADER)
        gpu.state.blend_set('NONE')

        # Border.
        if not dashed:
            # Solid border shadow.
            self.UBO_data.u_SegmentColor = shadow_color
            self.update_ubo()

            gpu.state.line_width_set(3)
            _BORDER_SHADER.bind()
            _BORDER_SHADER.uniform_block("ub", self.UBO)
            _BORDER_SHADER.uniform_float("u_ViewProjectionMatrix", matrix)
            border_batch.draw(_BORDER_SHADER)
            gpu.state.line_width_set(1)

            # Solid border.
            self.UBO_data.u_SegmentColor = segment_color
            self.update_ubo()

            _BORDER_SHADER.uniform_block("ub", self.UBO)
            border_batch.draw(_BORDER_SHADER)

        else:
            # Dashed border.
            _BORDER_SHADER.bind()
            _BORDER_SHADER.uniform_block("ub", self.UBO)
            _BORDER_SHADER.uniform_float("u_ViewProjectionMatrix", matrix)
            border_batch.draw(_BORDER_SHADER)
