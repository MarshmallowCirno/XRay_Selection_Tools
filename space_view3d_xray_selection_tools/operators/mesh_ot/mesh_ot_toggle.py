from typing import TYPE_CHECKING, Any, Literal

import blf
import bpy

from ... import addon_info

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems


def _draw_text(
    text: str,
    pos_x: float,
    pos_y: float,
    align: Literal['LEFT', 'RIGHT'] = 'LEFT',
    font: int = 0,
    font_size: int = 12,
    color: tuple[float, float, float, float] = (1, 1, 1, 1),
):
    if bpy.app.version >= (4, 0, 0):
        blf.size(font, font_size)
    else:
        blf.size(font, font_size, 0)  # pyright: ignore [reportCallIssue]
    blf.color(font, *color)
    blf.enable(font, blf.SHADOW)
    blf.shadow_offset(font, 1, -1)
    blf.shadow(font, 3, *(0, 0, 0, 1))

    if align == 'RIGHT':
        width, _height = blf.dimensions(font, text)
        blf.position(font, pos_x - width, pos_y, 0)
    else:
        blf.position(font, pos_x, pos_y, 0)

    blf.draw(font, text)


def _get_safe_draw_x(context: bpy.types.Context, ui_width: int):
    """Maximum x position of ui left side that doesn't cause overlap width sidebar."""
    region_overlap = context.preferences.system.use_region_overlap
    offset_width = 0
    sv3d = context.space_data
    assert isinstance(sv3d, bpy.types.SpaceView3D)

    if sv3d.show_region_ui and region_overlap:
        for region in context.area.regions:
            if region.type == 'UI':
                offset_width = region.width  # area of 3d view covered by sidebar
                break

    safe_x = context.region.width - offset_width - ui_width
    return safe_x


class _ToggleBase(bpy.types.Operator):
    def __init__(self, *args: Any, **kwargs: Any):
        self.handler: Any | None = None
        self.timer: bpy.types.Timer | None = None
        self.text: str = NotImplemented

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set["OperatorReturnItems"]:
        self.execute(context)

        context.window_manager.modal_handler_add(self)
        self.handler = context.space_data.draw_handler_add(self.draw_ui, (context,), 'WINDOW', 'POST_PIXEL')  # pyright: ignore[reportArgumentType]
        context.area.tag_redraw()
        self.timer = context.window_manager.event_timer_add(0.1, window=context.window)
        return {'RUNNING_MODAL'}

    def modal(self, context: bpy.types.Context, event: bpy.types.Event) -> set["OperatorReturnItems"]:
        if event.type == 'TIMER':
            assert isinstance(self.timer, bpy.types.Timer)
            if self.timer.time_duration > 0.25:
                context.window_manager.event_timer_remove(self.timer)
                context.space_data.draw_handler_remove(self.handler, 'WINDOW')
                context.area.tag_redraw()
                return {'FINISHED'}
        return {'PASS_THROUGH'}

    def draw_ui(self, context: bpy.types.Context):
        ui_scale = context.preferences.view.ui_scale
        main_color = (1.0, 1.0, 1.0, 1.0)
        font = 0
        font_size = int(20 * ui_scale)
        align = "RIGHT"
        width_offset, height_offset = 20, 40
        ui_offset = int(40 * ui_scale)
        safe_x, safe_y = _get_safe_draw_x(context, width_offset + ui_offset), height_offset + ui_offset
        _draw_text(self.text, safe_x, safe_y, align, font, font_size, main_color)


class MESH_OT_select_tools_xray_toggle_select_through(_ToggleBase):
    """Toggle selection through for mesh xray selection tools."""

    bl_idname = "mesh.select_tools_xray_toggle_select_through"
    bl_label = "Toggle Select Through"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.text = "OFF" if addon_info.get_preferences().mesh_tools.select_through else "Select Through"

    def execute(self, context: bpy.types.Context) -> set["OperatorReturnItems"]:
        addon_info.get_preferences().mesh_tools.select_through = (
            not addon_info.get_preferences().mesh_tools.select_through
        )
        return {'FINISHED'}


class MESH_OT_select_tools_xray_toggle_mesh_behavior(_ToggleBase):
    """Toggle mesh selection behavior for mesh xray selection tools."""

    bl_idname = "mesh.select_tools_xray_toggle_mesh_behavior"
    bl_label = "Toggle Select All Edges & Faces"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.text = "Default" if addon_info.get_preferences().mesh_tools.select_all_edges else "Select All"

    def execute(self, context: bpy.types.Context) -> set["OperatorReturnItems"]:
        _ = addon_info.get_preferences().mesh_tools.select_all_edges
        addon_info.get_preferences().mesh_tools.select_all_edges = not _
        addon_info.get_preferences().mesh_tools.select_all_faces = not _
        return {'FINISHED'}


class MESH_OT_select_tools_xray_toggle_select_backfacing(_ToggleBase):
    """Toggle backfacing selection for mesh xray selection tools."""

    bl_idname = "mesh.select_tools_xray_toggle_select_backfacing"
    bl_label = "Toggle Select Backfacing"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.text = "Default" if not addon_info.get_preferences().mesh_tools.select_backfacing else "Exclude Backfacing"

    def execute(self, context: bpy.types.Context) -> set["OperatorReturnItems"]:
        addon_info.get_preferences().mesh_tools.select_backfacing = (
            not addon_info.get_preferences().mesh_tools.select_backfacing
        )
        return {'FINISHED'}
