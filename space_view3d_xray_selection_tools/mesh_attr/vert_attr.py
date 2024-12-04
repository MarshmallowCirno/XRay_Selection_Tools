import bpy
import numpy as np
from numpy.typing import NDArray


def coordinates(me: bpy.types.Mesh) -> NDArray[np.float32]:
    """
    Retrieve local coordinates of vertices.
    """
    vert_count = len(me.vertices)
    vert_co_local = np.empty(vert_count * 3, "f")
    if bpy.app.version >= (3, 5, 0):
        me.attributes.new(name="position", type="FLOAT_VECTOR", domain="POINT")
        data = me.attributes["position"].data
        data.foreach_get("vector", vert_co_local)
    else:
        me.vertices.foreach_get("co", vert_co_local)
    vert_co_local.shape = (vert_count, 3)
    return vert_co_local


def visibility_mask(me: bpy.types.Mesh) -> NDArray[np.bool_]:
    """
    Retrieve a mask of visible vertices.
    """
    vert_count = len(me.vertices)
    verts_mask_vis = np.empty(vert_count, "?")
    if bpy.app.version >= (3, 4, 0):
        me.attributes.new(name=".hide_vert", type="BOOLEAN", domain="POINT")
        data = me.attributes[".hide_vert"].data
        data.foreach_get("value", verts_mask_vis)
    else:
        me.vertices.foreach_get("hide", verts_mask_vis)
    verts_mask_vis = ~verts_mask_vis
    return verts_mask_vis


def normal_vector(me: bpy.types.Mesh) -> NDArray[np.float32]:
    """
    Retrieve normals of vertices.
    """
    vert_count = len(me.vertices)
    vert_normal = np.empty(vert_count * 3, "f")
    me.vertices.foreach_get("normal", vert_normal)
    vert_normal.shape = (vert_count, 3)
    return vert_normal


def selection_mask(me: bpy.types.Mesh) -> NDArray[np.bool_]:
    """
    Retrieve a mask of selected vertices.
    """
    vert_count = len(me.vertices)
    verts_mask_sel = np.zeros(vert_count, "?")
    if bpy.app.version >= (3, 4, 0):
        me.attributes.new(name=".select_vert", type="BOOLEAN", domain="POINT")
        data = me.attributes[".select_vert"].data
        data.foreach_get("value", verts_mask_sel)
    else:
        me.vertices.foreach_get("select", verts_mask_sel)
    return verts_mask_sel
