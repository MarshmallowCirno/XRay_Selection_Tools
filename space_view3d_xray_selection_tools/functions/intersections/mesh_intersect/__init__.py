import dataclasses
import itertools
import operator
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, Literal, cast

import bmesh
import bpy
import mathutils
import numpy as np

from ....types import Bool1DArray, Float2DArray, Int1DArray
from ... import geometry_tests, timer, view3d_utils
from ...mesh_attr import edge_attr, loop_attr, poly_attr, vert_attr
from .. import selection_utils


def _lookup_isin(index_array: Int1DArray, lut: Bool1DArray) -> Bool1DArray:
    """Faster np.isin."""
    # https://stackoverflow.com/questions/67391617/faster-membership-test-numpy-isin-too-slow/67393797#67393797

    # Size of lookup table.
    bound = lut.size

    # Pre-filter the invalid ranges and locate the value to check further.
    mask = index_array < bound
    idx = np.where(mask)

    # Correct the mask by using the very fast LUT.
    mask[idx] = lut[index_array[idx]]
    return mask


@dataclasses.dataclass(frozen=True)
class _ToolCoordinates:
    box_xmin: int = 0
    box_xmax: int = 0
    box_ymin: int = 0
    box_ymax: int = 0
    circle_center: tuple[int, int] = (0, 0)
    circle_radius: int = 0
    lasso_poly: tuple[tuple[int, int], ...] = ()


def select_mesh_elements(
    context: bpy.types.Context,
    mode: Literal['SET', 'ADD', 'SUB', 'XOR', 'AND'],
    tool: Literal['BOX', 'CIRCLE', 'LASSO'],
    tool_co_kwargs: dict[str, Any],
    select_all_edges: bool,
    select_all_faces: bool,
    select_backfacing: bool,
) -> None:
    """
    Select mesh elements of selected objects that intersect or lie within the tool region.

    Args:
        context: The Blender context.
        mode: The selection mode.
        tool: The selection tool type to use.
        tool_co_kwargs: A dictionary of tool-specific coordinates or parameters. Expected keys depend on the tool used.
        select_all_edges: If True, include edges that are partially inside the selection area.
        select_all_faces: If True, include faces that are partially inside the selection area.
        select_backfacing: If True, include back-facing geometry in the selection.

    Returns:
        None
    """
    tool_co = _ToolCoordinates(**tool_co_kwargs)

    scene = context.scene
    region = context.region
    sv3d = context.space_data
    assert isinstance(sv3d, bpy.types.SpaceView3D)
    rv3d = context.region_data

    if TYPE_CHECKING:
        eye_co_world = cast(mathutils.Vector, None)
        eye_co_local = cast(mathutils.Vector, None)
        facing_vec_world = cast(mathutils.Vector, None)
        cam = cast(bpy.types.Object, None)
        verts_mask_visin = cast(Bool1DArray, None)
        edges_mask_visin = cast(Bool1DArray, None)
        vis_edges_mask_in = cast(Bool1DArray, None)
        vert_co = cast(Float2DArray, None)
        me: bpy.types.Mesh | None = None

    # View vector
    match rv3d.view_perspective:
        case 'PERSP':
            eye = mathutils.Vector(rv3d.view_matrix[2][:3])
            eye.length = rv3d.view_distance
            eye_co_world = rv3d.view_location + eye
        case 'CAMERA':
            cam = sv3d.camera if sv3d.use_local_camera else scene.camera
            assert isinstance(cam, bpy.types.Object)
            eye_co_world = cam.matrix_world.translation
        case 'ORTHO':
            vec_z = mathutils.Vector((0.0, 0.0, 1.0))
            facing_vec_world = rv3d.view_matrix.inverted().to_3x3() @ vec_z

    sel_obs = context.selected_objects if context.selected_objects else [context.object]
    for ob in sel_obs:
        assert isinstance(ob, bpy.types.Object)

        if ob.type == 'MESH':
            assert isinstance(ob.data, bpy.types.Mesh)

            # View vector
            match rv3d.view_perspective:
                case 'PERSP' | 'CAMERA':
                    eye_co_local = ob.matrix_world.inverted() @ eye_co_world
                case 'ORTHO':
                    eye_co_local = facing_vec_world @ ob.matrix_world

            mesh_select_mode = context.tool_settings.mesh_select_mode

            try:
                with timer.time_section("Retrieve mesh", prefix="\n>> BEGIN\n"):
                    if bpy.app.version >= (3, 4, 0):
                        bm = bmesh.from_edit_mesh(ob.data)
                        me = bpy.data.meshes.new("xray_select_temp_mesh")
                        bm.to_mesh(me)
                    else:
                        ob.update_from_editmode()
                        me = ob.data
                        bm = bmesh.from_edit_mesh(me)

                # VERTEX PASS
                if mesh_select_mode[0] or mesh_select_mode[1] or (mesh_select_mode[2] and select_all_faces):
                    verts = me.vertices
                    vert_count = len(verts)

                    with timer.time_section("Get vertex attributes", prefix=">> VERTEX PASS\n"):
                        # Local coordinates of vertices.
                        vert_co_local = vert_attr.coordinates(me)

                        # Mask of visible vertices.
                        verts_mask_vis = vert_attr.visibility_mask(me)

                    # Filter out backfacing.
                    if (mesh_select_mode[0] or mesh_select_mode[1]) and not select_backfacing:
                        with timer.time_section("Filter out vertex backfacing"):
                            vert_normal = vert_attr.normal_vector(me)

                            if (
                                rv3d.view_perspective == 'ORTHO'
                                or rv3d.view_perspective == 'CAMERA'
                                and cast(bpy.types.Camera, cam.data).type == 'ORTHO'
                            ):
                                verts_mask_facing = vert_normal @ eye_co_local[:] > 0
                            else:
                                offset_vec = vert_co_local - eye_co_local[:]
                                verts_mask_facing = np.einsum("ij,ij->i", vert_normal, offset_vec) < 0

                            verts_mask_vis &= verts_mask_facing

                    with timer.time_section("Calculate vertex 2d coordinates"):
                        # Local coordinates of visible vertices.
                        vis_vert_co_local = vert_co_local[verts_mask_vis]
                        # World coordinates of visible vertices.
                        vis_vert_co_world = view3d_utils.transform_local_to_world_co(ob.matrix_world, vis_vert_co_local)
                        # 2d coordinates of visible vertices.
                        vert_co = np.full((vert_count, 2), np.nan, "f")
                        vis_vert_co = view3d_utils.transform_world_to_2d_co(region, rv3d, vis_vert_co_world)[0]
                        vert_co[verts_mask_vis] = vis_vert_co

                    with timer.time_section("Calculate vertex intersection"):
                        # Mask of vertices inside the selection region from visible vertices.
                        match tool:
                            case 'BOX':
                                vis_verts_mask_in = geometry_tests.points_inside_rectangle(
                                    vis_vert_co, tool_co.box_xmin, tool_co.box_xmax, tool_co.box_ymin, tool_co.box_ymax
                                )
                            case 'CIRCLE':
                                vis_verts_mask_in = geometry_tests.points_inside_circle(
                                    vis_vert_co, tool_co.circle_center, tool_co.circle_radius
                                )
                            case 'LASSO':
                                vis_verts_mask_in = geometry_tests.points_inside_polygon_prefiltered(
                                    vis_vert_co, tool_co.lasso_poly
                                )

                        # Mask of visible vertices inside the selection region from all vertices.
                        verts_mask_visin = np.zeros(vert_count, "?")
                        verts_mask_visin[verts_mask_vis] = vis_verts_mask_in

                    # Do selection.
                    if mesh_select_mode[0]:
                        with timer.time_section("Select vertices"):
                            cur_selection_mask = vert_attr.selection_mask(me)
                            new_selection_mask = selection_utils.calculate_selection_mask(
                                cur_selection_mask, verts_mask_visin, mode
                            )
                            update_mask = cur_selection_mask ^ new_selection_mask

                            update_list: list[bool] = update_mask.tolist()
                            state_list: list[bool] = new_selection_mask.tolist()

                            for v, state in itertools.compress(zip(bm.verts, state_list), update_list):
                                v.select = state
                # EDGE PASS
                if mesh_select_mode[1] or (mesh_select_mode[2] and select_all_faces):
                    edges = me.edges
                    edge_count = len(edges)

                    with timer.time_section("Get edge attributes", prefix=">> EDGE PASS\n"):
                        # For each edge get 2 indices of its vertices.
                        edge_vert_indices = edge_attr.vertex_indices(me)

                        # Mask of visible edges.
                        edges_mask_vis = edge_attr.visibility_mask(me)

                    with timer.time_section("Calculate edge intersection"):
                        # For each visible edge get 2 vertex indices.
                        vis_edge_vert_indices = edge_vert_indices[edges_mask_vis]
                        # For each visible edge, get mask of vertices in the selection region.
                        vis_edge_verts_mask_in = verts_mask_visin[vis_edge_vert_indices]

                        # Try to select edges that are completely inside the selection region.
                        if not select_all_edges:
                            # Mask of edges inside the selection region from visible edges.
                            vis_edges_mask_in = vis_edge_verts_mask_in[:, 0] & vis_edge_verts_mask_in[:, 1]

                        # If select_all_edges enabled or no inner edges found,
                        # then select edges that intersect the selection region.
                        if (
                            select_all_edges
                            or (not select_all_edges and not np.any(vis_edges_mask_in))
                            or (mesh_select_mode[2] and select_all_faces)
                        ):
                            # Coordinates of vertices of visible edges.
                            vis_edge_vert_co = vert_co[vis_edge_vert_indices]

                            # Mask of edges from visible edges that have vertex inside the selection region and
                            # should be selected.
                            vis_edges_mask_vert_in = cast(
                                Bool1DArray,
                                vis_edge_verts_mask_in[:, 0] | vis_edge_verts_mask_in[:, 1],
                            )

                            # Selection region bbox.
                            match tool:
                                case 'BOX':
                                    xmin, xmax, ymin, ymax = (
                                        tool_co.box_xmin,
                                        tool_co.box_xmax,
                                        tool_co.box_ymin,
                                        tool_co.box_ymax,
                                    )
                                case 'CIRCLE':
                                    xmin, xmax, ymin, ymax = geometry_tests.circle_bbox(
                                        tool_co.circle_center, tool_co.circle_radius
                                    )
                                case 'LASSO':
                                    xmin, xmax, ymin, ymax = geometry_tests.polygon_bbox(tool_co.lasso_poly)

                            # A mask of edges from visible edges whose vertices are both located outside any
                            # side of the selection region's bounding box.
                            # These edges cannot intersect the selection region and should not be selected.
                            vis_edges_mask_cant_isect = geometry_tests.segments_on_same_rectangle_side(
                                vis_edge_vert_co, xmin, xmax, ymin, ymax
                            )

                            # Mask of edges from visible edges that may intersect the selection region and
                            # should be tested for intersection.
                            vis_edges_mask_may_isect = ~vis_edges_mask_vert_in & ~vis_edges_mask_cant_isect

                            # Skip if there are no edges that need to be tested for intersection.
                            if np.any(vis_edges_mask_may_isect):
                                # Get coordinates of verts of visible edges that may intersect the selection region.
                                may_isect_vis_edge_co = vis_edge_vert_co[vis_edges_mask_may_isect]

                                # Mask of edges that intersect the selection region from edges that may intersect it.
                                match tool:
                                    case 'BOX':
                                        may_isect_vis_edges_mask_isect = geometry_tests.segments_intersect_rectangle(
                                            may_isect_vis_edge_co,
                                            tool_co.box_xmin,
                                            tool_co.box_xmax,
                                            tool_co.box_ymin,
                                            tool_co.box_ymax,
                                        )
                                    case 'CIRCLE':
                                        may_isect_vis_edges_mask_isect = geometry_tests.segments_intersect_circle(
                                            may_isect_vis_edge_co, tool_co.circle_center, tool_co.circle_radius
                                        )
                                    case 'LASSO':
                                        may_isect_vis_edges_mask_isect = geometry_tests.segments_intersect_polygon(
                                            may_isect_vis_edge_co, tool_co.lasso_poly
                                        )

                                # Mask of edges that intersect the selection region from visible edges.
                                vis_edges_mask_in = vis_edges_mask_vert_in
                                vis_edges_mask_in[vis_edges_mask_may_isect] = may_isect_vis_edges_mask_isect
                            else:
                                vis_edges_mask_in = vis_edges_mask_vert_in

                        # Mask of visible edges inside the selection region from all edges.
                        edges_mask_visin = np.zeros(edge_count, "?")
                        edges_mask_visin[edges_mask_vis] = vis_edges_mask_in

                    # Do selection.
                    if mesh_select_mode[1]:
                        with timer.time_section("Select edges"):
                            cur_selection_mask = edge_attr.selection_mask(me)
                            new_selection_mask = selection_utils.calculate_selection_mask(
                                cur_selection_mask, edges_mask_visin, mode
                            )
                            update_mask = cur_selection_mask ^ new_selection_mask

                            update_list: list[bool] = update_mask.tolist()
                            state_list: list[bool] = new_selection_mask.tolist()

                            for e, state in itertools.compress(zip(bm.edges, state_list), update_list):
                                e.select = state

                # FACE PASS
                if mesh_select_mode[2]:
                    faces = me.polygons
                    face_count = len(faces)

                    with timer.time_section("Get face attributes", prefix=">> FACE PASS\n"):
                        # Get mask of visible faces.
                        faces_mask_vis = poly_attr.visibility_mask(me)

                    # Filter out backfacing.
                    if not select_backfacing:
                        with timer.time_section("Filter out face backfacing"):
                            face_normal = poly_attr.normal_vector(me)

                            face_center_co_local = poly_attr.center_coordinates(me)

                            if (
                                rv3d.view_perspective == 'ORTHO'
                                or rv3d.view_perspective == 'CAMERA'
                                and cast(bpy.types.Camera, cam.data).type == 'ORTHO'
                            ):
                                faces_mask_facing = face_normal @ eye_co_local[:] > 0
                            else:
                                offset_vec = face_center_co_local - eye_co_local[:]
                                faces_mask_facing = np.einsum("ij,ij->i", face_normal, offset_vec) < 0

                            faces_mask_vis &= faces_mask_facing

                    # Select faces which centers are inside the selection region.
                    if not select_all_faces:
                        with timer.time_section("Calculate faces centers intersection"):
                            # Local coordinates of face centers.
                            face_center_co_local = poly_attr.center_coordinates(me)

                            # Local coordinates of visible face centers.
                            vis_face_center_co_local = face_center_co_local[faces_mask_vis]
                            # world coordinates of visible face centers.
                            vis_vert_co_world = view3d_utils.transform_local_to_world_co(
                                ob.matrix_world, vis_face_center_co_local
                            )
                            # 2d coordinates of visible face centers.
                            vis_face_center_co = view3d_utils.transform_world_to_2d_co(region, rv3d, vis_vert_co_world)[
                                0
                            ]

                            # Mask of face centers inside the selection region from visible faces.
                            match tool:
                                case 'BOX':
                                    vis_faces_mask_in = geometry_tests.points_inside_rectangle(
                                        vis_face_center_co,
                                        tool_co.box_xmin,
                                        tool_co.box_xmax,
                                        tool_co.box_ymin,
                                        tool_co.box_ymax,
                                    )
                                case 'CIRCLE':
                                    vis_faces_mask_in = geometry_tests.points_inside_circle(
                                        vis_face_center_co, tool_co.circle_center, tool_co.circle_radius
                                    )
                                case 'LASSO':
                                    vis_faces_mask_in = geometry_tests.points_inside_polygon_prefiltered(
                                        vis_face_center_co, tool_co.lasso_poly
                                    )

                            # Mask of visible faces inside the selection region from all faces.
                            faces_mask_visin = np.zeros(face_count, "?")
                            faces_mask_visin[faces_mask_vis] = vis_faces_mask_in
                    else:
                        with timer.time_section("Calculate faces by edges"):
                            # Number of vertices for each face.
                            face_loop_totals = poly_attr.vertex_count(me)

                            # Skip calculating faces from edges if there is no edges inside selection region.
                            in_edge_count = np.count_nonzero(edges_mask_visin)
                            if in_edge_count:
                                # Retrieving faces from bmesh is faster when a low number of faces need to be
                                # selected from a large number of total faces,
                                # otherwise numpy is faster.
                                edge_count = len(me.edges)
                                ratio = edge_count / in_edge_count

                                if ratio > 5.9:
                                    # Bmesh pass.
                                    # Indices of visible edges inside the selection region.
                                    visin_edge_indices: list[int] = np.nonzero(edges_mask_visin)[0].tolist()

                                    # Visible edges inside the selection region.
                                    visin_edges_: tuple[bmesh.types.BMEdge, ...] | bmesh.types.BMEdge = (
                                        operator.itemgetter(
                                            *visin_edge_indices,
                                        )(bm.edges)
                                    )
                                    # itemgetter return-type is not consistent
                                    visin_edges: tuple[bmesh.types.BMEdge, ...] = (
                                        visin_edges_ if isinstance(visin_edges_, tuple) else (visin_edges_,)
                                    )

                                    # Faces per visible edge inside the selection region.
                                    visin_edge_faces: Iterator[tuple[bmesh.types.BMFace, ...]] = map(
                                        operator.attrgetter("link_faces"), visin_edges
                                    )
                                    # Faces inside the selection region.
                                    in_faces: set[bmesh.types.BMFace] = set(
                                        itertools.chain.from_iterable(visin_edge_faces)
                                    )

                                    # Indices of faces inside the selection region.
                                    in_face_indices_it: Iterator[int] = map(operator.attrgetter("index"), in_faces)
                                    in_face_indices = np.fromiter(in_face_indices_it, "i")
                                else:
                                    # Numpy pass.
                                    # Indices of face edges.
                                    loop_edge_indices: Int1DArray = loop_attr.edge_indices(me)

                                    # Index of face for each edge in mesh loop.
                                    face_indices: Int1DArray = np.arange(face_count)
                                    loop_face_indices: Int1DArray = np.repeat(face_indices, face_loop_totals)

                                    # Mask of visible edges in the selection region that are part of mesh loops,
                                    # therefore forming face polygons in the selection region.
                                    loop_edges_mask_visin = _lookup_isin(loop_edge_indices, edges_mask_visin)

                                    # Indices of faces inside the selection region.
                                    in_face_indices = np.unique(loop_face_indices[loop_edges_mask_visin])

                                # Mask of all faces in the selection region.
                                faces_mask_in = np.zeros(face_count, "?")
                                faces_mask_in[in_face_indices] = np.True_
                                # Mask of visible faces in the selection region.
                                faces_mask_visin = faces_mask_vis & faces_mask_in
                            else:
                                faces_mask_in = faces_mask_visin = np.zeros(face_count, "?")

                        with timer.time_section("Calculate faces under cursor"):
                            # Select faces under the cursor (faces that have the selection region inside their area).

                            # Visible faces not in the selection region.
                            faces_mask_visnoin = ~faces_mask_in & faces_mask_vis

                            # Number of vertices of each visible face not in the selection region.
                            visnoin_face_loop_totals = face_loop_totals[faces_mask_visnoin]

                            # Skip if all faces are already selected.
                            if visnoin_face_loop_totals.size > 0:
                                match tool:
                                    case 'BOX':
                                        cursor_co = (tool_co.box_xmax, tool_co.box_ymin)  # bottom right box corner
                                    case 'CIRCLE':
                                        cursor_co = tool_co.circle_center
                                    case 'LASSO':
                                        cursor_co = tool_co.lasso_poly[0]

                                # Indices of vertices of all faces.
                                face_vert_indices = loop_attr.vertex_indices(me)

                                # Mask of vertices not in the selection region from face vertices.
                                face_verts_mask_visnoin = np.repeat(faces_mask_visnoin, face_loop_totals)
                                # Indices of vertices of visible faces not in the selection region.
                                visnoin_face_vert_indices = face_vert_indices[face_verts_mask_visnoin]
                                # Coordinates of vertices of visible face vertices not in the selection region.
                                visnoin_face_vert_co = vert_co[visnoin_face_vert_indices]
                                # Index of first face vertex in a face vertex sequence.
                                cumsum: Int1DArray = visnoin_face_loop_totals.cumsum()
                                visnoin_face_cell_starts = np.insert(cumsum[:-1], 0, 0)

                                # Mask of faces that have cursor inside their polygon area.
                                # From visible faces not in the selection region.
                                visnoin_faces_mask_under = geometry_tests.point_inside_polygons_prefiltered(
                                    cursor_co,
                                    visnoin_face_vert_co,
                                    visnoin_face_cell_starts,
                                    visnoin_face_loop_totals,
                                )

                                # Mask of visible faces under cursor from all faces.
                                faces_mask_visunder = np.zeros(face_count, "?")
                                faces_mask_visunder[faces_mask_visnoin] = visnoin_faces_mask_under

                                # Mask of visible faces in the selection region and under the cursor.
                                faces_mask_visin[faces_mask_visunder] = np.True_

                    with timer.time_section("Select faces"):
                        # Do selection.
                        cur_selection_mask = poly_attr.selection_mask(me)
                        new_selection_mask = selection_utils.calculate_selection_mask(
                            cur_selection_mask, faces_mask_visin, mode
                        )
                        update_mask = cur_selection_mask ^ new_selection_mask

                        update_list: list[bool] = update_mask.tolist()
                        state_list: list[bool] = new_selection_mask.tolist()

                        for f, state in itertools.compress(zip(bm.faces, state_list), update_list):
                            f.select = state

                with timer.time_section("Finalize", prefix=">> END\n"):
                    # Flush face selection after selecting/deselecting edges and vertices.
                    bm.select_flush_mode()
                    bmesh.update_edit_mesh(ob.data, loop_triangles=False, destructive=False)

            finally:
                if bpy.app.version >= (3, 4, 0):
                    if me is not None:
                        bpy.data.meshes.remove(me, do_unlink=True)
