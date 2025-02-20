from collections.abc import Sequence
from itertools import compress
from typing import Literal

import bpy
import numpy as np

from ....types import Bool1DArray
from ... import geometry_tests
from . import object_intersect_shared


def _is_mesh_in_selbox(
    ob_eval: bpy.types.Object,
    me: bpy.types.Mesh,
    region: bpy.types.Region,
    rv3d: bpy.types.RegionView3D,
    xmin: int,
    xmax: int,
    ymin: int,
    ymax: int,
) -> bool:
    """
    Determine whether all object data vertices lie fully within the selection region.
    """
    vert_co_2d = object_intersect_shared.get_vert_co_2d(me, ob_eval, region, rv3d)
    verts_mask_in_selbox = geometry_tests.points_inside_rectangle(vert_co_2d, xmin, xmax, ymin, ymax)
    return bool(np.all(verts_mask_in_selbox))


def _get_obs_mask_in_selbox(
    obs: Sequence[bpy.types.Object],
    obs_mask_check: Bool1DArray,
    depsgraph: bpy.types.Depsgraph,
    region: bpy.types.Region,
    rv3d: bpy.types.RegionView3D,
    xmin: int,
    xmax: int,
    ymin: int,
    ymax: int,
) -> Bool1DArray:
    """
    Determine whether all object data vertices lie fully within the selection region.
    """
    obs_to_check = compress(obs, obs_mask_check)
    bools: list[bool] = []

    for ob in obs_to_check:
        ob_eval = ob.evaluated_get(depsgraph)
        with object_intersect_shared.managed_mesh(ob_eval) as me:
            res = _is_mesh_in_selbox(ob_eval, me, region, rv3d, xmin, xmax, ymin, ymax)
        bools.append(res)

    return np.fromiter(bools, "?", len(bools))


def select_objects_in_box(
    context: bpy.types.Context,
    mode: Literal['SET', 'ADD', 'SUB', 'XOR', 'AND'],
    xmin: int,
    xmax: int,
    ymin: int,
    ymax: int,
    behavior: Literal['ORIGIN', 'CONTAIN'],
) -> None:
    """
    Select objects that intersect or lie within the selection region.

    Args:
        context: The Blender context.
        mode: The selection mode:
        xmin: The selection tool to use:
        xmin: Minimum x-coordinates of the selection region.
        xmax: Maximum x-coordinates of the selection region.
        ymin: Minimum y-coordinates of the selection region.
        ymax: Maximum y-coordinates of the selection region.
        behavior: Selection behavior.

    Returns:
        None
    """
    region = context.region
    rv3d = context.region_data
    depsgraph = context.evaluated_depsgraph_get()

    selectable_obs = context.selectable_objects

    match behavior:
        case 'CONTAIN':
            mesh_obs, nonmesh_obs = object_intersect_shared.partition(
                selectable_obs, lambda ob: ob.type in {'MESH', 'CURVE', 'FONT'}
            )
            mesh_ob_count = len(mesh_obs)

            # Get coordinates of object's 2D bounding boxes.
            (
                ob_2dbbox_xmin,
                ob_2dbbox_xmax,
                ob_2dbbox_ymin,
                ob_2dbbox_ymax,
                ob_2dbbox_points,
                ob_2dbbox_segments,
                obs_mask_2dbbox_entire_clip,
            ) = object_intersect_shared.get_ob_2dbboxes(mesh_obs, mesh_ob_count, region, rv3d)

            # Objects with bounding box intersecting the selection box.
            segments_mask_in = geometry_tests.segments_intersect_rectangle(ob_2dbbox_segments, xmin, xmax, ymin, ymax)
            segments_mask_in.shape = (mesh_ob_count, 4)
            obs_mask_2dbbox_isect_selbox = np.any(segments_mask_in, axis=1)

            # Objects with bounding box entirely inside the selection box.
            points_mask_in = geometry_tests.points_inside_rectangle(ob_2dbbox_points, xmin, xmax, ymin, ymax)
            points_mask_in.shape = (mesh_ob_count, 4)
            obs_mask_2dbbox_entire_in_selbox = np.all(points_mask_in, axis=1)

            # Objects having bounding box under mouse cursor.
            obs_mask_cursor_in_2dbbox = geometry_tests.point_inside_rectangles(
                (xmin, ymin), ob_2dbbox_xmin, ob_2dbbox_xmax, ob_2dbbox_ymin, ob_2dbbox_ymax
            )

            # Skip tests on objects with an already known result.
            obs_mask_skip_check = obs_mask_2dbbox_entire_in_selbox | obs_mask_2dbbox_entire_clip
            obs_mask_check = (
                obs_mask_2dbbox_isect_selbox | (obs_mask_cursor_in_2dbbox & ~obs_mask_2dbbox_isect_selbox)
            ) & ~obs_mask_skip_check

            # Intersection tests on object data vertices.
            # Object with all vertices inside the selection region.
            mesh_obs_mask_in_selbox = obs_mask_2dbbox_entire_in_selbox
            mesh_obs_mask_in_selbox[obs_mask_check] = _get_obs_mask_in_selbox(
                mesh_obs, obs_mask_check, depsgraph, region, rv3d, xmin, xmax, ymin, ymax
            )

            # Intersection tests on origin only.
            nonmesh_ob_co_2d = object_intersect_shared.get_ob_loc_co_2d(nonmesh_obs, region, rv3d)
            nonmesh_obs_mask_in_selbox = geometry_tests.points_inside_rectangle(
                nonmesh_ob_co_2d, xmin, xmax, ymin, ymax
            )

            object_intersect_shared.do_selection(mesh_obs_mask_in_selbox, mesh_obs, mode)
            object_intersect_shared.do_selection(nonmesh_obs_mask_in_selbox, nonmesh_obs, mode)

        case 'ORIGIN':
            # Intersection tests on origin only.
            ob_co_2d = object_intersect_shared.get_ob_loc_co_2d(selectable_obs, region, rv3d)
            obs_mask_in_selbox = geometry_tests.points_inside_rectangle(ob_co_2d, xmin, xmax, ymin, ymax)
            object_intersect_shared.do_selection(obs_mask_in_selbox, selectable_obs, mode)
