from typing import cast

import bpy
import numpy as np

from ...types import Int1DArray


def vertex_indices(me: bpy.types.Mesh) -> Int1DArray:
    """
    Retrieve indices of loop vertices.
    """
    loop_count = len(me.loops)
    loop_vert_indices = np.empty(loop_count, "i")
    if bpy.app.version >= (3, 6, 0):
        if ".corner_vert" not in me.attributes:
            me.attributes.new(name=".corner_vert", type="INT", domain="CORNER")
        data = cast(bpy.types.IntAttribute, me.attributes[".corner_vert"]).data
        data.foreach_get("value", loop_vert_indices)  # pyright: ignore[reportArgumentType]
    else:
        me.loops.foreach_get("vertex_index", loop_vert_indices)  # pyright: ignore[reportArgumentType]
    return loop_vert_indices


def edge_indices(me: bpy.types.Mesh) -> Int1DArray:
    """
    Retrieve indices of loop edges.
    """
    loop_count = len(me.loops)
    loop_edge_indices = np.empty(loop_count, "i")
    if bpy.app.version >= (3, 6, 0):
        if ".corner_edge" not in me.attributes:
            me.attributes.new(name=".corner_edge", type="INT", domain="CORNER")
        data = cast(bpy.types.IntAttribute, me.attributes[".corner_edge"]).data
        data.foreach_get("value", loop_edge_indices)  # pyright: ignore[reportArgumentType]
    else:
        me.loops.foreach_get("edge_index", loop_edge_indices)  # pyright: ignore[reportArgumentType]
    return loop_edge_indices
