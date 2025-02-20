import textwrap
from functools import partial
from typing import TYPE_CHECKING

import bpy

if TYPE_CHECKING:
    from bpy._typing.rna_enums import OperatorReturnItems


_info_texts: dict[str, tuple[str, ...]] = {
    "select_all_edges": (
        "By default, in selection through mode tools select only edges, both vertices of which are inside a "
        "selection region. Enable this option if you want to select all edges, that overlap a selection region "
        "(this is slower than the default selection on meshes with a lot of geometry).",
    ),
    "select_all_faces": (
        "By default, in selection through mode tools select only faces whose center dots are inside a selection "
        "region. Enable this option if you want to select all faces, that overlap a selection region "
        "(this is slower than the default selection on meshes with a lot of geometry).",
    ),
    "select_backfacing": (
        "By default, in selection through mode tools select elements regardless of their normal directions. "
        "Disable this option if you want to select only elements with back side facing away from you "
        "(this is slower than the default selection on meshes with a lot of geometry).",
    ),
    "drag_direction": (
        "For example you can set up selection through for right-to-left drag direction and disable it for "
        "left-to-right drag direction.",
    ),
    "hide_modifiers": (
        "Hide mirror modifier or solidify modifier during selection through and re-enable them after finishing "
        "selection. This can be useful on dense mesh, making it easier to see real geometry in x-ray shading.",
    ),
    "wait_for_input_cursor": (
        "Show crosshair of box tool or lasso icon of lasso tool next to cursor when tool is started with "
        "a keyboard shortcut.",
    ),
    "hide_gizmo": (
        "Hide gizmo of the active tool for the duration of the selection and restore it after " "finishing selection.",
    ),
    "group_with_builtins": (
        "Enable to place tools inside the group with builtin selection tools, disable to create a new separate group.",
    ),
    "selection_behavior": (
        "• In Origin mode you select only objects with origins within the selection region.",
        "• In Contain mode you select only objects entirely enclosed in the selection region.",
        "• In Overlap mode you select all objects within the selection region, plus any objects "
        "crossing boundaries of the selection region.",
        "• In Direction mode you automatically switch between Overlap and Contain selection "
        "based on cursor movement direction.",
        "    ○ Drag from left to right to select all objects crossing or within the selection region (Overlap).",
        "    ○ Drag from right to left to select all objects entirely enclosed in the selection region (Contain).",
        "Note that every mode is slower than the default one on objects with a lot of geometry.",
    ),
    "tool_keymaps": (
        "Change, disable or enable shortcuts here. To edit shortcut properties independently of global addon "
        "settings, expand key item and check Override Global Properties.",
        "Deactivating header here will remove shortcuts below it from blender keyconfig.",
    ),
    "tool_selection_mode_keymaps": (
        "Keys that change selection mode when held down before using a box, lasso or circle xray tool in the "
        "toolbar.",
        "Deactivating selection mode here will remove its shortcut from xray selection tool.",
        "Active Mode corresponds to active selection mode button in blender header or Active Tool tab in "
        "blender properties area.",
    ),
}


def _draw_func(self: bpy.types.Operator, _context: bpy.types.Context, description: tuple[str, ...]):
    for paragraph in description:
        lines = textwrap.wrap(paragraph, 115)
        col = self.layout.column(align=True)
        for line in lines:
            col.label(text=line)


class XRAYSEL_OT_show_info_popup(bpy.types.Operator):
    """Show description"""

    bl_idname = "xraysel.show_info_popup"
    bl_label = "Show Info"

    if TYPE_CHECKING:
        button: str
    else:
        button: bpy.props.StringProperty()

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set["OperatorReturnItems"]:
        description = _info_texts.get(self.button, ("Description not found",))
        draw_func = partial(_draw_func, description=description)
        context.window_manager.popover(draw_func, ui_units_x=31, keymap=None, from_active_button=True)
        return {'FINISHED'}
