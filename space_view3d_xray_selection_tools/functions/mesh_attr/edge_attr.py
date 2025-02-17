from typing import cast

import bpy
import numpy as np

from ...types import Bool1DArray, Int2DArray


def vertex_indices(me: bpy.types.Mesh) -> Int2DArray:
    """
    Retrieve indices of edge vertices.
    """
    edge_count = len(me.edges)
    edge_vert_indices = np.empty((edge_count, 2), "i")
    if bpy.app.version >= (3, 6, 0):
        if ".edge_verts" not in me.attributes:
            me.attributes.new(name=".edge_verts", type="INT32_2D", domain="EDGE")
        data = cast(bpy.types.Int2Attribute, me.attributes[".edge_verts"]).data
        data.foreach_get("value", edge_vert_indices.reshape(-1))  # pyright: ignore[reportArgumentType]
    else:
        me.edges.foreach_get("vertices", edge_vert_indices.reshape(-1))  # pyright: ignore[reportArgumentType]
    return edge_vert_indices


def visibility_mask(me: bpy.types.Mesh) -> Bool1DArray:
    """
    Retrieve a mask of visible edges.
    """
    edge_count = len(me.edges)
    edges_mask_hid = np.empty(edge_count, "?")
    if bpy.app.version >= (3, 4, 0):
        if ".hide_edge" not in me.attributes:
            me.attributes.new(name=".hide_edge", type="BOOLEAN", domain="EDGE")
        data = cast(bpy.types.BoolAttribute, me.attributes[".hide_edge"]).data
        data.foreach_get("value", edges_mask_hid)  # pyright: ignore[reportArgumentType]
    else:
        me.edges.foreach_get("hide", edges_mask_hid)  # pyright: ignore[reportArgumentType]
    return ~edges_mask_hid


def selection_mask(me: bpy.types.Mesh) -> Bool1DArray:
    """
    Retrieve a mask of selected edges.
    """
    edge_count = len(me.edges)
    edges_mask_sel = np.empty(edge_count, "?")
    if bpy.app.version >= (3, 4, 0):
        if ".select_edge" not in me.attributes:
            me.attributes.new(name=".select_edge", type="BOOLEAN", domain="EDGE")
        data = cast(bpy.types.BoolAttribute, me.attributes[".select_edge"]).data
        data.foreach_get("value", edges_mask_sel)  # pyright: ignore[reportArgumentType]
    else:
        me.edges.foreach_get("select", edges_mask_sel)  # pyright: ignore[reportArgumentType]
    return edges_mask_sel
