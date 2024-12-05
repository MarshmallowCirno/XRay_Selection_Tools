import bpy
import numpy as np
from numpy.typing import NDArray


def center_coordinates(me: bpy.types.Mesh) -> NDArray[np.float32]:
    """
    Retrieve local coordinates of face centers.
    """
    face_count = len(me.polygons)
    face_center_co_local = np.empty((face_count, 3), "f")
    me.polygons.foreach_get("center", face_center_co_local.reshape(-1))
    return face_center_co_local


def vertex_count(me: bpy.types.Mesh) -> NDArray[np.int32]:
    """
    Retrieve count of face vertices.
    """
    face_count = len(me.polygons)
    face_loop_totals = np.empty(face_count, "i")
    me.polygons.foreach_get("loop_total", face_loop_totals)
    return face_loop_totals


def vertex_indices(me: bpy.types.Mesh) -> NDArray[np.int32]:
    """
    Retrieve indices of face vertices.
    """
    loop_count = len(me.loops)
    face_vert_indices = np.empty(loop_count, "i")
    if bpy.app.version >= (3, 6, 0):
        if ".corner_vert" not in me.attributes:
            me.attributes.new(name=".corner_vert", type="INT", domain="CORNER")
        data = me.attributes[".corner_vert"].data
        data.foreach_get("value", face_vert_indices)
    else:
        me.polygons.foreach_get("vertices", face_vert_indices)
    return face_vert_indices


def edge_indices(me: bpy.types.Mesh) -> NDArray[np.int32]:
    """
    Retrieve indices of face edges.
    """
    loop_count = len(me.loops)
    loop_edge_indices = np.empty(loop_count, "i")
    if bpy.app.version >= (3, 6, 0):
        if ".corner_edge" not in me.attributes:
            me.attributes.new(name=".corner_edge", type="INT", domain="CORNER")
        data = me.attributes[".corner_edge"].data
        data.foreach_get("value", loop_edge_indices)
    else:
        me.loops.foreach_get("edge_index", loop_edge_indices)
    return loop_edge_indices


def visibility_mask(me: bpy.types.Mesh) -> NDArray[np.bool_]:
    """
    Retrieve a mask of visible faces.
    """
    face_count = len(me.polygons)
    faces_mask_hid = np.empty(face_count, "?")
    if bpy.app.version >= (3, 4, 0):
        if ".hide_poly" not in me.attributes:
            me.attributes.new(name=".hide_poly", type="BOOLEAN", domain="FACE")
        data = me.attributes[".hide_poly"].data
        data.foreach_get("value", faces_mask_hid)
    else:
        me.polygons.foreach_get("hide", faces_mask_hid)
    return ~faces_mask_hid


def normal_vector(me: bpy.types.Mesh) -> NDArray[np.float32]:
    """
    Retrieve normals of faces.
    """
    face_count = len(me.polygons)
    face_normal = np.empty((face_count, 3), "f")
    me.polygons.foreach_get("normal", face_normal.reshape(-1))
    return face_normal


def selection_mask(me: bpy.types.Mesh) -> NDArray[np.bool_]:
    """
    Retrieve a mask of selected faces.
    """
    face_count = len(me.polygons)
    faces_mask_sel = np.empty(face_count, "?")
    if bpy.app.version >= (3, 4, 0):
        if ".select_poly" not in me.attributes:
            me.attributes.new(name=".select_poly", type="BOOLEAN", domain="FACE")
        data = me.attributes[".select_poly"].data
        data.foreach_get("value", faces_mask_sel)
    else:
        me.polygons.foreach_get("select", faces_mask_sel)
    return faces_mask_sel
