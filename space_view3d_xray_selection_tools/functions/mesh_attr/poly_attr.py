from typing import cast

import bpy
import numpy as np

from ...types import Bool1DArray, Float3DArray, Int1DArray


def center_coordinates(me: bpy.types.Mesh) -> Float3DArray:
    """
    Retrieve local coordinates of polygon centers.
    """
    poly_count = len(me.polygons)
    poly_center_co_local = np.empty((poly_count, 3), "f")
    me.polygons.foreach_get("center", poly_center_co_local.reshape(-1))  # pyright: ignore[reportArgumentType]
    return poly_center_co_local


def vertex_count(me: bpy.types.Mesh) -> Int1DArray:
    """
    Retrieve count of polygon vertices.
    """
    poly_count = len(me.polygons)
    poly_loop_totals = np.empty(poly_count, "i")
    me.polygons.foreach_get("loop_total", poly_loop_totals)  # pyright: ignore[reportArgumentType]
    return poly_loop_totals


def visibility_mask(me: bpy.types.Mesh) -> Bool1DArray:
    """
    Retrieve a mask of visible polygons.
    """
    poly_count = len(me.polygons)
    polys_mask_hid = np.empty(poly_count, "?")
    if bpy.app.version >= (3, 4, 0):
        if ".hide_poly" not in me.attributes:
            me.attributes.new(name=".hide_poly", type="BOOLEAN", domain="FACE")
        data = cast(bpy.types.BoolAttribute, me.attributes[".hide_poly"]).data
        data.foreach_get("value", polys_mask_hid)  # pyright: ignore[reportArgumentType]
    else:
        me.polygons.foreach_get("hide", polys_mask_hid)  # pyright: ignore[reportArgumentType]
    return ~polys_mask_hid


def normal_vector(me: bpy.types.Mesh) -> Float3DArray:
    """
    Retrieve normals of polygons.
    """
    poly_count = len(me.polygons)
    poly_normal = np.empty((poly_count, 3), "f")
    me.polygons.foreach_get("normal", poly_normal.reshape(-1))  # pyright: ignore[reportArgumentType]
    return poly_normal


def selection_mask(me: bpy.types.Mesh) -> Bool1DArray:
    """
    Retrieve a mask of selected polygons.
    """
    poly_count = len(me.polygons)
    polys_mask_sel = np.empty(poly_count, "?")
    if bpy.app.version >= (3, 4, 0):
        if ".select_poly" not in me.attributes:
            me.attributes.new(name=".select_poly", type="BOOLEAN", domain="FACE")
        data = cast(bpy.types.BoolAttribute, me.attributes[".select_poly"]).data
        data.foreach_get("value", polys_mask_sel)  # pyright: ignore[reportArgumentType]
    else:
        me.polygons.foreach_get("select", polys_mask_sel)  # pyright: ignore[reportArgumentType]
    return polys_mask_sel
