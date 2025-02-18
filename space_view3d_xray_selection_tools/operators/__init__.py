from . import ot_keymap, xraysel_ot_info
from .mesh_ot import mesh_ot_box, mesh_ot_circle, mesh_ot_lasso, mesh_ot_toggle
from .object_ot import object_ot_box, object_ot_circle, object_ot_lasso

_classes = (
    mesh_ot_box.MESH_OT_select_box_xray,
    mesh_ot_circle.MESH_OT_select_circle_xray,
    mesh_ot_lasso.MESH_OT_select_lasso_xray,
    object_ot_box.OBJECT_OT_select_box_xray,
    object_ot_circle.OBJECT_OT_select_circle_xray,
    object_ot_lasso.OBJECT_OT_select_lasso_xray,
    mesh_ot_toggle.MESH_OT_select_tools_xray_toggle_select_through,
    mesh_ot_toggle.MESH_OT_select_tools_xray_toggle_mesh_behavior,
    mesh_ot_toggle.MESH_OT_select_tools_xray_toggle_select_backfacing,
    xraysel_ot_info.XRAYSEL_OT_show_info_popup,
)


def register() -> None:
    from bpy.utils import register_class  # pyright: ignore[reportUnknownVariableType]

    for cls in _classes:
        register_class(cls)

    ot_keymap.register()


def unregister() -> None:
    ot_keymap.unregister()

    from bpy.utils import unregister_class  # pyright: ignore[reportUnknownVariableType]

    for cls in _classes:
        unregister_class(cls)
