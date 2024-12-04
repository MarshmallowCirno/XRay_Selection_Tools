import bpy
import numpy as np
from numpy.typing import NDArray


def vertex_indices(me: bpy.types.Mesh) -> NDArray[np.int32]:
    """
    Retrieve indices of edge vertices.
    """
    edge_count = len(me.edges)
    edge_vert_indices = np.empty(edge_count * 2, "i")
    if bpy.app.version >= (3, 6, 0):
        me.attributes.new(name=".edge_verts", type="INT", domain="EDGE")
        data = me.attributes[".edge_verts"].data
        data.foreach_get("value", edge_vert_indices)
    else:
        me.edges.foreach_get("vertices", edge_vert_indices)
    edge_vert_indices.shape = (edge_count, 2)
    return edge_vert_indices


def visibility_mask(me: bpy.types.Mesh) -> NDArray[np.bool_]:
    """
    Retrieve a mask of visible edges.
    """
    edge_count = len(me.edges)
    edges_mask_vis = np.empty(edge_count, "?")
    if bpy.app.version >= (3, 4, 0):
        me.attributes.new(name=".hide_edge", type="BOOLEAN", domain="EDGE")
        data = me.attributes[".hide_edge"].data
        data.foreach_get("value", edges_mask_vis)
    else:
        me.edges.foreach_get("hide", edges_mask_vis)
    edges_mask_vis = ~edges_mask_vis
    return edges_mask_vis


def selection_mask(me: bpy.types.Mesh) -> NDArray[np.bool_]:
    """
    Retrieve a mask of selected edges.
    """
    edge_count = len(me.edges)
    edges_mask_sel = np.zeros(edge_count, "?")
    if bpy.app.version >= (3, 4, 0):
        me.attributes.new(name=".select_edge", type="BOOLEAN", domain="EDGE")
        data = me.attributes[".select_edge"].data
        data.foreach_get("value", edges_mask_sel)
    else:
        me.edges.foreach_get("select", edges_mask_sel)
    return edges_mask_sel
