import ctypes
from typing import TYPE_CHECKING, Any, Literal, cast

import bpy
import gpu
import mathutils
import numpy as np
from gpu_extras import batch

from ...functions.intersections import object_intersect
from ...functions.modals import object_modal

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems


class _UBOStruct(ctypes.Structure):
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


_UBO_SOURCE = """
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
      gl_Position = u_ViewProjectionMatrix * vec4(pos.x + ub.u_X, pos.y + ub.u_Y, 0.0f, 1.0f);
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
_shader_info.vertex_in(1, 'FLOAT', "len")
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
      float dash_size = 2;
      float gap_size = 2;
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


class OBJECT_OT_select_circle_xray(bpy.types.Operator):
    """Select items using circle selection with x-ray"""

    bl_idname = "object.select_circle_xray"
    bl_label = "Circle Select X-Ray"

    if TYPE_CHECKING:
        mode: Literal['SET', 'ADD', 'SUB']
        alt_mode: Literal['SET', 'ADD', 'SUB']
        alt_mode_toggle_key: Literal['CTRL', 'ALT', 'SHIFT', 'OSKEY']
        radius: int
        wait_for_input: bool
        override_global_props: bool
        show_xray: bool
        xray_toggle_key: Literal['CTRL', 'ALT', 'SHIFT', 'OSKEY', 'DISABLED']
        xray_toggle_type: Literal['HOLD', 'PRESS']
        hide_gizmo: bool
        behavior: Literal['ORIGIN', 'CONTAIN', 'OVERLAP']
    else:
        mode: bpy.props.EnumProperty(
            name="Mode",
            items=[
                ('SET', "Set", "Set a new selection", 'SELECT_SET', 1),
                ('ADD', "Extend", "Extend existing selection", 'SELECT_EXTEND', 2),
                ('SUB', "Subtract", "Subtract existing selection", 'SELECT_SUBTRACT', 3),
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
        radius: bpy.props.IntProperty(
            name="Radius",
            description="Radius",
            default=25,
            min=1,
        )
        wait_for_input: bpy.props.BoolProperty(
            name="Wait for input",
            description=(
                "Wait for mouse input or initialize box selection immediately "
                "(enable when assigning the operator to a keyboard key)"
            ),
            default=True,
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
        behavior: bpy.props.EnumProperty(
            name="Selection Behavior",
            description="Selection behavior",
            items=[
                ('ORIGIN', "Origin (Default)", "Select objects by origins", 'DOT', 1),
                ('CONTAIN', "Contain", "Select only the objects fully contained in circle", 'STICKY_UVS_LOC', 2),
                ('OVERLAP', "Overlap", "Select objects overlapping circle", 'SELECT_SUBTRACT', 3),
            ],
            default='ORIGIN',
        )

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.area.type == 'VIEW_3D' and context.mode == 'OBJECT'

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if bpy.app.version >= (4, 4, 0):
            super().__init__(*args, **kwargs)

        self.stage: Literal['CUSTOM_WAIT_FOR_INPUT', 'CUSTOM_SELECTION', 'INBUILT_OP'] = 'CUSTOM_WAIT_FOR_INPUT'
        self.curr_mode: Literal['SET', 'ADD', 'SUB'] = self.mode

        self.last_mouse_region_x: int = 0
        self.last_mouse_region_y: int = 0

        self.init_overlays: dict[str, Any] = dict()

        self.override_modal: bool = False
        self.override_intersect_tests: bool = False

        self.xray_toggle_key_list: set[
            Literal[
                'LEFT_CTRL', 'RIGHT_CTRL', 'LEFT_ALT', 'RIGHT_ALT', 'LEFT_SHIFT', 'RIGHT_SHIFT', 'OSKEY', 'DISABLED'
            ]
        ] = object_modal.get_xray_toggle_key_list()

        self.handler: Any | None = None
        self.border_batch: gpu.types.GPUBatch | None = None
        self.shadow_batch: gpu.types.GPUBatch | None = None
        self.fill_batch: gpu.types.GPUBatch | None = None
        self.UBO_data: _UBOStruct = _UBOStruct()
        self.UBO: gpu.types.GPUUniformBuf = gpu.types.GPUUniformBuf(
            gpu.types.Buffer('UBYTE', ctypes.sizeof(self.UBO_data), self.UBO_data)  # pyright: ignore [reportCallIssue]
        )

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set["OperatorReturnItems"]:
        object_modal.set_properties(self, tool='CIRCLE')

        self.override_intersect_tests = self.behavior != 'ORIGIN'

        self.override_modal = (
            self.xray_toggle_key != 'DISABLED'
            or self.alt_mode_toggle_key != 'SHIFT'
            or self.alt_mode != 'SUB'
            or self.override_intersect_tests
        )

        self.init_overlays = object_modal.gather_overlays(context)  # save initial x-ray overlay states

        # Sync operator properties with current shading.
        object_modal.sync_properties(self, context)

        # Enable x-ray overlays.
        object_modal.toggle_overlays(self, context)

        context.window_manager.modal_handler_add(self)

        # Jump to.
        if self.override_modal:
            self.show_custom_ui(context, event)
            if self.wait_for_input:
                self.stage = 'CUSTOM_WAIT_FOR_INPUT'
            else:
                self.stage = 'CUSTOM_SELECTION'
        else:
            self.invoke_inbuilt_circle_select()
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

            # Change radius.
            if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'NUMPAD_MINUS', 'NUMPAD_PLUS'}:
                self.update_radius(context, event)

            # Finish stage.
            if event.value == 'PRESS' and event.type in {'LEFTMOUSE', 'MIDDLEMOUSE'}:
                self.stage = 'CUSTOM_SELECTION'
                object_modal.toggle_alt_mode(self, event)
                if self.override_intersect_tests:
                    self.begin_custom_intersect_tests(context)
                else:
                    self.exec_inbuilt_circle_select()

        if self.stage == 'CUSTOM_SELECTION':
            # Update shader.
            if event.type == 'MOUSEMOVE':
                self.update_shader_position(context, event)
                if self.override_intersect_tests:
                    self.begin_custom_intersect_tests(context)
                else:
                    self.exec_inbuilt_circle_select()

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

            # Change radius.
            if event.type in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'NUMPAD_MINUS', 'NUMPAD_PLUS'}:
                self.update_radius(context, event)

            # Finish stage.
            if event.value == 'RELEASE' and event.type in {'LEFTMOUSE', 'MIDDLEMOUSE'}:
                if self.wait_for_input:
                    self.stage = 'CUSTOM_WAIT_FOR_INPUT'
                else:
                    self.remove_custom_ui(context)
                    self.finish_modal(context)
                    bpy.ops.ed.undo_push(message="Circle Select")
                    return {'FINISHED'}

        # Finish modal.
        if event.value == 'PRESS' and event.type == 'RET':
            if self.stage in {'CUSTOM_WAIT_FOR_INPUT', 'CUSTOM_SELECTION'}:
                self.remove_custom_ui(context)
            self.finish_modal(context)
            return {'FINISHED'}

        if self.stage == 'INBUILT_OP':
            # Inbuilt op was finished, now finish modal.
            if event.type == 'MOUSEMOVE':
                self.radius = context.window_manager.operator_properties_last("view3d.select_circle").radius  # pyright: ignore [reportAttributeAccessIssue]
                self.finish_modal(context)
                return {'FINISHED'}

        # Cancel modal.
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            if self.stage in {'CUSTOM_WAIT_FOR_INPUT', 'CUSTOM_SELECTION'}:
                self.remove_custom_ui(context)
                bpy.ops.ed.undo_push(message="Circle Select")
            self.finish_modal(context)
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def show_custom_ui(self, context: bpy.types.Context, event: bpy.types.Event) -> None:
        """Set cursor and status text, draw shader."""
        context.window.cursor_modal_set('CROSSHAIR')
        enum_items = cast(bpy.types.EnumProperty, self.properties.bl_rna.properties["mode"]).enum_items
        curr_mode_name = enum_items[self.curr_mode].name
        enum_items = cast(bpy.types.EnumProperty, self.properties.bl_rna.properties["alt_mode"]).enum_items
        alt_mode_name = enum_items[self.alt_mode].name

        if self.wait_for_input:
            status_text = (
                "RMB, ESC: Cancel  |  ENTER: Confirm  |  WhDown/Pad+: Add  |  WhUp/Pad-: Subtract  |  "
                f"LMB: {curr_mode_name}  |  {self.alt_mode_toggle_key}+LMB: {alt_mode_name}"
            )
        else:
            status_text = "RMB, ESC: Cancel  |  WhDown/Pad+: Add  |  WhUp/Pad-: Subtract"
        if self.xray_toggle_key != 'DISABLED':
            status_text += f"  |  {self.xray_toggle_key}: Toggle X-Ray"
        context.workspace.status_text_set(text=status_text)

        self.build_circle_shader()
        self.handler = context.space_data.draw_handler_add(self.draw_circle_shader, (), 'WINDOW', 'POST_PIXEL')  # pyright: ignore [reportArgumentType]
        self.update_shader_position(context, event)

    def update_radius(self, context: bpy.types.Context, event: bpy.types.Event) -> None:
        if event.type in {'WHEELUPMOUSE', 'NUMPAD_MINUS'}:
            self.radius -= 10
        elif event.type in {'WHEELDOWNMOUSE', 'NUMPAD_PLUS'}:
            self.radius += 10
        self.build_circle_shader()
        context.region.tag_redraw()

    def remove_custom_ui(self, context: bpy.types.Context) -> None:
        """Restore cursor and status text, remove shader."""
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(text=None)
        context.space_data.draw_handler_remove(self.handler, 'WINDOW')
        context.region.tag_redraw()

    def invoke_inbuilt_circle_select(self) -> None:
        self.stage = 'INBUILT_OP'
        bpy.ops.view3d.select_circle(
            'INVOKE_DEFAULT', mode=self.curr_mode, wait_for_input=self.wait_for_input, radius=self.radius
        )

    def exec_inbuilt_circle_select(self) -> None:
        bpy.ops.view3d.select_circle(
            x=self.last_mouse_region_x,
            y=self.last_mouse_region_y,
            mode=self.curr_mode,
            wait_for_input=False,
            radius=self.radius,
        )
        if self.curr_mode == 'SET':
            self.curr_mode = 'ADD'

    def begin_custom_intersect_tests(self, context: bpy.types.Context) -> None:
        center = (self.last_mouse_region_x, self.last_mouse_region_y)
        assert self.behavior == 'CONTAIN' or self.behavior == 'OVERLAP'
        object_intersect.select_objects_in_circle(
            context, mode=self.curr_mode, center=center, radius=self.radius, behavior=self.behavior
        )
        if self.curr_mode == 'SET':
            self.curr_mode = 'ADD'

    def finish_modal(self, context: bpy.types.Context) -> None:
        object_modal.restore_overlays(self, context)
        context.window_manager.operator_properties_last("object.select_circle_xray").radius = self.radius  # pyright: ignore [reportAttributeAccessIssue]

    def update_ubo(self) -> None:
        self.UBO.update(gpu.types.Buffer("UBYTE", ctypes.sizeof(self.UBO_data), self.UBO_data))  # pyright: ignore [reportCallIssue]

    def update_shader_position(self, context: bpy.types.Context, event: bpy.types.Event) -> None:
        self.last_mouse_region_x = event.mouse_region_x
        self.last_mouse_region_y = event.mouse_region_y
        context.region.tag_redraw()

    @staticmethod
    def get_circle_verts_orig(radius: int) -> list[tuple[float, float]]:
        sides = 31
        # https://stackoverflow.com/questions/17258546/opengl-creating-a-circle-change-radius
        counts = np.arange(1, sides + 1, dtype="f")
        angles = np.multiply(counts, 2 * np.pi / sides)
        vert_x = np.multiply(np.sin(angles), radius)
        vert_y = np.multiply(np.cos(angles), radius)
        vert_co = np.vstack((vert_x, vert_y)).T
        vert_co.shape = (sides, 2)
        vertices = vert_co.tolist()
        vertices.append(vertices[0])
        return [*map(tuple, vertices)]

    def build_circle_shader(self) -> None:
        vertices = self.get_circle_verts_orig(self.radius)
        segment = (mathutils.Vector(vertices[0]) - mathutils.Vector(vertices[1])).length
        lengths = [segment * i for i in range(32)]
        self.border_batch = batch.batch_for_shader(_border_shader, 'LINE_STRIP', {"pos": vertices, "len": lengths})

        shadow_vertices = self.get_circle_verts_orig(self.radius - 1)
        self.shadow_batch = batch.batch_for_shader(
            _border_shader, 'LINE_STRIP', {"pos": shadow_vertices, "len": lengths}
        )

        vertices.append(vertices[0])  # ending triangle
        vertices.insert(0, (0, 0))  # starting vert of triangle fan
        self.fill_batch = batch.batch_for_shader(_fill_shader, 'TRI_FAN', {"pos": vertices})

    def draw_circle_shader(self) -> None:
        matrix = gpu.matrix.get_projection_matrix()
        segment_color = (1.0, 1.0, 1.0, 1.0)
        gap_color = (0.2, 0.2, 0.2, 1.0)
        shadow_color = (0.3, 0.3, 0.3, 1.0)
        fill_color = (1.0, 1.0, 1.0, 0.04)
        dashed = not self.behavior == 'CONTAIN'

        # UBO.
        self.UBO_data.u_X = self.last_mouse_region_x
        self.UBO_data.u_Y = self.last_mouse_region_y
        self.UBO_data.u_SegmentColor = segment_color
        self.UBO_data.u_GapColor = gap_color
        self.UBO_data.u_FillColor = fill_color
        self.update_ubo()

        # Fill.
        assert isinstance(self.fill_batch, gpu.types.GPUBatch)
        gpu.state.blend_set("ALPHA")
        _fill_shader.bind()
        _fill_shader.uniform_block("ub", self.UBO)
        _fill_shader.uniform_float("u_ViewProjectionMatrix", matrix)  # pyright: ignore[reportArgumentType]
        self.fill_batch.draw(_fill_shader)
        gpu.state.blend_set("NONE")

        # Border.
        if not dashed:
            # Solid border shadow.
            assert isinstance(self.shadow_batch, gpu.types.GPUBatch)
            self.UBO_data.u_SegmentColor = shadow_color
            self.update_ubo()

            _border_shader.bind()
            _border_shader.uniform_block("ub", self.UBO)
            _border_shader.uniform_float("u_ViewProjectionMatrix", matrix)  # pyright: ignore[reportArgumentType]
            self.shadow_batch.draw(_border_shader)

            # Solid border.
            assert isinstance(self.border_batch, gpu.types.GPUBatch)
            self.UBO_data.u_SegmentColor = segment_color
            self.update_ubo()

            _border_shader.uniform_block("ub", self.UBO)
            self.border_batch.draw(_border_shader)

        else:
            # Dashed border.
            assert isinstance(self.border_batch, gpu.types.GPUBatch)
            _border_shader.bind()
            _border_shader.uniform_block("ub", self.UBO)
            _border_shader.uniform_float("u_ViewProjectionMatrix", matrix)  # pyright: ignore[reportArgumentType]
            self.border_batch.draw(_border_shader)
