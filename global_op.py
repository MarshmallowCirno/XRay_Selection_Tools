import bpy
import blf
from .preferences import get_preferences


def draw_text(text, pos_x, pos_y, align="LEFT", font=0, font_size=12, color=(1, 1, 1, 1)):
    blf.size(font, font_size, 0)
    blf.color(font, *color)
    blf.enable(font, blf.SHADOW)
    blf.shadow_offset(font, 1, -1)
    blf.shadow(font, 3, *(0, 0, 0, 1))

    if align == "RIGHT":
        width, height = blf.dimensions(font, text)
        blf.position(font, pos_x - width, pos_y, 0)
    else:
        blf.position(font, pos_x, pos_y, 0)

    blf.draw(font, text)


def get_text_dimensions(text, font=0):
    return blf.dimensions(font, text)


def get_safe_draw_x(context, ui_width):
    """Maximum x position of ui left side that doesn't cause overlap width sidebar"""
    region_overlap = context.preferences.system.use_region_overlap
    if context.space_data.show_region_ui and region_overlap:
        for region in context.area.regions:
            if region.type == 'UI':
                offset_width = region.width  # area of 3d view covered by sidebar
                break
    else:
        offset_width = 0

    safe_x = context.region.width - offset_width - ui_width
    return safe_x


class MESH_OT_select_tools_xray_toggle_select_through(bpy.types.Operator):
    """Toggle selection through for all mesh xray selection tools"""
    bl_idname = "mesh.select_tools_xray_toggle_select_through"
    bl_label = "Toggle Select Through for X-Ray Select Tools"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self):
        self.handler = None
        self.timer = None

    def execute(self, context):
        get_preferences().me_select_through = not get_preferences().me_select_through
        return {'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)

        context.window_manager.modal_handler_add(self)

        self.handler = context.space_data.draw_handler_add(
            self.draw_ui, (context,), 'WINDOW', 'POST_PIXEL')
        context.area.tag_redraw()

        self.timer = context.window_manager.event_timer_add(0.1, window=context.window)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'TIMER':
            if self.timer.time_duration > 0.25:
                context.window_manager.event_timer_remove(self.timer)
                context.space_data.draw_handler_remove(self.handler, 'WINDOW')
                context.area.tag_redraw()
                return {'FINISHED'}

        return {'PASS_THROUGH'}

    def draw_ui(self, context):
        ui_scale = context.preferences.view.ui_scale
        main_color = (1.0, 1.0, 1.0, 1.0)

        font = 0
        font_size = int(20 * ui_scale)
        align = "RIGHT"

        width_offset, height_offset = 20, 40
        ui_offset = 40 * ui_scale

        safe_x, safe_y = get_safe_draw_x(context, width_offset + ui_offset), \
                         height_offset + ui_offset

        text = "Select Through" if get_preferences().me_select_through else "OFF"

        draw_text(text, safe_x, safe_y, align, font, font_size, main_color)


classes = (
    MESH_OT_select_tools_xray_toggle_select_through,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
