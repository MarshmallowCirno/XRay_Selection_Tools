import bpy
import textwrap


def draw_select_all_edges_info_popup(self, context):
    layout = self.layout
    text = \
        "By default, only those edges will be selected that have both vertices inside " \
        "the selection box, lasso, or circle when selection through is enabled. Enable this " \
        "option if you want to select all edges, that touch a selection border (this is " \
        "slower than the default selection)."
    lines = textwrap.fill(text, 120)
    lines = lines.splitlines()
    col = layout.column(align=True)
    for n in lines:
        col.label(text=n)


def draw_select_all_faces_info_popup(self, context):
    layout = self.layout
    text = \
        "By default, faces are selected by their centers when selection through is enabled. " \
        "So, only those faces will be selected, the centers of which are inside the selection " \
        "box, lasso, or circle. Enable this option if you want to select all faces, that touch " \
        "a selection border (this is slower than the default selection)."
    lines = textwrap.fill(text, 120)
    lines = lines.splitlines()
    col = layout.column(align=True)
    for n in lines:
        col.label(text=n)


def draw_wait_for_input_cursor_info_popup(self, context):
    layout = self.layout
    text = \
        "Show crosshair of box tool or lasso icon next to cursor of lasso tool when " \
        "starting selection with a hotkey."
    lines = textwrap.fill(text, 120)
    lines = lines.splitlines()
    col = layout.column(align=True)
    for n in lines:
        col.label(text=n)


def draw_tools_keymap_info_popup(self, context):
    layout = self.layout
    text = \
        "Tools key modifiers that change selection mode when held down before you use a box, " \
        "lasso or circle tool in the toolbar. Deactivating selection mode here will remove " \
        "its shortcut from all xray selection tools. Note that difference and intersect mode " \
        "don't work with circle selection and their shortcuts won't be added to circle select " \
        "tool, even if modes are active here."
    lines = textwrap.fill(text, 120)
    lines = lines.splitlines()
    col = layout.column(align=True)
    for n in lines:
        col.label(text=n)


class XRAYSEL_OT_show_info_popup(bpy.types.Operator):
    bl_idname = "xraysel.show_info_popup"
    bl_label = "Select X-Ray"

    button: bpy.props.StringProperty()

    def invoke(self, context, event):
        if self.button == "select_all_edges":
            context.window_manager.popover(draw_select_all_edges_info_popup,
                                           ui_units_x=30, keymap=None, from_active_button=True)
        elif self.button == "select_all_faces":
            context.window_manager.popover(draw_select_all_faces_info_popup,
                                           ui_units_x=30, keymap=None, from_active_button=True)
        elif self.button == "wait_for_input_cursor":
            context.window_manager.popover(draw_wait_for_input_cursor_info_popup,
                                           ui_units_x=30, keymap=None, from_active_button=True)
        elif self.button == "tools_keymap":
            context.window_manager.popover(draw_tools_keymap_info_popup,
                                           ui_units_x=31, keymap=None, from_active_button=True)
        return {'FINISHED'}


classes = (
    XRAYSEL_OT_show_info_popup,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
