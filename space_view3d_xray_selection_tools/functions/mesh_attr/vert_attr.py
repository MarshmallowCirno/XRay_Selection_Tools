from typing import cast

import bpy
import numpy as np

from ...types import Bool1DArray, Float3DArray


def coordinates(me: bpy.types.Mesh) -> Float3DArray:
    """
    Retrieve local coordinates of vertices.
    """
    vert_count = len(me.vertices)
    vert_co_local = np.empty((vert_count, 3), "f")
    if bpy.app.version >= (3, 5, 0):
        if "position" not in me.attributes:
            me.attributes.new(name="position", type="FLOAT_VECTOR", domain="POINT")
        data = cast(bpy.types.FloatVectorAttribute, me.attributes["position"]).data
        data.foreach_get("vector", vert_co_local.reshape(-1))  # pyright: ignore[reportArgumentType]
    else:
        me.vertices.foreach_get("co", vert_co_local.reshape(-1))  # pyright: ignore[reportArgumentType]
    return vert_co_local


def visibility_mask(me: bpy.types.Mesh) -> Bool1DArray:
    """
    Retrieve a mask of visible vertices.
    """
    vert_count = len(me.vertices)
    verts_mask_hid = np.empty(vert_count, "?")
    if bpy.app.version >= (3, 4, 0):
        if ".hide_vert" not in me.attributes:
            me.attributes.new(name=".hide_vert", type="BOOLEAN", domain="POINT")
        data = cast(bpy.types.BoolAttribute, me.attributes[".hide_vert"]).data
        data.foreach_get("value", verts_mask_hid)  # pyright: ignore[reportArgumentType]
    else:
        me.vertices.foreach_get("hide", verts_mask_hid)  # pyright: ignore[reportArgumentType]
    return ~verts_mask_hid


def normal_vector(me: bpy.types.Mesh) -> Float3DArray:
    """
    Retrieve normals of vertices.
    """
    vert_count = len(me.vertices)
    vert_normal = np.empty((vert_count, 3), "f")
    me.vertices.foreach_get("normal", vert_normal.reshape(-1))  # pyright: ignore[reportArgumentType]
    return vert_normal


def selection_mask(me: bpy.types.Mesh) -> Bool1DArray:
    """
    Retrieve a mask of selected vertices.
    """
    vert_count = len(me.vertices)
    verts_mask_sel = np.empty(vert_count, "?")
    if bpy.app.version >= (3, 4, 0):
        if ".select_vert" not in me.attributes:
            me.attributes.new(name=".select_vert", type="BOOLEAN", domain="POINT")
        data = cast(bpy.types.BoolAttribute, me.attributes[".select_vert"]).data
        data.foreach_get("value", verts_mask_sel)  # pyright: ignore[reportArgumentType]
    else:
        me.vertices.foreach_get("select", verts_mask_sel)  # pyright: ignore[reportArgumentType]
    return verts_mask_sel
