import ctypes
from typing import TYPE_CHECKING, Any, Literal, cast

import bpy
import gpu
from gpu_extras import batch

from ...functions.intersections import object_intersect
from ...functions.modals import object_modal

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems


# https://docs.blender.org/api/blender2.8/gpu.html#custom-shader-for-dotted-3d-line
# https://stackoverflow.com/questions/52928678/dashed-line-in-opengl3
class _UBOStruct(ctypes.Structure):
    _pack_ = 4
    _fields_ = [
        ("u_X", ctypes.c_int),
        ("u_Y", ctypes.c_int),
        ("u_Height", ctypes.c_int),
        ("u_Width", ctypes.c_int),
        ("u_SegmentColor", 4 * ctypes.c_float),
        ("u_GapColor", 4 * ctypes.c_float),
        ("u_FillColor", 4 * ctypes.c_float),
        ("u_Dashed", ctypes.c_bool),
        ("_pad", ctypes.c_int * 3),
    ]


_UBO_SOURCE = """
struct Data
{
  int u_X;
  int u_Y;
  int u_Height;
  int u_Width;
  vec4 u_SegmentColor;
  vec4 u_GapColor;
  vec4 u_FillColor;
  bool u_Dashed;
};
"""

# Crosshair shader.
_vert_out = gpu.types.GPUStageInterfaceInfo("my_interface")  # pyright: ignore [reportCallIssue]
_vert_out.smooth('FLOAT', "v_Len")

_shader_info = gpu.types.GPUShaderCreateInfo()
_shader_info.typedef_source(_UBO_SOURCE)
_shader_info.uniform_buf(0, "Data", "ub")
_shader_info.push_constant('MAT4', "u_ViewProjectionMatrix")
_shader_info.vertex_in(0, 'VEC2', "pos")
_shader_info.vertex_in(1, 'INT', "len")
_shader_info.vertex_out(_vert_out)

_shader_info.vertex_source(
    """
    void main()
    {
      v_Len = len;
      gl_Position = u_ViewProjectionMatrix * vec4(pos.x + ub.u_X, pos.y + ub.u_Y, 0.0f, 1.0f);
    }
    """
)
_shader_info.fragment_out(0, 'VEC4', "FragColor")
_shader_info.fragment_source(
    """
    void main()
    {
      float dash_size = 4;
      float gap_size = 4;
      vec4 col = ub.u_SegmentColor;
      if (fract(v_Len/(dash_size + gap_size)) > dash_size/(dash_size + gap_size))
        col = ub.u_GapColor;
      FragColor = col;
    }
    """
)
_crosshair_shader = gpu.shader.create_from_info(_shader_info)
del _vert_out
del _shader_info

# Fill shader.
_shader_info = gpu.types.GPUShaderCreateInfo()
_shader_info.typedef_source(_UBO_SOURCE)
_shader_info.uniform_buf(0, "Data", "ub")
_shader_info.push_constant('MAT4', "u_ViewProjectionMatrix")
_shader_info.vertex_in(0, 'VEC2', "pos")
_shader_info.vertex_source(
    """
    void main()
    {
      gl_Position = u_ViewProjectionMatrix * vec4(
        pos.x * ub.u_Width + ub.u_X, pos.y * ub.u_Height + ub.u_Y, 0.0f, 1.0f);
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
_fill_shader = gpu.shader.create_from_info(_shader_info)
del _shader_info

# Border shader.
_vert_out = gpu.types.GPUStageInterfaceInfo("my_interface")  # pyright: ignore [reportCallIssue]
_vert_out.smooth('FLOAT', "v_Len")

_shader_info = gpu.types.GPUShaderCreateInfo()
_shader_info.typedef_source(_UBO_SOURCE)
_shader_info.uniform_buf(0, "Data", "ub")
_shader_info.push_constant('MAT4', "u_ViewProjectionMatrix")
_shader_info.vertex_in(0, 'VEC2', "pos")
_shader_info.vertex_in(1, 'VEC2', "len")
_shader_info.vertex_out(_vert_out)
_shader_info.vertex_source(
    """
    void main()
    {
      v_Len = len.x * ub.u_Width + len.y * ub.u_Height;
      gl_Position = u_ViewProjectionMatrix * vec4(
        pos.x * ub.u_Width + ub.u_X, pos.y * ub.u_Height + ub.u_Y, 0.0f, 1.0f);
    }
    """
)
_shader_info.fragment_out(0, 'VEC4', "FragColor")
_shader_info.fragment_source(
    """
    void main()
    {
      float dash_size = 4;
      float gap_size = 4;
      vec4 col = ub.u_SegmentColor;
      if (ub.u_Dashed)
        if (fract(v_Len/(dash_size + gap_size)) > dash_size/(dash_size + gap_size))
          col = ub.u_GapColor;
        FragColor = col;
    }
    """
)
_border_shader = gpu.shader.create_from_info(_shader_info)
del _vert_out
del _shader_info


class OBJECT_OT_select_box_xray(bpy.types.Operator):
    """Select items using box selection with x-ray"""

    bl_idname = "object.select_box_xray"
    bl_label = "Box Select X-Ray"

    if TYPE_CHECKING:
        mode: Literal['SET', 'ADD', 'SUB', 'XOR', 'AND']
        alt_mode: Literal['SET', 'ADD', 'SUB']
        alt_mode_toggle_key: Literal['CTRL', 'ALT', 'SHIFT', 'OSKEY']
        wait_for_input: bool
        override_global_props: bool
        show_xray: bool
        xray_toggle_key: Literal['CTRL', 'ALT', 'SHIFT', 'OSKEY', 'DISABLED']
        xray_toggle_type: Literal['HOLD', 'PRESS']
        hide_gizmo: bool
        show_crosshair: bool
        behavior: Literal['ORIGIN', 'CONTAIN', 'OVERLAP', 'DIRECTIONAL', 'DIRECTIONAL_REVERSED']
    else:
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
                ('OSKEY', "CMD", ""),
            ],
            default='SHIFT',
            options={'SKIP_SAVE'},
        )
        wait_for_input: bpy.props.BoolProperty(
            name="Wait for input",
            description=(
                "Wait for mouse input or initialize box selection immediately "
                "(enable when assigning the operator to a keyboard key)"
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
                ('OSKEY', "CMD", ""),
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
        show_crosshair: bpy.props.BoolProperty(
            name="Show Crosshair",
            description="Show crosshair when wait_for_input is enabled",
            default=True,
            options={'SKIP_SAVE'},
        )
        behavior: bpy.props.EnumProperty(
            name="Selection Behavior",
            description="Selection behavior",
            items=[
                ('ORIGIN', "Origin", "Select objects by origins", 'DOT', 1),
                ('CONTAIN', "Contain", "Select only the objects fully contained in box", 'STICKY_UVS_LOC', 2),
                ('OVERLAP', "Overlap (Default)", "Select objects overlapping box", 'SELECT_SUBTRACT', 3),
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
            default='OVERLAP',
        )

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.area.type == 'VIEW_3D' and context.mode == 'OBJECT'

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if bpy.app.version >= (4, 4, 0):
            super().__init__(*args, **kwargs)

        self.stage: Literal['CUSTOM_WAIT_FOR_INPUT', 'CUSTOM_SELECTION', 'INBUILT_OP'] = 'CUSTOM_WAIT_FOR_INPUT'
        self.curr_mode: Literal['SET', 'ADD', 'SUB', 'XOR', 'AND'] = self.mode
        self.curr_behavior: Literal['ORIGIN', 'CONTAIN', 'OVERLAP', 'DIRECTIONAL', 'DIRECTIONAL_REVERSED'] = (
            self.behavior
        )

        self.start_mouse_region_x: int = 0
        self.start_mouse_region_y: int = 0
        self.last_mouse_region_x: int = 0
        self.last_mouse_region_y: int = 0

        self.init_overlays: dict[str, Any] = dict()

        self.override_wait_for_input: bool = False
        self.override_selection: bool = False
        self.override_intersect_tests: bool = False

        self.xray_toggle_key_list: set[
            Literal[
                'LEFT_CTRL', 'RIGHT_CTRL', 'LEFT_ALT', 'RIGHT_ALT', 'LEFT_SHIFT', 'RIGHT_SHIFT', 'OSKEY', 'DISABLED'
            ]
        ] = object_modal.get_xray_toggle_key_list()

        self.handler: Any | None = None
        self.crosshair_batch: gpu.types.GPUBatch | None = None
        self.border_batch: gpu.types.GPUBatch | None = None
        self.fill_batch: gpu.types.GPUBatch | None = None
        self.UBO_data: _UBOStruct = _UBOStruct()
        self.UBO: gpu.types.GPUUniformBuf = gpu.types.GPUUniformBuf(
            gpu.types.Buffer("UBYTE", ctypes.sizeof(self.UBO_data), self.UBO_data)  # pyright: ignore [reportCallIssue]
        )

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set["OperatorReturnItems"]:
        object_modal.set_properties(self, tool='BOX')

        self.override_intersect_tests = self.behavior != 'OVERLAP'

        self.override_selection = (
            self.xray_toggle_key != 'DISABLED'
            or self.alt_mode_toggle_key != 'SHIFT'
            or self.alt_mode != 'SUB'
            or self.override_intersect_tests
        )

        self.override_wait_for_input = not self.show_crosshair or self.override_selection

        self.init_overlays = object_modal.gather_overlays(context)  # save initial x-ray overlay states

        # Sync operator properties with current shading.
        object_modal.sync_properties(self, context)

        # Enable x-ray overlays.
        object_modal.toggle_overlays(self, context)

        self.update_directional_behavior()

        context.window_manager.modal_handler_add(self)

        # Jump to.
        if self.wait_for_input and self.override_wait_for_input:
            self.begin_custom_wait_for_input_stage(context, event)
        elif self.override_selection:
            self.begin_custom_selection_stage(context, event)
        else:
            self.invoke_inbuilt_box_select()

        return {'RUNNING_MODAL'}

    def modal(self, context: bpy.types.Context, event: bpy.types.Event) -> set["OperatorReturnItems"]:
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
                    object_modal.toggle_overlays(self, context)

            # Finish stage.
            if event.value == 'PRESS' and event.type in {'LEFTMOUSE', 'MIDDLEMOUSE'}:
                self.finish_custom_wait_for_input_stage(context)
                object_modal.toggle_alt_mode(self, event)
                if self.override_selection:
                    self.begin_custom_selection_stage(context, event)
                else:
                    self.invoke_inbuilt_box_select()

        if self.stage == 'CUSTOM_SELECTION':
            # Update shader.
            if event.type == 'MOUSEMOVE':
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
                    object_modal.toggle_overlays(self, context)

            # Finish stage.
            if event.value == 'RELEASE' and event.type in {'LEFTMOUSE', 'MIDDLEMOUSE', 'RIGHTMOUSE'}:
                self.finish_custom_selection_stage(context)
                if self.override_intersect_tests:
                    self.begin_custom_intersect_tests(context)
                    self.finish_modal(context)
                    bpy.ops.ed.undo_push(message="Box Select")
                    return {'FINISHED'}

                self.exec_inbuilt_box_select()
                self.finish_modal(context)
                bpy.ops.ed.undo_push(message="Box Select")
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

    def begin_custom_wait_for_input_stage(self, context: bpy.types.Context, event: bpy.types.Event) -> None:
        """Set cursor and status text, draw wait_for_input shader."""
        self.stage = 'CUSTOM_WAIT_FOR_INPUT'
        context.window.cursor_modal_set('CROSSHAIR')
        enum_items = cast(bpy.types.EnumProperty, self.properties.bl_rna.properties["mode"]).enum_items
        curr_mode_name = enum_items[self.curr_mode].name
        enum_items = cast(bpy.types.EnumProperty, self.properties.bl_rna.properties["alt_mode"]).enum_items
        alt_mode_name = enum_items[self.alt_mode].name

        status_text = f"RMB, ESC: Cancel  |  LMB: {curr_mode_name}  |  {self.alt_mode_toggle_key}+LMB: {alt_mode_name}"
        if self.xray_toggle_key != 'DISABLED':
            status_text += f"  |  {self.xray_toggle_key}: Toggle X-Ray"
        context.workspace.status_text_set(text=status_text)

        if self.show_crosshair:
            self.build_crosshair_shader(context)
            self.handler = context.space_data.draw_handler_add(self.draw_crosshair_shader, (), 'WINDOW', 'POST_PIXEL')  # pyright: ignore [reportArgumentType]
            self.update_shader_position(context, event)

    def finish_custom_wait_for_input_stage(self, context: bpy.types.Context) -> None:
        """Restore cursor and status text, remove wait_for_input shader."""
        self.wait_for_input = False
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(text=None)
        if self.show_crosshair:
            context.space_data.draw_handler_remove(self.handler, 'WINDOW')
            context.region.tag_redraw()

    def begin_custom_selection_stage(self, context: bpy.types.Context, event: bpy.types.Event) -> None:
        self.stage = 'CUSTOM_SELECTION'
        context.window.cursor_modal_set('CROSSHAIR')

        status_text = "RMB, ESC: Cancel"
        if self.xray_toggle_key != 'DISABLED':
            status_text += f"  |  {self.xray_toggle_key}: Toggle X-Ray"
        context.workspace.status_text_set(text=status_text)

        self.start_mouse_region_x = event.mouse_region_x
        self.start_mouse_region_y = event.mouse_region_y
        self.build_box_shader()
        self.handler = context.space_data.draw_handler_add(self.draw_box_shader, (), 'WINDOW', 'POST_PIXEL')  # pyright: ignore [reportArgumentType]
        self.update_shader_position(context, event)

    def finish_custom_selection_stage(self, context: bpy.types.Context) -> None:
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(text=None)
        context.space_data.draw_handler_remove(self.handler, 'WINDOW')
        context.region.tag_redraw()

    def invoke_inbuilt_box_select(self) -> None:
        self.stage = 'INBUILT_OP'
        bpy.ops.view3d.select_box('INVOKE_DEFAULT', mode=self.curr_mode, wait_for_input=self.wait_for_input)

    def exec_inbuilt_box_select(self) -> None:
        # Get selection rectangle coordinates.
        xmin = min(self.start_mouse_region_x, self.last_mouse_region_x)
        xmax = max(self.start_mouse_region_x, self.last_mouse_region_x)
        ymin = min(self.start_mouse_region_y, self.last_mouse_region_y)
        ymax = max(self.start_mouse_region_y, self.last_mouse_region_y)
        bpy.ops.view3d.select_box(mode=self.curr_mode, wait_for_input=False, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)

    def begin_custom_intersect_tests(self, context: bpy.types.Context) -> None:
        # Get selection rectangle coordinates.
        xmin = min(self.start_mouse_region_x, self.last_mouse_region_x)
        xmax = max(self.start_mouse_region_x, self.last_mouse_region_x)
        ymin = min(self.start_mouse_region_y, self.last_mouse_region_y)
        ymax = max(self.start_mouse_region_y, self.last_mouse_region_y)
        assert self.curr_behavior == 'ORIGIN' or self.curr_behavior == 'CONTAIN'
        object_intersect.select_objects_in_box(
            context, mode=self.curr_mode, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, behavior=self.curr_behavior
        )

    def finish_modal(self, context: bpy.types.Context) -> None:
        object_modal.restore_overlays(self, context)

    def update_directional_behavior(self) -> None:
        if self.behavior in {'DIRECTIONAL', 'DIRECTIONAL_REVERSED'}:
            right_to_left = self.last_mouse_region_x - self.start_mouse_region_x > 0
            if (
                right_to_left
                and self.behavior == 'DIRECTIONAL'
                or not right_to_left
                and self.behavior == 'DIRECTIONAL_REVERSED'
            ):
                self.curr_behavior = 'OVERLAP'
                self.override_intersect_tests = False
            else:
                self.curr_behavior = 'CONTAIN'
                self.override_intersect_tests = True

    def update_ubo(self) -> None:
        self.UBO.update(gpu.types.Buffer('UBYTE', ctypes.sizeof(self.UBO_data), self.UBO_data))  # pyright: ignore [reportCallIssue]

    def update_shader_position(self, context: bpy.types.Context, event: bpy.types.Event) -> None:
        self.last_mouse_region_x = event.mouse_region_x
        self.last_mouse_region_y = event.mouse_region_y
        context.region.tag_redraw()

    def build_crosshair_shader(self, context: bpy.types.Context) -> None:
        width = context.region.width
        height = context.region.height
        vertices = ((0, -height), (0, height), (-width, 0), (width, 0))
        lengths = (0, 2 * height, 0, 2 * width)
        self.crosshair_batch = batch.batch_for_shader(_crosshair_shader, 'LINES', {"pos": vertices, "len": lengths})

    def draw_crosshair_shader(self) -> None:
        matrix = gpu.matrix.get_projection_matrix()
        segment_color = (1.0, 1.0, 1.0, 1.0)
        gap_color = (0.2, 0.2, 0.2, 1.0)

        # UBO.
        self.UBO_data.u_X = self.last_mouse_region_x
        self.UBO_data.u_Y = self.last_mouse_region_y
        self.UBO_data.u_SegmentColor = segment_color
        self.UBO_data.u_GapColor = gap_color
        self.update_ubo()

        # Crosshair.
        assert isinstance(self.crosshair_batch, gpu.types.GPUBatch)
        _crosshair_shader.bind()
        _border_shader.uniform_block("ub", self.UBO)
        _crosshair_shader.uniform_float("u_ViewProjectionMatrix", matrix)  # pyright: ignore[reportArgumentType]
        self.crosshair_batch.draw(_crosshair_shader)

    def build_box_shader(self) -> None:
        vertices = ((0, 0), (1, 0), (1, 1), (0, 1), (0, 0))
        lengths = ((0, 0), (1, 0), (1, 1), (2, 1), (2, 2))
        self.border_batch = batch.batch_for_shader(_border_shader, 'LINE_STRIP', {"pos": vertices, "len": lengths})

        vertices = ((0, 0), (1, 0), (0, 1), (1, 1))
        self.fill_batch = batch.batch_for_shader(_fill_shader, 'TRI_STRIP', {"pos": vertices})

    def draw_box_shader(self) -> None:
        matrix = gpu.matrix.get_projection_matrix()
        segment_color = (1.0, 1.0, 1.0, 1.0)
        gap_color = (0.2, 0.2, 0.2, 1.0)
        shadow_color = (0.3, 0.3, 0.3, 1.0)
        fill_color = (1.0, 1.0, 1.0, 0.04)
        width = self.last_mouse_region_x - self.start_mouse_region_x
        height = self.last_mouse_region_y - self.start_mouse_region_y
        dashed = 0 if self.curr_behavior == 'CONTAIN' else 1

        # UBO.
        self.UBO_data.u_X = self.start_mouse_region_x
        self.UBO_data.u_Y = self.start_mouse_region_y
        self.UBO_data.u_Height = height
        self.UBO_data.u_Width = width
        self.UBO_data.u_Dashed = dashed
        self.UBO_data.u_SegmentColor = segment_color
        self.UBO_data.u_GapColor = gap_color
        self.UBO_data.u_FillColor = fill_color
        self.update_ubo()

        # Fill.
        assert isinstance(self.fill_batch, gpu.types.GPUBatch)
        gpu.state.blend_set('ALPHA')
        _fill_shader.bind()
        _fill_shader.uniform_block("ub", self.UBO)
        _fill_shader.uniform_float("u_ViewProjectionMatrix", matrix)  # pyright: ignore[reportArgumentType]
        self.fill_batch.draw(_fill_shader)
        gpu.state.blend_set('NONE')

        # Border.
        assert isinstance(self.border_batch, gpu.types.GPUBatch)
        _border_shader.bind()
        _border_shader.uniform_block("ub", self.UBO)
        _border_shader.uniform_float("u_ViewProjectionMatrix", matrix)  # pyright: ignore[reportArgumentType]
        self.border_batch.draw(_border_shader)

        # Solid border shadow.
        if not dashed:
            self.UBO_data.u_X = self.start_mouse_region_x + 1
            self.UBO_data.u_Y = self.start_mouse_region_y - 1
            self.UBO_data.u_SegmentColor = shadow_color
            self.update_ubo()

            _border_shader.uniform_block("ub", self.UBO)
            self.border_batch.draw(_border_shader)
