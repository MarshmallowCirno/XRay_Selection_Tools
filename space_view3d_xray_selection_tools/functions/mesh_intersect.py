from typing import Literal

from itertools import chain, compress
from operator import itemgetter, attrgetter

import bmesh
import bpy
import numpy as np
from bpy.types import Context
from mathutils import Vector

from ..functions.timer import time_section
from .polygon_tests import (
    circle_bbox,
    polygon_bbox,
    points_inside_rectangle,
    segments_completely_outside_rectangle,
    segments_intersect_rectangle,
    points_inside_circle,
    segments_inside_or_intersect_circle,
    points_inside_polygon,
    point_inside_polygons,
    segments_intersect_polygon,
)
from .view3d import get_co_world_of_ob, get_co_2d
from .selection import new_mesh_selection_mask
from ..mesh_attr import vert_attr, edge_attr, face_attr


def lookup_isin(array, lut):
    """Faster np.isin."""
    # https://stackoverflow.com/questions/67391617/faster-membership-test-numpy-isin-too-slow/67393797#67393797

    # size of lookup table
    bound = lut.size

    # pre-filter the invalid ranges and locate the value to check further
    mask = array < bound
    idx = np.where(mask)

    # correct the mask by using the very fast LUT
    mask[idx] = lut[array[idx]]
    return mask


def select_mesh_elems(
    context: Context,
    mode: Literal['SET', 'ADD', 'SUB', 'XOR', 'AND'],
    tool: Literal['BOX', 'CIRCLE', 'LASSO'],
    tool_co: list[int],
    select_all_edges: bool,
    select_all_faces: bool,
    select_backfacing: bool,
):
    box_xmin = box_xmax = box_ymin = box_ymax = center = radius = lasso = None
    vert_co = verts_mask_visin = vis_edges_mask_in = edge_count = edges_mask_visin = cam = eye_co_world = facing_vec_world = None

    match tool:
        case 'BOX':
            box_xmin, box_xmax, box_ymin, box_ymax = tool_co
        case 'CIRCLE':
            center, radius = tool_co
        case 'LASSO':
            lasso = tool_co
        case _:
            raise ValueError("Tool is invalid")

    scene = context.scene
    region = context.region
    sv3d = context.space_data
    rv3d = context.region_data

    # View vector
    match rv3d.view_perspective:
        case 'PERSP':
            eye = Vector(rv3d.view_matrix[2][:3])
            eye.length = rv3d.view_distance
            eye_co_world = rv3d.view_location + eye
        case 'CAMERA':
            cam = sv3d.camera if sv3d.use_local_camera else scene.camera
            eye_co_world = cam.matrix_world.translation
        case _:  # 'ORTHO'
            vec_z = Vector((0.0, 0.0, 1.0))
            facing_vec_world = rv3d.view_matrix.inverted().to_3x3() @ vec_z

    sel_obs = context.selected_objects if context.selected_objects else [context.object]
    for ob in sel_obs:
        if ob.type == 'MESH':
            # View vector
            match rv3d.view_perspective:
                case 'PERSP' | 'CAMERA':
                    eye_co_local = ob.matrix_world.inverted() @ eye_co_world
                case _:  # 'ORTHO'
                    eye_co_local = facing_vec_world @ ob.matrix_world

            mesh_select_mode = context.tool_settings.mesh_select_mode

            with time_section("Get mesh", prefix="\n>> BEGIN\n"):
                if bpy.app.version >= (3, 4, 0):
                    # noinspection PyTypeChecker
                    bm = bmesh.from_edit_mesh(ob.data)
                    me = bpy.data.meshes.new("xray_select_temp_mesh")
                    bm.to_mesh(me)
                else:
                    ob.update_from_editmode()
                    me = ob.data
                    # noinspection PyTypeChecker
                    bm = bmesh.from_edit_mesh(me)

            # VERTEX PASS
            if mesh_select_mode[0] or mesh_select_mode[1] or mesh_select_mode[2] and select_all_faces:
                verts = me.vertices
                vert_count = len(verts)

                with time_section("Get vertex attributes", prefix=">> VERTEX PASS\n"):
                    # Local coordinates of vertices.
                    vert_co_local = vert_attr.coordinates(me)

                    # Mask of visible vertices.
                    verts_mask_vis = vert_attr.visibility_mask(me)

                # Filter out backfacing.
                if (mesh_select_mode[0] or mesh_select_mode[1]) and not select_backfacing:
                    with time_section("Filter out vertex backfacing"):
                        vert_normal = vert_attr.normal_vector(me)

                        if rv3d.view_perspective == 'ORTHO' or rv3d.view_perspective == 'CAMERA' and cam.data.type == 'ORTHO':
                            verts_mask_facing = vert_normal @ eye_co_local > 0
                        else:
                            offset_vec = vert_co_local - eye_co_local
                            verts_mask_facing = np.einsum('ij,ij->i', vert_normal, offset_vec) < 0

                        verts_mask_vis &= verts_mask_facing

                with time_section("Calculate vertex 2d coordinates"):
                    # Local coordinates of visible vertices.
                    vis_vert_co_local = vert_co_local[verts_mask_vis]
                    # World coordinates of visible vertices.
                    vis_vert_co_world = get_co_world_of_ob(ob, vis_vert_co_local)
                    # 2d coordinates of visible vertices.
                    vert_co = np.full((vert_count, 2), np.nan, "f")
                    vert_co[verts_mask_vis] = vis_vert_co = get_co_2d(region, rv3d, vis_vert_co_world)

                with time_section("Calculate vertex intersection"):
                    # Mask of vertices inside the selection polygon from visible vertices.
                    match tool:
                        case 'BOX':
                            vis_verts_mask_in = points_inside_rectangle(vis_vert_co, box_xmin, box_xmax, box_ymin, box_ymax)
                        case 'CIRCLE':
                            vis_verts_mask_in = points_inside_circle(vis_vert_co, center, radius)
                        case 'LASSO':
                            vis_verts_mask_in = points_inside_polygon(vis_vert_co, lasso, prefilter=True)
                        case _:
                            raise ValueError("tool is invalid")

                    # Mask of visible vertices inside the selection polygon from all vertices.
                    verts_mask_visin = np.full(vert_count, False, "?")
                    verts_mask_visin[verts_mask_vis] = vis_verts_mask_in

                # Do selection.
                if mesh_select_mode[0]:
                    with time_section("Select vertices"):
                        cur_selection_mask = vert_attr.selection_mask(me)
                        new_selection_mask = new_mesh_selection_mask(cur_selection_mask, verts_mask_visin, mode)
                        update_mask = cur_selection_mask ^ new_selection_mask

                        update_list: list[bool] = update_mask.tolist()
                        state_list: list[bool] = new_selection_mask.tolist()

                        for v, state in compress(zip(bm.verts, state_list), update_list):
                            v.select = state

            # EDGE PASS
            if mesh_select_mode[1] or mesh_select_mode[2] and select_all_faces:
                edges = me.edges
                edge_count = len(edges)

                with time_section("Get edge attributes", prefix=">> EDGE PASS\n"):
                    # For each edge get 2 indices of its vertices.
                    edge_vert_indices = edge_attr.vertex_indices(me)

                    # Mask of visible edges.
                    edges_mask_vis = edge_attr.visibility_mask(me)

                with time_section("Calculate edge intersection"):
                    # For each visible edge get 2 vertex indices.
                    vis_edge_vert_indices = edge_vert_indices[edges_mask_vis]
                    # For each visible edge get mask of vertices in the selection polygon.
                    vis_edge_verts_mask_in = verts_mask_visin[vis_edge_vert_indices]

                    # Try to select edges that are completely inside the selection polygon.
                    if not select_all_edges:
                        # Mask of edges inside the selection polygon from visible edges.
                        vis_edges_mask_in = vis_edge_verts_mask_in[:, 0] & vis_edge_verts_mask_in[:, 1]

                    # If select_all_edges enabled or no inner edges found
                    # then select edges that intersect the selection polygon.
                    if (
                            select_all_edges
                            or (not select_all_edges and not np.any(vis_edges_mask_in))
                            or (mesh_select_mode[2] and select_all_faces)
                    ):

                        # Coordinates of vertices of visible edges.
                        vis_edge_vert_co = vert_co[vis_edge_vert_indices]

                        # Mask of edges from visible edges that have vertex inside the selection polygon and
                        # should be selected.
                        vis_edges_mask_vert_in = vis_edge_verts_mask_in[:, 0] | vis_edge_verts_mask_in[:, 1]

                        # Selection polygon bbox.
                        match tool:
                            case 'BOX':
                                xmin, xmax, ymin, ymax = box_xmin, box_xmax, box_ymin, box_ymax
                            case 'CIRCLE':
                                xmin, xmax, ymin, ymax = circle_bbox(center, radius)
                            case 'LASSO':
                                xmin, xmax, ymin, ymax = polygon_bbox(lasso)
                            case _:
                                raise ValueError("Tool is invalid")

                        # Mask of edges from visible edges that have verts both laying outside of one of sides
                        # of selection polygon bbox, so they can't intersect the selection polygon and
                        # shouldn't be selected.
                        vis_edges_mask_cant_isect = segments_completely_outside_rectangle(
                            vis_edge_vert_co, xmin, xmax, ymin, ymax)

                        # Mask of edges from visible edges that may intersect selection polygon and
                        # should be tested for intersection.
                        vis_edges_mask_may_isect = ~vis_edges_mask_vert_in & ~vis_edges_mask_cant_isect

                        # Skip if there is no edges that need to be tested for intersection.
                        if np.any(vis_edges_mask_may_isect):
                            # Get coordinates of verts of visible edges that may intersect the selection polygon.
                            may_isect_vis_edge_co = vis_edge_vert_co[vis_edges_mask_may_isect]

                            # Mask of edges that intersect the selection polygon from edges that may intersect it.
                            match tool:
                                case 'BOX':
                                    may_isect_vis_edges_mask_isect = segments_intersect_rectangle(
                                        may_isect_vis_edge_co, box_xmin, box_xmax, box_ymin, box_ymax)
                                case 'CIRCLE':
                                    may_isect_vis_edges_mask_isect = segments_inside_or_intersect_circle(
                                        may_isect_vis_edge_co, center, radius)
                                case 'LASSO':
                                    may_isect_vis_edges_mask_isect = segments_intersect_polygon(
                                        may_isect_vis_edge_co, lasso)
                                case _:
                                    raise ValueError("Tool is invalid")

                            # Mask of edges that intersect the selection polygon from visible edges.
                            vis_edges_mask_in = vis_edges_mask_vert_in
                            vis_edges_mask_in[vis_edges_mask_may_isect] = may_isect_vis_edges_mask_isect
                        else:
                            vis_edges_mask_in = vis_edges_mask_vert_in

                    # Mask of visible edges inside the selection polygon from all edges.
                    edges_mask_visin = np.full(edge_count, False, "?")
                    edges_mask_visin[edges_mask_vis] = vis_edges_mask_in

                # Do selection.
                if mesh_select_mode[1]:
                    with time_section("Select edges"):
                        cur_selection_mask = edge_attr.selection_mask(me)
                        new_selection_mask = new_mesh_selection_mask(cur_selection_mask, edges_mask_visin, mode)
                        update_mask = cur_selection_mask ^ new_selection_mask

                        update_list: list[bool] = update_mask.tolist()
                        state_list: list[bool] = new_selection_mask.tolist()

                        for e, state in compress(zip(bm.edges, state_list), update_list):
                            e.select = state

            # FACE PASS
            if mesh_select_mode[2]:
                faces = me.polygons
                face_count = len(faces)

                with time_section("Get face attributes", prefix=">> FACE PASS\n"):
                    # Get mask of visible faces.
                    faces_mask_vis = face_attr.visibility_mask(me)

                # Filter out backfacing.
                if not select_backfacing:
                    with time_section("Filter out face backfacing"):
                        face_normal = face_attr.normal_vector(me)

                        face_center_co_local = face_attr.center_coordinates(me)

                        if rv3d.view_perspective == 'ORTHO' or rv3d.view_perspective == 'CAMERA' and cam.data.type == 'ORTHO':
                            faces_mask_facing = face_normal @ eye_co_local > 0
                        else:
                            offset_vec = face_center_co_local - eye_co_local
                            faces_mask_facing = np.einsum('ij,ij->i', face_normal, offset_vec) < 0

                        faces_mask_vis &= faces_mask_facing

                # Select faces which centers are inside the selection rectangle.
                if not select_all_faces:
                    with time_section("Calculate faces centers intersection"):
                        # Local coordinates of face centers.
                        face_center_co_local = face_attr.center_coordinates(me)

                        # Local coordinates of visible face centers.
                        vis_face_center_co_local = face_center_co_local[faces_mask_vis]
                        # world coordinates of visible face centers.
                        vis_vert_co_world = get_co_world_of_ob(ob, vis_face_center_co_local)
                        # 2d coordinates of visible face centers.
                        vis_face_center_co = get_co_2d(region, rv3d, vis_vert_co_world)

                        # Mask of face centers inside the selection polygon from visible faces.
                        match tool:
                            case 'BOX':
                                vis_faces_mask_in = points_inside_rectangle(
                                    vis_face_center_co, box_xmin, box_xmax, box_ymin, box_ymax)
                            case 'CIRCLE':
                                vis_faces_mask_in = points_inside_circle(vis_face_center_co, center, radius)
                            case 'LASSO':
                                vis_faces_mask_in = points_inside_polygon(vis_face_center_co, lasso, prefilter=True)
                            case _:
                                raise ValueError("Tool is invalid")

                        # Mask of visible faces inside the selection polygon from all faces.
                        faces_mask_visin = np.full(face_count, False, "?")
                        faces_mask_visin[faces_mask_vis] = vis_faces_mask_in
                else:
                    with time_section("Calculate faces by verts and edges"):
                        # Number of vertices for each face.
                        face_loop_totals = face_attr.vertex_count(me)

                        # Skip getting faces from edges if there is no edges inside selection border.
                        in_edge_count = np.count_nonzero(edges_mask_visin)
                        if in_edge_count:
                            # Getting faces from bmesh is faster when a low number of faces need to be
                            # selected from a large number of total faces, otherwise numpy is faster.
                            ratio = edge_count / in_edge_count

                            if ratio > 5.9:
                                # Bmesh pass.
                                visin_edge_indices = np.nonzero(edges_mask_visin)[0].tolist()

                                # noinspection PyTypeChecker
                                visin_edges = itemgetter(*visin_edge_indices)(bm.edges)
                                visin_edges = (visin_edges,) if type(visin_edges) is not tuple else visin_edges

                                link_faces = map(attrgetter("link_faces"), visin_edges)
                                link_faces = set(chain.from_iterable(link_faces))

                                in_face_indices = map(attrgetter("index"), link_faces)

                                in_face_indices = np.fromiter(in_face_indices, "i")
                            else:
                                # Numpy pass.
                                # Indices of face edges.
                                loop_edge_indices = face_attr.edge_indices(me)

                                # Index of face for each edge in mesh loop.
                                face_indices = np.arange(face_count)
                                loop_face_indices = np.repeat(face_indices, face_loop_totals)

                                # Mask of visible edges in the selection polygon that are in mesh loops,
                                # therefore forming face polygons in the selection border.
                                loop_edges_mask_visin = lookup_isin(loop_edge_indices, edges_mask_visin)

                                # Indices of faces inside the selection polygon.
                                in_face_indices = np.unique(loop_face_indices[loop_edges_mask_visin])

                            # Mask of all faces in the selection polygon.
                            faces_mask_in = np.full(face_count, False, "?")
                            faces_mask_in[in_face_indices] = np.True_
                            # Mask of visible faces in the selection polygon.
                            faces_mask_visin = faces_mask_vis & faces_mask_in
                        else:
                            faces_mask_in = faces_mask_visin = np.full(face_count, False, "?")

                    with time_section("Calculate faces under cursor"):
                        # FACE POLY PASS ####
                        # Select faces under cursor (faces that have the selection polygon inside their area).

                        # Visible faces not in the selection polygon.
                        faces_mask_visnoin = ~faces_mask_in & faces_mask_vis

                        # Number of vertices of each visible face not in the selection polygon.
                        visnoin_face_loop_totals = face_loop_totals[faces_mask_visnoin]

                        # Skip if all faces are already selected.
                        if visnoin_face_loop_totals.size > 0:
                            match tool:
                                case 'BOX':
                                    cursor_co = (box_xmax, box_ymin)  # bottom right box corner
                                case 'CIRCLE':
                                    cursor_co = center
                                case 'LASSO':
                                    cursor_co = lasso[0]
                                case _:
                                    raise ValueError("Tool is invalid")

                            # Indices of vertices of all faces.
                            face_vert_indices = face_attr.vertex_indices(me)

                            # Mask of vertices not in the selection polygon from face vertices.
                            face_verts_mask_visnoin = np.repeat(faces_mask_visnoin, face_loop_totals)
                            # Indices of vertices of visible faces not in the selection polygon.
                            visnoin_face_vert_indices = face_vert_indices[face_verts_mask_visnoin]
                            # Coordinates of vertices of visible faces not in the selection polygon.
                            visnoin_face_vert_co = vert_co[visnoin_face_vert_indices]
                            # Index of first face vertex in face vertex sequence.
                            visnoin_face_cell_starts = np.insert(visnoin_face_loop_totals[:-1].cumsum(), 0, 0)

                            # Mask of faces that have cursor inside their polygon area.
                            # From visible faces not in the selection polygon.
                            visnoin_faces_mask_under = point_inside_polygons(
                                cursor_co, visnoin_face_vert_co, visnoin_face_cell_starts, None,
                                visnoin_face_loop_totals, prefilter=True)

                            # Mask of visible faces under cursor from all faces.
                            faces_mask_visunder = np.full(face_count, False, "?")
                            faces_mask_visunder[faces_mask_visnoin] = visnoin_faces_mask_under

                            # Mask of visible faces in the selection polygon and under cursor.
                            faces_mask_visin[faces_mask_visunder] = np.True_

                with time_section("Select faces"):
                    # Do selection.
                    cur_selection_mask = face_attr.selection_mask(me)
                    new_selection_mask = new_mesh_selection_mask(cur_selection_mask, faces_mask_visin, mode)
                    update_mask = cur_selection_mask ^ new_selection_mask

                    update_list: list[bool] = update_mask.tolist()
                    state_list: list[bool] = new_selection_mask.tolist()

                    for f, state in compress(zip(bm.faces, state_list), update_list):
                        f.select = state

            with time_section("Finalize", prefix=">> END\n"):
                if bpy.app.version >= (3, 4, 0):
                    bpy.data.meshes.remove(me, do_unlink=True)

                # Flush face selection after selecting/deselecting edges and vertices.
                bm.select_flush_mode()

                # noinspection PyTypeChecker
                bmesh.update_edit_mesh(ob.data, loop_triangles=False, destructive=False)
