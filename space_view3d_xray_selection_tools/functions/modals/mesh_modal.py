from typing import TYPE_CHECKING, Any, Literal, TypeAlias, cast

import bpy

from ... import addon_info

if TYPE_CHECKING:
    from ...operators.mesh_ot.mesh_ot_box import MESH_OT_select_box_xray
    from ...operators.mesh_ot.mesh_ot_circle import MESH_OT_select_circle_xray
    from ...operators.mesh_ot.mesh_ot_lasso import MESH_OT_select_lasso_xray


_MESH_OT: TypeAlias = "MESH_OT_select_box_xray | MESH_OT_select_circle_xray | MESH_OT_select_lasso_xray"


def gather_overlays(context: bpy.types.Context) -> dict[str, Any]:
    sv3d = context.space_data
    assert isinstance(sv3d, bpy.types.SpaceView3D)

    overlays = {
        "show_xray": sv3d.shading.show_xray,
        "show_xray_wireframe": sv3d.shading.show_xray_wireframe,
        "show_gizmo": sv3d.show_gizmo,
    }
    if bpy.app.version < (4, 1, 0):
        overlays.update(
            {
                "xray_alpha": sv3d.shading.xray_alpha,
                "xray_alpha_wireframe": sv3d.shading.xray_alpha_wireframe,
                "backwire_opacity": sv3d.overlay.backwire_opacity,  # type: ignore
            }
        )
    if bpy.app.version >= (4, 1, 0):
        overlays["show_face_center"] = sv3d.overlay.show_face_center
    return overlays


def gather_modifiers(op: _MESH_OT, context: bpy.types.Context) -> list[tuple[bpy.types.Modifier, bool]]:
    mods: list[tuple[bpy.types.Modifier, bool]] = []
    mods_to_hide: set[Literal['MIRROR', 'SOLIDIFY']] = set()

    if op.hide_mirror:
        mods_to_hide.add('MIRROR')
    if op.hide_solidify:
        mods_to_hide.add('SOLIDIFY')

    sel_obs = context.selected_objects if context.selected_objects else [context.object]
    for ob in sel_obs:
        assert isinstance(ob, bpy.types.Object)
        mods.extend([(m, m.show_in_editmode) for m in ob.modifiers if m.type in mods_to_hide])
    return mods


def set_properties_from_preferences(
    op: _MESH_OT,
    tool: Literal['BOX', 'CIRCLE', 'LASSO'],
) -> None:
    mesh_tools_props = addon_info.get_preferences().mesh_tools
    direction_props = mesh_tools_props.direction_properties

    if not op.override_global_props:
        if op.directional:  # for initial shading before direction is determined
            op.select_through = direction_props[0].select_through and direction_props[1].select_through
            op.show_xray = direction_props[0].show_xray and direction_props[1].show_xray and op.select_through
        else:
            op.select_through = mesh_tools_props.select_through
            op.default_color = mesh_tools_props.default_color
            op.select_through_color = mesh_tools_props.select_through_color
            op.show_xray = mesh_tools_props.show_xray
            op.select_all_edges = mesh_tools_props.select_all_edges
            op.select_all_faces = mesh_tools_props.select_all_faces
            op.select_backfacing = mesh_tools_props.select_backfacing

        op.select_through_toggle_key = mesh_tools_props.select_through_toggle_key
        op.select_through_toggle_type = mesh_tools_props.select_through_toggle_type
        op.hide_mirror = mesh_tools_props.hide_mirror
        op.hide_solidify = mesh_tools_props.hide_solidify
        op.hide_gizmo = mesh_tools_props.hide_gizmo
        match tool:
            case 'BOX':
                op = cast("MESH_OT_select_box_xray", op)
                op.show_crosshair = mesh_tools_props.show_crosshair
            case 'LASSO':
                op = cast("MESH_OT_select_lasso_xray", op)
                op.show_lasso_icon = mesh_tools_props.show_lasso_icon
            case 'CIRCLE':
                pass


def initialize_shading_from_properties(op: _MESH_OT, context: bpy.types.Context) -> None:
    sv3d = context.space_data
    assert isinstance(sv3d, bpy.types.SpaceView3D)

    if op.directional:
        # If both directions have prop to show xray turned on
        # enable xray shading for wait for input stage.
        direction_props = addon_info.get_preferences().mesh_tools.direction_properties
        if (
            direction_props[0].select_through
            and direction_props[1].select_through
            and direction_props[0].show_xray
            and direction_props[1].show_xray
        ):
            sv3d.shading.show_xray = True
            sv3d.shading.show_xray_wireframe = True
    else:
        if op.select_through:
            # Default xray shading should be turned on.
            if op.show_xray:
                sv3d.shading.show_xray = True
                sv3d.shading.show_xray_wireframe = True

            if bpy.app.version < (4, 1, 0):
                # Hidden xray shading should be turned on to select through if default xray shading is off.
                if not op.override_intersect_tests:
                    if (
                        sv3d.shading.type in {'SOLID', 'MATERIAL', 'RENDERED'}
                        and not sv3d.shading.show_xray
                        or sv3d.shading.type == 'WIREFRAME'
                        and not sv3d.shading.show_xray_wireframe
                    ):
                        sv3d.shading.show_xray = True
                        sv3d.shading.show_xray_wireframe = True
                        sv3d.shading.xray_alpha = 1.0  # default 0.5
                        sv3d.shading.xray_alpha_wireframe = 1.0  # default 0.0
                        sv3d.overlay.backwire_opacity = (  # pyright: ignore [reportAttributeAccessIssue]
                            0.0  # default 0.5
                        )

            if bpy.app.version >= (4, 1, 0):
                if context.tool_settings.mesh_select_mode[2]:
                    if not op.select_all_faces and not op.show_xray:
                        sv3d.overlay.show_face_center = True

        if op.hide_gizmo:
            sv3d.show_gizmo = False


def set_properties_from_direction(
    op: _MESH_OT,
    direction: Literal['LEFT_TO_RIGHT', 'RIGHT_TO_LEFT'],
) -> None:
    direction_props = addon_info.get_preferences().mesh_tools.direction_properties[direction]
    op.select_through = direction_props.select_through
    op.default_color = direction_props.default_color
    op.select_through_color = direction_props.select_through_color
    op.show_xray = direction_props.show_xray
    op.select_all_edges = direction_props.select_all_edges
    op.select_all_faces = direction_props.select_all_faces
    op.select_backfacing = direction_props.select_backfacing


def set_shading_from_properties(op: _MESH_OT, context: bpy.types.Context) -> None:
    """For toggling overlays by hotkey or by changing dragging direction."""
    sv3d = context.space_data
    assert isinstance(sv3d, bpy.types.SpaceView3D)

    # In general avoiding here turning off xray shading and selecting through if xray shading is already enabled.
    if not (op.directional and not op.direction):  # skip toggling until direction is determined
        # Enable xray shading when it is enabled in props.
        if op.show_xray:
            sv3d.shading.show_xray = True
            sv3d.shading.show_xray_wireframe = True
        # Return initial xray shading when xray is off in props (don't hide xray when it is already enabled).
        else:
            sv3d.shading.show_xray = op.init_overlays["show_xray"]
            sv3d.shading.show_xray_wireframe = op.init_overlays["show_xray_wireframe"]

        if bpy.app.version < (4, 1, 0):
            # If select through is toggled on in props by direction or by key and intersect tests won't be used
            # enabled hidden xray shading to select through
            # don't use hidden xray shading if default xray shading is already enabled.
            if (
                (
                    op.select_through
                    and not op.invert_select_through
                    or not op.select_through
                    and op.invert_select_through
                )
                and not op.override_intersect_tests
                and (
                    sv3d.shading.type in {'SOLID', 'MATERIAL', 'RENDERED'}
                    and not sv3d.shading.show_xray
                    or sv3d.shading.type == 'WIREFRAME'
                    and not sv3d.shading.show_xray_wireframe
                )
            ):
                sv3d.shading.show_xray = True
                sv3d.shading.show_xray_wireframe = True
                sv3d.shading.xray_alpha = 1.0  # default 0.5
                sv3d.shading.xray_alpha_wireframe = 1.0  # default 0.0
                sv3d.overlay.backwire_opacity = 0.0  # default 0.5  # pyright: ignore [reportAttributeAccessIssue]
            else:
                # If hidden xray shading should be off, restore initial overlay opacity.
                sv3d.shading.xray_alpha = op.init_overlays["xray_alpha"]
                sv3d.shading.xray_alpha_wireframe = op.init_overlays["xray_alpha_wireframe"]
                sv3d.overlay.backwire_opacity = op.init_overlays["backwire_opacity"]  # pyright: ignore [reportAttributeAccessIssue]

        if bpy.app.version >= (4, 1, 0):
            # Show face centers in selection through with disabled xray shading.
            if context.tool_settings.mesh_select_mode[2]:
                if (
                    (
                        op.select_through
                        and not op.invert_select_through
                        or not op.select_through
                        and op.invert_select_through
                    )
                    and not op.select_all_faces
                    and not op.show_xray
                ):
                    sv3d.overlay.show_face_center = True
                else:
                    sv3d.overlay.show_face_center = op.init_overlays["show_face_center"]

        # If select through is toggled off in props by direction or by key
        # return initial xray shading.
        if (not op.select_through and not op.invert_select_through) or (op.select_through and op.invert_select_through):
            sv3d.shading.show_xray = op.init_overlays["show_xray"]
            sv3d.shading.show_xray_wireframe = op.init_overlays["show_xray_wireframe"]


def set_modifiers_from_properties(op: _MESH_OT) -> None:
    """Hide modifiers in editmode or restore initial visibility."""
    if op.init_mods:
        if op.select_through:
            for mod, show_in_editmode in op.init_mods:
                if mod.show_in_editmode:
                    mod.show_in_editmode = False
        else:
            for mod, show_in_editmode in op.init_mods:
                if mod.show_in_editmode != show_in_editmode:
                    mod.show_in_editmode = show_in_editmode


def restore_overlays(op: _MESH_OT, context: bpy.types.Context) -> None:
    sv3d = context.space_data
    assert isinstance(sv3d, bpy.types.SpaceView3D)

    if op.init_overlays:
        sv3d.shading.show_xray = op.init_overlays["show_xray"]
        sv3d.shading.show_xray_wireframe = op.init_overlays["show_xray_wireframe"]
        sv3d.show_gizmo = op.init_overlays["show_gizmo"]
        if bpy.app.version < (4, 1, 0):
            sv3d.shading.xray_alpha = op.init_overlays["xray_alpha"]
            sv3d.shading.xray_alpha_wireframe = op.init_overlays["xray_alpha_wireframe"]
            sv3d.overlay.backwire_opacity = op.init_overlays["backwire_opacity"]  # pyright: ignore [reportAttributeAccessIssue]
        if bpy.app.version >= (4, 1, 0):
            sv3d.overlay.show_face_center = op.init_overlays["show_face_center"]


def restore_modifiers(op: _MESH_OT) -> None:
    if op.init_mods:
        for mod, show_in_editmode in op.init_mods:
            if mod.show_in_editmode != show_in_editmode:
                mod.show_in_editmode = show_in_editmode


def get_select_through_toggle_keys() -> (
    set[Literal['LEFT_CTRL', 'RIGHT_CTRL', 'LEFT_ALT', 'RIGHT_ALT', 'LEFT_SHIFT', 'RIGHT_SHIFT', 'OSKEY', 'DISABLED']]
):
    match addon_info.get_preferences().mesh_tools.select_through_toggle_key:
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


def toggle_alt_mode(op: _MESH_OT, event: bpy.types.Event) -> None:
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
        op.curr_mode = op.mode  # pyright: ignore [reportAttributeAccessIssue]


def update_shader_color(
    op: "MESH_OT_select_box_xray | MESH_OT_select_circle_xray | MESH_OT_select_lasso_xray", context: bpy.types.Context
) -> None:
    if op.select_through_color != op.default_color:
        context.region.tag_redraw()
