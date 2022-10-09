import bpy
import textwrap


def draw_select_all_edges_info_popup(self, context):
    layout = self.layout
    text = \
        "By default, only those edges will be selected that have both vertices inside " \
        "the selection box, lasso, or circle when selection through is enabled. Enable this " \
        "option if you want to select all edges, that touch a selection border (this is " \
        "slower than the default selection)."
    lines = textwrap.wrap(text, 120)
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
    lines = textwrap.wrap(text, 120)
    col = layout.column(align=True)
    for n in lines:
        col.label(text=n)


def draw_wait_for_input_cursor_info_popup(self, context):
    layout = self.layout
    text = \
        "When starting a selection with a hotkey show crosshair of box tool or lasso icon " \
        "of lasso tool next to cursor."
    lines = textwrap.wrap(text, 120)
    col = layout.column(align=True)
    for n in lines:
        col.label(text=n)


def draw_ob_select_behavior_info_popup(self, context):
    layout = self.layout
    texts = \
        ("• In Origin mode, you select only objects with origins within the selection region.",
         "• In Contain mode, you select only objects within the selection region.",
         "• In Overlap mode, you select all objects within the region, plus any objects "
         "crossing the boundaries of the region.",
         "• In Direction mode, you automatically switch between Overlap and Contain selection "
         "based on cursor movement direction. Drag from left to right to select all objects "
         "that are entirely enclosed in the selection rectangle or lasso (Contain). "
         "Drag from right to left to select all objects that are crossed by the selection "
         "rectangle or lasso (Overlap).",
         "Note that every mode is slower than the default one on high poly objects."
         )
    for text in texts:
        lines = textwrap.wrap(text, 120)
        col = layout.column(align=True)
        for n in lines:
            col.label(text=n)


def draw_tools_keymap_info_popup(self, context):
    layout = self.layout
    texts = \
        ("Keys that change selection mode when held down before using a box, lasso or circle xray tool in the "
         "toolbar. Deactivating selection mode here will remove its shortcut from all xray selection tools.",
         "Active Mode corresponds to active selection mode button in blender header or Active Tool tab in "
         "blender properties area."
         )
    for text in texts:
        lines = textwrap.wrap(text, 120)
        col = layout.column(align=True)
        for n in lines:
            col.label(text=n)


class XRAYSEL_OT_show_info_popup(bpy.types.Operator):
    """Show description"""
    bl_idname = "xraysel.show_info_popup"
    bl_label = "Select X-Ray"

    button: bpy.props.StringProperty()

    def invoke(self, context, event):
        if self.button == "select_all_edges":
            context.window_manager.popover(draw_select_all_edges_info_popup,
                                           ui_units_x=31, keymap=None, from_active_button=True)
        elif self.button == "select_all_faces":
            context.window_manager.popover(draw_select_all_faces_info_popup,
                                           ui_units_x=31, keymap=None, from_active_button=True)
        elif self.button == "wait_for_input_cursor":
            context.window_manager.popover(draw_wait_for_input_cursor_info_popup,
                                           ui_units_x=31, keymap=None, from_active_button=True)
        elif self.button == "ob_selection_behavior":
            context.window_manager.popover(draw_ob_select_behavior_info_popup,
                                           ui_units_x=31, keymap=None, from_active_button=True)
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
