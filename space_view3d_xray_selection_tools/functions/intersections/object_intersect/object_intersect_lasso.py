from itertools import compress
from typing import Literal

import bpy
import numpy as np

from ....types import Bool1DArray
from ... import geometry_tests
from . import object_intersect_shared


def _is_mesh_overlap_lasso(
    ob_eval: bpy.types.Object,
    me: bpy.types.Mesh,
    region: bpy.types.Region,
    rv3d: bpy.types.RegionView3D,
    lasso_poly: tuple[tuple[int, int], ...],
    check_faces: bool = False,
) -> bool:
    """
    Determine whether object data vertices overlap the selection region.

    Args:
        check_faces: Check for existence of faces having the selection region inside their area.
    """
    vert_co_2d = object_intersect_shared.get_vert_co_2d(me, ob_eval, region, rv3d)

    # One of the vertices lies inside the selection region.
    verts_mask_in_lasso = geometry_tests.points_inside_polygon_prefiltered(vert_co_2d, lasso_poly)
    if np.any(verts_mask_in_lasso):
        return True

    # One of the edges intersects the selection region.
    edge_vert_co_2d = object_intersect_shared.get_edge_vert_co_2d(me, vert_co_2d)
    edges_mask_isect_lasso = geometry_tests.segments_intersect_polygon_prefiltered(edge_vert_co_2d, lasso_poly)
    if np.any(edges_mask_isect_lasso):
        return True

    # One of the faces has a cursor inside their area.
    if check_faces:
        face_vert_co_2d, face_cell_starts, _face_cell_ends, face_loop_totals = (
            object_intersect_shared.get_face_vert_co_2d(me, vert_co_2d)
        )
        if face_loop_totals.size > 0:
            faces_mask_cursor_in = geometry_tests.point_inside_polygons_prefiltered(
                lasso_poly[0],
                face_vert_co_2d,
                face_cell_starts,
                face_loop_totals,
            )
            if np.any(faces_mask_cursor_in):
                return True

    return False


def _get_obs_mask_overlap_lasso(
    obs: list[bpy.types.Object],
    obs_mask_check: Bool1DArray,
    depsgraph: bpy.types.Depsgraph,
    region: bpy.types.Region,
    rv3d: bpy.types.RegionView3D,
    lasso_poly: tuple[tuple[int, int], ...],
    check_faces: bool = False,
) -> Bool1DArray:
    """
    Determine whether object data vertices overlap the selection region.

    Args:
        check_faces: Check for existence of faces having the selection region inside their area.
    """
    obs_to_check = compress(obs, obs_mask_check)
    bools: list[bool] = []

    for ob in obs_to_check:
        ob_eval = ob.evaluated_get(depsgraph)
        with object_intersect_shared.managed_mesh(ob_eval) as me:
            res = _is_mesh_overlap_lasso(ob_eval, me, region, rv3d, lasso_poly, check_faces)
        bools.append(res)

    return np.fromiter(bools, "?", len(bools))


def _is_mesh_in_lasso(
    ob_eval: bpy.types.Object,
    me: bpy.types.Mesh,
    region: bpy.types.Region,
    rv3d: bpy.types.RegionView3D,
    lasso_poly: tuple[tuple[int, int], ...],
) -> bool:
    """
    Determine whether all object data vertices lie fully within the selection region.
    """
    vert_co_2d = object_intersect_shared.get_vert_co_2d(me, ob_eval, region, rv3d)
    verts_mask_in_lasso = geometry_tests.points_inside_polygon_prefiltered(vert_co_2d, lasso_poly)
    return bool(np.all(verts_mask_in_lasso))


def _get_obs_mask_in_lasso(
    obs: list[bpy.types.Object],
    obs_mask_check: Bool1DArray,
    depsgraph: bpy.types.Depsgraph,
    region: bpy.types.Region,
    rv3d: bpy.types.RegionView3D,
    lasso_poly: tuple[tuple[int, int], ...],
):
    """
    Determine whether all object data vertices lie fully within the selection region.
    """
    obs_to_check = compress(obs, obs_mask_check)
    bools: list[bool] = []

    for ob in obs_to_check:
        ob_eval = ob.evaluated_get(depsgraph)
        with object_intersect_shared.managed_mesh(ob_eval) as me:
            res = _is_mesh_in_lasso(ob_eval, me, region, rv3d, lasso_poly)
        bools.append(res)

    return np.fromiter(bools, "?", len(bools))


def select_objects_in_lasso(
    context: bpy.types.Context,
    mode: Literal['SET', 'ADD', 'SUB', 'XOR', 'AND'],
    lasso_poly: tuple[tuple[int, int], ...],
    behavior: Literal['CONTAIN', 'OVERLAP'],
) -> None:
    """
    Select objects that intersect or lie within the selection region.

    Args:
        context: The Blender context.
        mode: The selection mode:
        lasso_poly: Coordinates (x, y) of the lasso vertices.
        behavior: Selection behavior.

    Returns:
        None
    """
    region = context.region
    rv3d = context.region_data
    depsgraph = context.evaluated_depsgraph_get()

    selectable_obs = context.selectable_objects
    mesh_obs, nonmesh_obs = object_intersect_shared.partition(
        selectable_obs, lambda o: o.type in {'MESH', 'CURVE', 'FONT'}
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

    # Objects with bounding box intersecting the selection circle.
    segments_mask_in = geometry_tests.segments_intersect_polygon(ob_2dbbox_segments, lasso_poly)
    segments_mask_in.shape = (mesh_ob_count, 4)
    obs_mask_2dbbox_isect_lasso = np.any(segments_mask_in, axis=1)

    # Objects with bounding box entirely inside the selection circle.
    points_mask_in = geometry_tests.points_inside_polygon(ob_2dbbox_points, lasso_poly)
    points_mask_in.shape = (mesh_ob_count, 4)
    obs_mask_2dbbox_entire_in_lasso = np.all(points_mask_in, axis=1)

    # Objects having bounding box under mouse cursor.
    obs_mask_cursor_in_2dbbox = geometry_tests.point_inside_rectangles(
        lasso_poly[0], ob_2dbbox_xmin, ob_2dbbox_xmax, ob_2dbbox_ymin, ob_2dbbox_ymax
    )

    # Skip tests on objects with an already known result.
    obs_mask_skip_check = obs_mask_2dbbox_entire_in_lasso | obs_mask_2dbbox_entire_clip

    match behavior:
        case 'OVERLAP':
            # Skip tests on objects with an already known result.
            # Tests on faces are expensive, perform them on as few objects as possible.
            obs_mask_check_verts_edges = obs_mask_2dbbox_isect_lasso & ~obs_mask_skip_check
            obs_mask_check_faces = obs_mask_cursor_in_2dbbox & ~obs_mask_2dbbox_isect_lasso & ~obs_mask_skip_check

            mesh_obs_mask_in_lasso = obs_mask_2dbbox_entire_in_lasso
            mesh_obs_mask_in_lasso[obs_mask_check_verts_edges] = _get_obs_mask_overlap_lasso(
                mesh_obs, obs_mask_check_verts_edges, depsgraph, region, rv3d, lasso_poly
            )
            mesh_obs_mask_in_lasso[obs_mask_check_faces] = _get_obs_mask_overlap_lasso(
                mesh_obs, obs_mask_check_faces, depsgraph, region, rv3d, lasso_poly, check_faces=True
            )
            object_intersect_shared.do_selection(mesh_obs_mask_in_lasso, mesh_obs, mode)

        case 'CONTAIN':
            # Skip tests on objects with an already known result.
            obs_mask_check = (
                obs_mask_2dbbox_isect_lasso | (obs_mask_cursor_in_2dbbox & ~obs_mask_2dbbox_isect_lasso)
            ) & ~obs_mask_skip_check

            # Intersection tests on object data vertices.
            # Object with all vertices inside the selection region.
            mesh_obs_mask_in_lasso = obs_mask_2dbbox_entire_in_lasso
            mesh_obs_mask_in_lasso[obs_mask_check] = _get_obs_mask_in_lasso(
                mesh_obs, obs_mask_check, depsgraph, region, rv3d, lasso_poly
            )
            object_intersect_shared.do_selection(mesh_obs_mask_in_lasso, mesh_obs, mode)

    # Intersection tests on origin only.
    nonmesh_ob_co_2d = object_intersect_shared.get_ob_loc_co_2d(nonmesh_obs, region, rv3d)
    nonmesh_obs_mask_in_lasso = geometry_tests.points_inside_polygon(nonmesh_ob_co_2d, lasso_poly)
    object_intersect_shared.do_selection(nonmesh_obs_mask_in_lasso, nonmesh_obs, mode)
