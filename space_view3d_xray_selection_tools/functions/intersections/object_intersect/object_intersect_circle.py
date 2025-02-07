from itertools import compress

import numpy as np

from ... import geometry_tests
from . import object_intersect_shared


def _get_obs_mask_overlap_selcircle(obs, obs_mask_check, depsgraph, region, rv3d, center, radius, check_faces=False):
    list_of_obs_to_check = compress(obs, obs_mask_check)
    bool_list = []

    for ob in list_of_obs_to_check:
        ob_eval = ob.evaluated_get(depsgraph)
        me = ob_eval.to_mesh(preserve_all_data_layers=False, depsgraph=None)
        vert_co_2d = object_intersect_shared.get_vert_co_2d(me, ob_eval, region, rv3d)
        verts_mask_in_selcircle = geometry_tests.points_inside_circle(vert_co_2d, center, radius)
        if np.any(verts_mask_in_selcircle):
            bool_list.append(True)
        else:
            edge_vert_co_2d = object_intersect_shared.get_edge_vert_co_2d(me, vert_co_2d)
            edges_mask_isect_selcircle = geometry_tests.segments_intersect_circle_prefiltered(
                edge_vert_co_2d, center, radius
            )
            if np.any(edges_mask_isect_selcircle):
                bool_list.append(True)
            else:
                if check_faces:
                    face_vert_co_2d, face_cell_starts, face_cell_ends, face_loop_totals = (
                        object_intersect_shared.get_face_vert_co_2d(me, vert_co_2d)
                    )
                    if face_loop_totals.size > 0:
                        faces_mask_cursor_in = geometry_tests.point_inside_polygons_prefiltered(
                            center, face_vert_co_2d, face_cell_starts, face_loop_totals
                        )
                        bool_list.append(np.any(faces_mask_cursor_in))
                    else:
                        bool_list.append(False)
                else:
                    bool_list.append(False)
        ob_eval.to_mesh_clear()

    bools = np.fromiter(bool_list, "?", len(bool_list))
    return bools


def _get_obs_mask_in_selcircle(obs, obs_mask_check, depsgraph, region, rv3d, center, radius):
    list_of_obs_to_check = compress(obs, obs_mask_check)
    bool_list = []

    for ob in list_of_obs_to_check:
        ob_eval = ob.evaluated_get(depsgraph)
        me = ob_eval.to_mesh(preserve_all_data_layers=False, depsgraph=None)
        vert_co_2d = object_intersect_shared.get_vert_co_2d(me, ob_eval, region, rv3d)
        verts_mask_in_selcircle = geometry_tests.points_inside_circle(vert_co_2d, center, radius)
        if np.all(verts_mask_in_selcircle):
            bool_list.append(True)
        else:
            bool_list.append(False)
        ob_eval.to_mesh_clear()

    bools = np.fromiter(bool_list, "?", len(bool_list))
    return bools


def select_obs_in_circle(context, mode, center, radius, behavior):
    region = context.region
    rv3d = context.region_data
    depsgraph = context.evaluated_depsgraph_get()

    selectable_obs = context.selectable_objects
    mesh_obs, nonmesh_obs = object_intersect_shared.partition(
        selectable_obs, lambda o: o.type in {'MESH', 'CURVE', 'FONT'}
    )
    mesh_ob_count = len(mesh_obs)

    # Get coordinates of 2d bounding boxes of objects.
    (
        ob_2dbbox_xmin,
        ob_2dbbox_xmax,
        ob_2dbbox_ymin,
        ob_2dbbox_ymax,
        ob_2dbbox_points,
        ob_2dbbox_segments,
        obs_mask_2dbbox_entire_clip,
    ) = object_intersect_shared.get_ob_2dbboxes(mesh_obs, mesh_ob_count, region, rv3d)

    # Check for bounding boxes intersections with selection circle.
    # Speed up finding overlaps or intersections by doing polygon tests on bounding boxes.

    # Ob bbox intersects selection circle.
    segment_bools = geometry_tests.segments_intersect_circle(ob_2dbbox_segments, center, radius).reshape(
        (mesh_ob_count, 4)
    )
    obs_mask_2dbbox_isect_selcircle = np.any(segment_bools, axis=1)

    # Ob bbox entirely inside selection circle.
    point_bools = geometry_tests.points_inside_circle(ob_2dbbox_points, center, radius).reshape((mesh_ob_count, 4))
    obs_mask_2dbbox_entire_in_selcircle = np.all(point_bools, axis=1)

    # Cursor is inside ob bbox.
    obs_mask_cursor_in_2dbbox = geometry_tests.point_inside_rectangles(
        center, ob_2dbbox_xmin, ob_2dbbox_xmax, ob_2dbbox_ymin, ob_2dbbox_ymax
    )

    obs_mask_dont_check = obs_mask_2dbbox_entire_in_selcircle | obs_mask_2dbbox_entire_clip

    if behavior == 'OVERLAP':
        obs_mask_check_verts_edges = obs_mask_2dbbox_isect_selcircle & ~obs_mask_dont_check
        obs_mask_check_faces = obs_mask_cursor_in_2dbbox & ~obs_mask_2dbbox_isect_selcircle & ~obs_mask_dont_check

        mesh_obs_mask_in_selcircle = obs_mask_2dbbox_entire_in_selcircle
        mesh_obs_mask_in_selcircle[obs_mask_check_verts_edges] = _get_obs_mask_overlap_selcircle(
            mesh_obs, obs_mask_check_verts_edges, depsgraph, region, rv3d, center, radius
        )
        mesh_obs_mask_in_selcircle[obs_mask_check_faces] = _get_obs_mask_overlap_selcircle(
            mesh_obs, obs_mask_check_faces, depsgraph, region, rv3d, center, radius, check_faces=True
        )
        object_intersect_shared.do_selection(mesh_obs_mask_in_selcircle, mesh_obs, mode)

    else:
        obs_mask_check = (
            obs_mask_2dbbox_isect_selcircle | (obs_mask_cursor_in_2dbbox & ~obs_mask_2dbbox_isect_selcircle)
        ) & ~obs_mask_dont_check

        mesh_obs_mask_in_selcircle = obs_mask_2dbbox_entire_in_selcircle
        mesh_obs_mask_in_selcircle[obs_mask_check] = _get_obs_mask_in_selcircle(
            mesh_obs, obs_mask_check, depsgraph, region, rv3d, center, radius
        )
        object_intersect_shared.do_selection(mesh_obs_mask_in_selcircle, mesh_obs, mode)

    nonmesh_obs_co_2d = object_intersect_shared.get_ob_loc_co_2d(nonmesh_obs, region, rv3d)
    nonmesh_obs_mask_in_selcircle = geometry_tests.points_inside_circle(nonmesh_obs_co_2d, center, radius)
    object_intersect_shared.do_selection(nonmesh_obs_mask_in_selcircle, nonmesh_obs, mode)
