import ctypes

import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from ...addon_info import get_preferences
from ...functions.intersections.mesh_intersect import select_mesh_elements
from ...functions.modals.mesh_modal import (
    gather_modifiers,
    gather_overlays,
    get_select_through_toggle_key_list,
    initialize_shading_from_properties,
    restore_modifiers,
    restore_overlays,
    set_modifiers_from_properties,
    set_properties_from_direction,
    set_properties_from_preferences,
    set_shading_from_properties,
    toggle_alt_mode,
    update_shader_color,
)


# https://docs.blender.org/api/blender2.8/gpu.html#custom-shader-for-dotted-3d-line
# https://stackoverflow.com/questions/52928678/dashed-line-in-opengl3
# noinspection PyTypeChecker
class _UBO_struct(ctypes.Structure):
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


UBO_source = """
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
vert_out = gpu.types.GPUStageInterfaceInfo("my_interface")  # noqa
vert_out.smooth('FLOAT', "v_Len")

shader_info = gpu.types.GPUShaderCreateInfo()
shader_info.typedef_source(UBO_source)
shader_info.uniform_buf(0, "Data", "ub")
shader_info.push_constant('MAT4', "u_ViewProjectionMatrix")
shader_info.vertex_in(0, 'VEC2', "pos")
shader_info.vertex_in(1, 'INT', "len")
shader_info.vertex_out(vert_out)

shader_info.vertex_source(
    """
    void main()
    {
      v_Len = len;
      gl_Position = u_ViewProjectionMatrix * vec4(pos.x + ub.u_X, pos.y + ub.u_Y, 0.0f, 1.0f);
    }
    """
)
shader_info.fragment_out(0, 'VEC4', "FragColor")
shader_info.fragment_source(
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
CROSSHAIR_SHADER = gpu.shader.create_from_info(shader_info)
del vert_out
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
      gl_Position = u_ViewProjectionMatrix * vec4(
        pos.x * ub.u_Width + ub.u_X, pos.y * ub.u_Height + ub.u_Y, 0.0f, 1.0f);
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
shader_info.vertex_in(1, 'VEC2', "len")
shader_info.vertex_out(vert_out)
shader_info.vertex_source(
    """
    void main()
    {
      v_Len = len.x * ub.u_Width + len.y * ub.u_Height;
      gl_Position = u_ViewProjectionMatrix * vec4(
        pos.x * ub.u_Width + ub.u_X, pos.y * ub.u_Height + ub.u_Y, 0.0f, 1.0f);
    }
    """
)
shader_info.fragment_out(0, 'VEC4', "FragColor")
shader_info.fragment_source(
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
BORDER_SHADER = gpu.shader.create_from_info(shader_info)
del vert_out
del shader_info


# noinspection PyTypeChecker
class MESH_OT_select_box_xray(bpy.types.Operator):
    """Select items using box selection with x-ray"""

    bl_idname = "mesh.select_box_xray"
    bl_label = "Box Select X-Ray"
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
            "Wait for mouse input or initialize box selection immediately (usually you "
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
            "Additionally select edges that are partially inside the selection box, "
            "not just the ones completely inside the selection box. Works only in "
            "select through mode"
        ),
        default=False,
        options={'SKIP_SAVE'},
    )
    select_all_faces: bpy.props.BoolProperty(
        name="Select All Faces",
        description=(
            "Additionally select faces that are partially inside the selection box, "
            "not just the ones with centers inside the selection box. Works only in "
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
    show_crosshair: bpy.props.BoolProperty(
        name="Show Crosshair",
        description="Show crosshair when wait_for_input is enabled",
        default=True,
        options={'SKIP_SAVE'},
    )

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode == 'EDIT_MESH'

    def __init__(self, *args, **kwargs):
        if bpy.app.version >= (4, 4, 0):
            super().__init__(*args, **kwargs)

        self.stage = None
        self.curr_mode = self.mode
        self.directional = get_preferences().me_directional_box and not self.override_global_props
        self.direction = None

        self.start_mouse_region_x = 0
        self.start_mouse_region_y = 0
        self.last_mouse_region_x = 0
        self.last_mouse_region_y = 0

        self.init_mods = None
        self.init_overlays = None

        self.override_wait_for_input = False
        self.override_selection = False
        self.override_intersect_tests = False

        self.invert_select_through = False
        self.select_through_toggle_key_list = get_select_through_toggle_key_list()

        self.handler = None
        self.crosshair_batch = None
        self.border_batch = None
        self.fill_batch = None
        self.UBO_data = _UBO_struct()
        self.UBO = gpu.types.GPUUniformBuf(
            gpu.types.Buffer("UBYTE", ctypes.sizeof(self.UBO_data), self.UBO_data)  # noqa
        )

    def invoke(self, context, event):
        # Set operator properties from addon preferences.
        set_properties_from_preferences(self, tool='BOX')

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

        self.override_wait_for_input = not self.show_crosshair or self.override_selection

        self.init_mods = gather_modifiers(self, context)  # save initial modifier states
        self.init_overlays = gather_overlays(context)  # save initial x-ray overlay states

        # Set x-ray overlays and modifiers.
        initialize_shading_from_properties(self, context)
        set_modifiers_from_properties(self)

        context.window_manager.modal_handler_add(self)

        # Jump to.
        if self.wait_for_input and self.override_wait_for_input:
            self.begin_custom_wait_for_input_stage(context, event)
        elif self.override_selection:
            self.begin_custom_selection_stage(context, event)
        else:
            self.invoke_inbuilt_box_select()

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
                    set_shading_from_properties(self, context)
                    update_shader_color(self, context)

            # Finish stage.
            if event.value == 'PRESS' and event.type in {'LEFTMOUSE', 'MIDDLEMOUSE'}:
                self.finish_custom_wait_for_input_stage(context)
                toggle_alt_mode(self, event)
                if self.override_selection:
                    self.begin_custom_selection_stage(context, event)
                else:
                    self.invoke_inbuilt_box_select()

        if self.stage == 'CUSTOM_SELECTION':
            # Update shader.
            if event.type == 'MOUSEMOVE':
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
                    set_shading_from_properties(self, context)
                    update_shader_color(self, context)

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

        if self.show_crosshair:
            self.build_crosshair_shader(context)
            self.handler = context.space_data.draw_handler_add(self.draw_crosshair_shader, (), 'WINDOW', 'POST_PIXEL')
            self.update_shader_position(context, event)

    def finish_custom_wait_for_input_stage(self, context):
        """Restore status text, remove wait_for_input shader."""
        self.wait_for_input = False
        context.workspace.status_text_set(text=None)
        if self.show_crosshair:
            context.space_data.draw_handler_remove(self.handler, 'WINDOW')
            context.region.tag_redraw()

    def begin_custom_selection_stage(self, context, event):
        self.stage = 'CUSTOM_SELECTION'

        status_text = "RMB, ESC: Cancel"
        if self.select_through_toggle_key != 'DISABLED':
            status_text += f"  |  {self.select_through_toggle_key}: Toggle Select Through"
        context.workspace.status_text_set(text=status_text)

        self.start_mouse_region_x = event.mouse_region_x
        self.start_mouse_region_y = event.mouse_region_y
        self.build_box_shader()
        self.handler = context.space_data.draw_handler_add(self.draw_box_shader, (), 'WINDOW', 'POST_PIXEL')
        self.update_shader_position(context, event)

    def finish_custom_selection_stage(self, context):
        context.workspace.status_text_set(text=None)
        context.space_data.draw_handler_remove(self.handler, 'WINDOW')
        context.region.tag_redraw()

    def invoke_inbuilt_box_select(self):
        self.stage = 'INBUILT_OP'
        bpy.ops.view3d.select_box('INVOKE_DEFAULT', mode=self.curr_mode, wait_for_input=self.wait_for_input)

    def exec_inbuilt_box_select(self):
        # Get selection rectangle coordinates.
        xmin = min(self.start_mouse_region_x, self.last_mouse_region_x)
        xmax = max(self.start_mouse_region_x, self.last_mouse_region_x)
        ymin = min(self.start_mouse_region_y, self.last_mouse_region_y)
        ymax = max(self.start_mouse_region_y, self.last_mouse_region_y)
        bpy.ops.view3d.select_box(mode=self.curr_mode, wait_for_input=False, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)

    def begin_custom_intersect_tests(self, context):
        # Get selection rectangle coordinates.
        xmin = min(self.start_mouse_region_x, self.last_mouse_region_x)
        xmax = max(self.start_mouse_region_x, self.last_mouse_region_x)
        ymin = min(self.start_mouse_region_y, self.last_mouse_region_y)
        ymax = max(self.start_mouse_region_y, self.last_mouse_region_y)

        # Do selection.
        select_mesh_elements(
            context,
            mode=self.curr_mode,
            tool='BOX',
            tool_co_kwargs={"box_xmin": xmin, "box_xmax": xmax, "box_ymin": ymin, "box_ymax": ymax},
            select_all_edges=self.select_all_edges,
            select_all_faces=self.select_all_faces,
            select_backfacing=self.select_backfacing,
        )

    def finish_modal(self, context):
        restore_overlays(self, context)
        restore_modifiers(self)

    def update_direction_and_properties(self, context):
        if self.directional and self.last_mouse_region_x != self.start_mouse_region_x:
            if self.last_mouse_region_x - self.start_mouse_region_x > 0:
                direction = "LEFT_TO_RIGHT"
            else:
                direction = "RIGHT_TO_LEFT"

            if direction != self.direction:
                self.direction = direction
                set_properties_from_direction(self, self.direction)
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
                set_shading_from_properties(self, context)

    def update_ubo(self):
        self.UBO.update(gpu.types.Buffer("UBYTE", ctypes.sizeof(self.UBO_data), self.UBO_data))  # noqa

    def update_shader_position(self, context, event):
        self.last_mouse_region_x = event.mouse_region_x
        self.last_mouse_region_y = event.mouse_region_y
        context.region.tag_redraw()

    def build_crosshair_shader(self, context):
        width = context.region.width
        height = context.region.height
        vertices = ((0, -height), (0, height), (-width, 0), (width, 0))
        lengths = (0, 2 * height, 0, 2 * width)
        self.crosshair_batch = batch_for_shader(CROSSHAIR_SHADER, 'LINES', {"pos": vertices, "len": lengths})

    def draw_crosshair_shader(self):
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
        gap_color = (0.0, 0.0, 0.0, 1.0)

        # UBO.
        self.UBO_data.u_X = self.last_mouse_region_x
        self.UBO_data.u_Y = self.last_mouse_region_y
        self.UBO_data.u_SegmentColor = segment_color
        self.UBO_data.u_GapColor = gap_color
        self.update_ubo()

        # Crosshair.
        CROSSHAIR_SHADER.bind()
        BORDER_SHADER.uniform_block("ub", self.UBO)
        CROSSHAIR_SHADER.uniform_float("u_ViewProjectionMatrix", matrix)
        self.crosshair_batch.draw(CROSSHAIR_SHADER)

    def build_box_shader(self):
        vertices = ((0, 0), (1, 0), (1, 1), (0, 1), (0, 0))
        lengths = ((0, 0), (1, 0), (1, 1), (2, 1), (2, 2))
        self.border_batch = batch_for_shader(BORDER_SHADER, 'LINE_STRIP', {"pos": vertices, "len": lengths})

        vertices = ((0, 0), (1, 0), (0, 1), (1, 1))
        self.fill_batch = batch_for_shader(FILL_SHADER, 'TRI_STRIP', {"pos": vertices})

    def draw_box_shader(self):
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
        width = self.last_mouse_region_x - self.start_mouse_region_x
        height = self.last_mouse_region_y - self.start_mouse_region_y
        dashed = False if self.direction == "RIGHT_TO_LEFT" else True

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
        gpu.state.blend_set("ALPHA")
        FILL_SHADER.bind()
        FILL_SHADER.uniform_block("ub", self.UBO)
        FILL_SHADER.uniform_float("u_ViewProjectionMatrix", matrix)
        self.fill_batch.draw(FILL_SHADER)
        gpu.state.blend_set("NONE")

        # Border.
        BORDER_SHADER.bind()
        BORDER_SHADER.uniform_block("ub", self.UBO)
        BORDER_SHADER.uniform_float("u_ViewProjectionMatrix", matrix)
        self.border_batch.draw(BORDER_SHADER)

        # Solid border shadow.
        if not dashed:
            self.UBO_data.u_X = self.start_mouse_region_x + 1
            self.UBO_data.u_Y = self.start_mouse_region_y - 1
            self.UBO_data.u_SegmentColor = shadow_color
            self.update_ubo()

            BORDER_SHADER.uniform_block("ub", self.UBO)
            self.border_batch.draw(BORDER_SHADER)
