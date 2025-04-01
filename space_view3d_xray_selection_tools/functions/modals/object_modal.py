from typing import TYPE_CHECKING, Any, Literal, TypeAlias, cast

import bpy

from ... import addon_info

if TYPE_CHECKING:
    from ...operators.object_ot.object_ot_box import OBJECT_OT_select_box_xray
    from ...operators.object_ot.object_ot_circle import OBJECT_OT_select_circle_xray
    from ...operators.object_ot.object_ot_lasso import OBJECT_OT_select_lasso_xray

_OBJECT_OT: TypeAlias = "OBJECT_OT_select_box_xray | OBJECT_OT_select_circle_xray | OBJECT_OT_select_lasso_xray"


def gather_overlays(context: bpy.types.Context) -> dict[str, Any]:
    sv3d = context.space_data
    assert isinstance(sv3d, bpy.types.SpaceView3D)

    overlays = {
        "show_xray": sv3d.shading.show_xray,
        "show_xray_wireframe": sv3d.shading.show_xray_wireframe,
        "show_gizmo": sv3d.show_gizmo,
    }
    return overlays


def set_properties(op: _OBJECT_OT, tool: Literal['BOX', 'CIRCLE', 'LASSO']) -> None:
    object_tools_props = addon_info.get_preferences().object_tools

    if not op.override_global_props:
        op.show_xray = object_tools_props.show_xray
        op.xray_toggle_key = object_tools_props.xray_toggle_key
        op.xray_toggle_type = object_tools_props.xray_toggle_type
        op.hide_gizmo = object_tools_props.hide_gizmo
        match tool:
            case 'BOX':
                op = cast("OBJECT_OT_select_box_xray", op)
                op.show_crosshair = object_tools_props.show_crosshair
                op.behavior = op.curr_behavior = object_tools_props.box_select_behavior
            case 'CIRCLE':
                op = cast("OBJECT_OT_select_circle_xray", op)
                op.behavior = object_tools_props.circle_select_behavior
            case 'LASSO':
                op = cast("OBJECT_OT_select_lasso_xray", op)
                op.show_lasso_icon = object_tools_props.show_lasso_icon
                op.behavior = op.curr_behavior = object_tools_props.lasso_select_behavior


def sync_properties(op: _OBJECT_OT, context: bpy.types.Context) -> None:
    """Sync operator parameters to current context shading. So if xray already enabled
    make sure it would be possible to toggle it regardless of operator parameters."""
    sv3d = context.space_data
    assert isinstance(sv3d, bpy.types.SpaceView3D)

    if (
        sv3d.shading.type in {'SOLID', 'MATERIAL', 'RENDERED'}
        and sv3d.shading.show_xray
        or sv3d.shading.type == 'WIREFRAME'
        and sv3d.shading.show_xray_wireframe
    ):
        op.show_xray = True


def toggle_overlays(op: _OBJECT_OT, context: bpy.types.Context) -> None:
    sv3d = context.space_data
    assert isinstance(sv3d, bpy.types.SpaceView3D)

    if sv3d.shading.type in {'SOLID', 'MATERIAL', 'RENDERED'}:
        sv3d.shading.show_xray = op.show_xray
    elif sv3d.shading.type == 'WIREFRAME':
        sv3d.shading.show_xray_wireframe = op.show_xray

    if op.hide_gizmo:
        sv3d.show_gizmo = False


def restore_overlays(op: _OBJECT_OT, context: bpy.types.Context) -> None:
    sv3d = context.space_data
    assert isinstance(sv3d, bpy.types.SpaceView3D)

    if op.init_overlays:
        sv3d.shading.show_xray = op.init_overlays["show_xray"]
        sv3d.shading.show_xray_wireframe = op.init_overlays["show_xray_wireframe"]
        sv3d.show_gizmo = op.init_overlays["show_gizmo"]


def get_xray_toggle_key_list() -> (
    set[Literal['LEFT_CTRL', 'RIGHT_CTRL', 'LEFT_ALT', 'RIGHT_ALT', 'LEFT_SHIFT', 'RIGHT_SHIFT', 'OSKEY', 'DISABLED']]
):
    match addon_info.get_preferences().object_tools.xray_toggle_key:
        case 'CTRL':
            return {'LEFT_CTRL', 'RIGHT_CTRL'}
        case 'ALT':
            return {'LEFT_ALT', 'RIGHT_ALT'}
        case 'SHIFT':
            return {'LEFT_SHIFT', 'RIGHT_SHIFT'}
        case 'OSKEY':
            return {'OSKEY'}
        case 'DISABLED':
            return {'DISABLED'}


def toggle_alt_mode(op: _OBJECT_OT, event: bpy.types.Event) -> None:
    if (
        event.ctrl
        and op.alt_mode_toggle_key == 'CTRL'
        or event.alt
        and op.alt_mode_toggle_key == 'ALT'
        or event.shift
        and op.alt_mode_toggle_key == 'SHIFT'
        or event.oskey
        and op.alt_mode_toggle_key == 'OSKEY'
    ):
        op.curr_mode = op.alt_mode
    else:
        op.curr_mode = op.mode  # pyright: ignore[reportAttributeAccessIssue]
