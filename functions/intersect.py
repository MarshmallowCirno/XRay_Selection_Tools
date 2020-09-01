import bmesh
import numpy as np


def get_co_2d(region, rv3d, ob, co_local):
    # https://blender.stackexchange.com/questions/6155/how-to-convert-coordinates-from-vertex-to-world-space # noqa
    # \scripts\modules\bpy_extras\view3d_utils.py location_3d_to_region_2d
    """Get 2D coordinates of points"""
    shape = co_local.shape[0]
    # get global_co
    mat_world = np.array(ob.matrix_world)
    mat = mat_world[:3, :3].T  # rotates backwards without T
    loc = mat_world[:3, 3]
    co_global = co_local @ mat + loc
    # bpy_extras.view3d_utils import location_3d_to_region_2d
    # get projection
    rv3d_mat = np.array(rv3d.perspective_matrix)
    co_global_4d = np.column_stack([co_global, np.ones((shape, 1), "f")])
    prj = (rv3d_mat @ co_global_4d.T).T
    # get 2d co
    width_half = region.width / 2.0
    height_half = region.height / 2.0

    prj_w = prj[:, 3]  # negative if coord is behind the origin of a perspective view
    co_2d = np.empty((shape, 3), "f")
    co_2d[:, 0] = width_half + width_half * (prj[:, 0] / prj_w)
    co_2d[:, 1] = height_half + height_half * (prj[:, 1] / prj_w)
    co_2d[:, 2] = prj_w
    return co_2d


def point_inside_rectangles(co, xmin, xmax, ymin, ymax):
    """Return a boolean mask of rectangles that have a single given point inside their area"""
    x, y = co
    with np.errstate(invalid="ignore"):
        return (xmin < x) & (x < xmax) & \
               (ymin < y) & (y < ymax)


def points_inside_rectangle(co, xmin, xmax, ymin, ymax):
    """Return a boolean mask of points that inside a border of selection rectangle"""
    x = co[:, 0]
    y = co[:, 1]
    with np.errstate(invalid="ignore"):
        return (xmin < x) & (x < xmax) & \
               (ymin < y) & (y < ymax)


def segments_intersect_rectangle(segment_co, xmin, xmax, ymin, ymax):
    """Check if points are completely outside the rectangle,
        both laying outside of one of its side. Then do simple check for lines intersecting.
        Return a boolean mask of segments that intersect a selection rectangle"""
    # https://github.com/dfelinto/blender/blob/master/source/blender/editors/space_view3d/view3d_select.c # noqa
    v1x = segment_co[:, 0, 0]
    v1y = segment_co[:, 0, 1]
    v2x = segment_co[:, 1, 0]
    v2y = segment_co[:, 1, 1]

    dx0 = v2x - v1x
    dy0 = v1y - v2y

    dx1 = v1x - xmin
    dx2 = v1x - xmax
    dy1 = v1y - ymin
    dy2 = v1y - ymax

    d1 = dy0 * dx1 + dx0 * dy1
    d2 = dy0 * dx1 + dx0 * dy2
    d3 = dy0 * dx2 + dx0 * dy2
    d4 = dy0 * dx2 + dx0 * dy1

    with np.errstate(invalid="ignore"):
        not_intersect = np.isnan(v1x) | np.isnan(v2x) | \
                        (v1x < xmin) & (v2x < xmin) | \
                        (v1x > xmax) & (v2x > xmax) | \
                        (v1y < ymin) & (v2y < ymin) | \
                        (v1y > ymax) & (v2y > ymax) | \
                        ((d1 < 0) & (d2 < 0) & (d3 < 0) & (d4 < 0)) | \
                        ((d1 > 0) & (d2 > 0) & (d3 > 0) & (d4 > 0))
    return ~not_intersect


def segments_outside_polygon_bbox(segment_co, poly):
    """Return a boolean mask of segments that lie outside polygon bounding box"""
    poly = np.array(poly, "f")
    xmin = np.amin(poly[:, 0])
    xmax = np.amax(poly[:, 0])
    ymin = np.amin(poly[:, 1])
    ymax = np.amax(poly[:, 1])

    v1x = segment_co[:, 0, 0]
    v1y = segment_co[:, 0, 1]
    v2x = segment_co[:, 1, 0]
    v2y = segment_co[:, 1, 1]

    with np.errstate(invalid="ignore"):
        return np.isnan(v1x) | np.isnan(v2x) | \
               (v1x < xmin) & (v2x < xmin) | \
               (v1x > xmax) & (v2x > xmax) | \
               (v1y < ymin) & (v2y < ymin) | \
               (v1y > ymax) & (v2y > ymax)


def point_inside_polygons(co, polygon_vertices_co, poly_cell_start, poly_cell_end):
    """Return a boolean mask of polygons that have a single given point inside their area"""

    # get coordinates of verts to calculate intersections
    # [0, 1, 2, 3], [0, 1, 2, 3, 4], [0, 1, 2] polygons example
    # [0, 1, 2, 3, 0, 1, 2, 3, 4, 0, 1, 2] p1 indices example
    # [0, 1, 2, 4, 0, 1, 2, 3, 2, 0, 1, 3] p2 indices example after replace
    # [3, 0, 1, 2, 4, 0, 1, 2, 3, 2, 0, 1] p2 indices example after roll
    # for example:
    # p2[3] = p1[8]
    # p2[8] = p1[11]
    # p2[11] = p1[3]
    # then roll

    mask1 = poly_cell_end
    mask2 = np.roll(mask1, 1)

    p1 = polygon_vertices_co
    p2 = p1.copy()
    p2[mask2] = p1[mask1]
    p2 = np.roll(p2, 1, axis=0)

    x, y = co
    p1x = p1[:, 0]
    p1y = p1[:, 1]
    p2x = p2[:, 0]
    p2y = p2[:, 1]

    # https://en.wikipedia.org/wiki/Even–odd_rule
    vert_odd_even = ((p1y > y) != (p2y > y)) & (x < p1x + (p2x - p1x) * (y - p1y) / (p2y - p1y))
    poly_odd_even = np.add.reduceat(vert_odd_even, poly_cell_start)
    mask_inside_poly = poly_odd_even % 2 == 1
    return mask_inside_poly


def points_inside_polygon(co, poly):
    """Return a boolean mask of points that lie within a single given polygon"""
    # https://stackoverflow.com/questions/36399381/whats-the-fastest-way-of-checking-if-a-point-is-inside-a-polygon-in-python # noqa
    n = len(poly)
    x = co[:, 0]
    y = co[:, 1]
    inside = np.full(len(x), False, "?")
    p1x, p1y = poly[0]
    xints = 0.0
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        with np.errstate(invalid="ignore"):
            idx = np.nonzero((y > min(p1y, p2y)) &
                             (y <= max(p1y, p2y)) &
                             (x <= max(p1x, p2x)))[0]
        if p1y != p2y:
            xints = (y[idx] - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
        if p1x == p2x:
            inside[idx] = ~inside[idx]
        else:
            if idx.size > 0:
                idxx = idx[x[idx] <= xints]
                inside[idxx] = ~inside[idxx]

        p1x, p1y = p2x, p2y
    return inside


def segments_intersect_polygon(segment_co, poly):
    v1x = segment_co[:, 0, 0]
    v1y = segment_co[:, 0, 1]
    v2x = segment_co[:, 1, 0]
    v2y = segment_co[:, 1, 1]

    loop_sides = len(poly)
    j = loop_sides - 1
    intersections = []

    for i in range(loop_sides):
        s1x = poly[i][0]
        s1y = poly[i][1]
        s2x = poly[j][0]
        s2y = poly[j][1]

        dx0 = v2x - v1x
        dx1 = s2x - s1x
        dy0 = v2y - v1y
        dy1 = s2y - s1y

        d1 = dy1 * (s2x - v1x) - dx1 * (s2y - v1y)
        d2 = dy1 * (s2x - v2x) - dx1 * (s2y - v2y)
        d3 = dy0 * (v2x - s1x) - dx0 * (v2y - s1y)
        d4 = dy0 * (v2x - s2x) - dx0 * (v2y - s2y)

        intersect = (d1 * d2 <= 0) & (d3 * d4 <= 0)
        intersections.append(intersect)
        j = i

    intersections = np.array(intersections, "?")
    intersections.shape = (loop_sides, v1x.size)
    return np.any(intersections.T, axis=1)


def segments_intersect_polygon_broadcast(segment_co, poly):
    poly = np.array(poly, "f")
    v1x = segment_co[:, 0, 0]
    v1y = segment_co[:, 0, 1]
    v2x = segment_co[:, 1, 0]
    v2y = segment_co[:, 1, 1]

    poly1 = poly
    poly2 = np.roll(poly, 2)

    p1x = poly1[:, 0][:, None]
    p1y = poly1[:, 1][:, None]
    p2x = poly2[:, 0][:, None]
    p2y = poly2[:, 1][:, None]

    # vectors
    dx0 = v2x - v1x
    dx1 = p2x - p1x
    dy0 = v2y - v1y
    dy1 = p2y - p1y

    d1 = dy1 * (p2x - v1x) - dx1 * (p2y - v1y)
    d2 = dy1 * (p2x - v2x) - dx1 * (p2y - v2y)
    d3 = dy0 * (v2x - p1x) - dx0 * (v2y - p1y)
    d4 = dy0 * (v2x - p2x) - dx0 * (v2y - p2y)

    intersections = (d1 * d2 <= 0) & (d3 * d4 <= 0)
    return np.any(intersections.T, axis=1)


def get_selection_mask(elem, shape, inside_mask, mode):
    # https://stackoverflow.com/questions/33384529/difference-between-numpy-logical-and-and
    if mode == 'SET':
        select = inside_mask
    elif mode == 'ADD':
        select = np.zeros(shape, "?")
        elem.foreach_get("select", select)
        select = select | inside_mask
    elif mode == 'SUB':
        select = np.zeros(shape, "?")
        elem.foreach_get("select", select)
        select = select & ~inside_mask
    elif mode == 'XOR':
        select = np.zeros(shape, "?")
        elem.foreach_get("select", select)
        select = select ^ inside_mask
    else:  # mode == 'AND'
        select = np.zeros(shape, "?")
        elem.foreach_get("select", select)
        select = select & inside_mask
    return select


def select_elems_in_poly(context, mode, shape, poly, select_all_edges, select_all_faces):
    poly_path = None
    box_xmin = box_xmax = box_ymin = box_ymax = None
    vert_co2d = None
    vert_mask_visin = None
    edge_mask_visin = None
    vis_edge_mask_in = None
    edges_count = None

    if shape == 0:
        box_xmin, box_xmax, box_ymin, box_ymax = poly
    elif shape == 1:
        poly_path = poly
    else:  # shape == 2:
        poly_path = [p["loc"] for p in poly]

    region = context.region
    rv3d = context.region_data

    # main loop
    sel_obs = context.selected_objects if context.selected_objects else [context.object]
    for ob in sel_obs:
        if ob.type == 'MESH':
            mesh_select_mode = context.tool_settings.mesh_select_mode

            ob.update_from_editmode()
            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            # VERTS PASS ######################################################
            if mesh_select_mode[0] or mesh_select_mode[1] or \
                    mesh_select_mode[2] and select_all_faces:

                verts = me.vertices
                verts_count = len(verts)

                # get local coordinates of vertices
                vert_colocal = np.empty(verts_count * 3, "f")
                verts.foreach_get("co", vert_colocal)
                vert_colocal.shape = (verts_count, 3)

                # get mask of visible vertices
                vert_mask_vis = np.empty(verts_count, "?")
                verts.foreach_get("hide", vert_mask_vis)
                vert_mask_vis = ~vert_mask_vis

                # get local coordinates of visible vertices
                vis_vert_colocal = vert_colocal[vert_mask_vis]

                # get 2d coordinates of vertices
                vert_co2d = np.full((verts_count, 3), -1, "f")
                vert_co2d[vert_mask_vis] = get_co_2d(region, rv3d, ob, vis_vert_colocal)
                vert_co2d[vert_co2d[:, 2] <= 0] = np.nan

                # get 2d coordinates of visible vertices
                vis_vert_co2d = vert_co2d[vert_mask_vis]

                # get mask of visible vertices inside the selection border
                # box select
                if shape == 0:
                    vis_vert_mask_in = points_inside_rectangle(
                        vis_vert_co2d, box_xmin, box_xmax, box_ymin, box_ymax)
                # circle select or loop select
                else:
                    vis_vert_mask_in = points_inside_polygon(vis_vert_co2d, poly_path)

                # create mask for all verts
                vert_mask_visin = np.full(verts_count, False, "?")
                vert_mask_visin[vert_mask_vis] = vis_vert_mask_in

                # do selection
                if mesh_select_mode[0]:
                    select = get_selection_mask(verts, verts_count, vert_mask_visin, mode)

                    select_list = select.tolist()
                    for i, v in enumerate(bm.verts):
                        v.select = select_list[i]

            # EDGES PASS ######################################################
            if mesh_select_mode[1] or mesh_select_mode[2] and select_all_faces:
                edges = me.edges
                edges_count = len(edges)

                # for each edge get 2 indices of its vertices
                edge_verts_index = np.empty(edges_count * 2, "i")
                edges.foreach_get("vertices", edge_verts_index)
                edge_verts_index.shape = (edges_count, 2)

                # get boolean mask of visible edges
                edge_mask_vis = np.empty(edges_count, "?")
                edges.foreach_get("hide", edge_mask_vis)
                edge_mask_vis = ~edge_mask_vis

                # for each visible edge get 2 vertex indices
                vis_edge_verts_index = edge_verts_index[edge_mask_vis]

                # for each visible edge get boolean mask of vertices found to be inside polygon
                vis_edge_verts_mask_in = vert_mask_visin[vis_edge_verts_index]

                # try to select edges that are completely inside the selection rectangle
                if not select_all_edges:
                    # get mask of visible edges inside
                    vis_edge_mask_in = np.all(vis_edge_verts_mask_in, axis=1)

                # if select_all_edges or no inner edges was found
                # select all edges that intersect the selection rectangle
                if select_all_edges or \
                        (not select_all_edges and not np.any(vis_edge_mask_in)) or \
                        (mesh_select_mode[2] and select_all_faces):

                    # get coordinates of verts of visible edges
                    vis_edge_verts_co = vert_co2d[vis_edge_verts_index]

                    # box select
                    if shape == 0:
                        vis_edge_mask_in = segments_intersect_rectangle(
                            vis_edge_verts_co, box_xmin, box_xmax, box_ymin, box_ymax)
                    # circle select or loop select
                    else:
                        # bool mask of visible edges that have verts inside the selection polygon
                        # and should be selected
                        vis_edge_mask_inpoly = np.any(vis_edge_verts_mask_in, axis=1)

                        # bool mask of visible edges that have verts both laying outside of one of
                        # sides of selection polygon bbox, so they can't intersect selection
                        # polygon and shouldn't be selected
                        vis_edge_mask_outpoly = segments_outside_polygon_bbox(
                            vis_edge_verts_co, poly_path)

                        # bool mask of visible edges that may intersect selection polygon
                        # and should be tested for intersection
                        vis_edge_mask_nearpoly = ~vis_edge_mask_inpoly & ~vis_edge_mask_outpoly

                        # skip if there is no edges near selection polygon
                        if np.any(vis_edge_mask_nearpoly):
                            # get coordinates of verts of visible edges near selection polygon
                            nearpoly_vis_edge_verts_co = vis_edge_verts_co[vis_edge_mask_nearpoly]

                            # bool mask of visible edges near polygon that intersect it
                            nearpoly_vis_edge_mask_intersect = segments_intersect_polygon(
                                nearpoly_vis_edge_verts_co, poly_path)

                            vis_edge_mask_in = vis_edge_mask_inpoly
                            vis_edge_mask_in[vis_edge_mask_nearpoly] = \
                                nearpoly_vis_edge_mask_intersect
                        else:
                            vis_edge_mask_in = vis_edge_mask_inpoly

                edge_mask_visin = np.full(edges_count, False, "?")
                edge_mask_visin[edge_mask_vis] = vis_edge_mask_in

                if mesh_select_mode[1]:
                    # do selection
                    select = get_selection_mask(edges, edges_count, edge_mask_visin, mode)

                    select_list = select.tolist()
                    for i, e in enumerate(bm.edges):
                        e.select = select_list[i]

            # FACES PASS ######################################################
            if mesh_select_mode[2]:
                faces = me.polygons
                faces_count = len(faces)

                # get mask of visible faces
                face_mask_vis = np.empty(faces_count, "?")
                faces.foreach_get("hide", face_mask_vis)
                face_mask_vis = ~face_mask_vis

                # select faces which centers are inside the selection rectangle
                if not select_all_faces:
                    # get faces centers coordinates
                    face_center_colocal = np.empty(faces_count * 3, "f")
                    faces.foreach_get("center", face_center_colocal)
                    face_center_colocal.shape = (faces_count, 3)

                    # get faces center coordinates
                    vis_face_center_colocal = face_center_colocal[face_mask_vis]

                    # get 2d coordinates of visible face centers
                    vis_face_center_co2d = get_co_2d(region, rv3d, ob, vis_face_center_colocal)

                    # get mask of visible face centers inside rectangle
                    face_mask_visin = np.full(faces_count, False, "?")
                    if shape == 0:
                        vis_face_mask_in = points_inside_rectangle(
                            vis_face_center_co2d, box_xmin, box_xmax, box_ymin, box_ymax)
                    else:
                        vis_face_mask_in = points_inside_polygon(
                            vis_face_center_co2d, poly_path)

                    face_mask_visin[face_mask_vis] = vis_face_mask_in
                else:
                    # loops - edges that forms face polygons, sorted by polygon indices
                    loops = me.loops
                    loops_count = len(loops)

                    # number of vertices for each face
                    face_loop_total = np.empty(faces_count, "i")
                    faces.foreach_get("loop_total", face_loop_total)

                    in_edges_count = np.count_nonzero(edge_mask_visin)
                    # skip getting faces from edges if there is no edges inside selection border
                    if in_edges_count:
                        # getting faces from bmesh is faster when a low number of faces need to be
                        # selected from a large number of total faces, otherwise numpy is faster
                        ratio = edges_count / in_edges_count

                        if ratio > 4.5:
                            # BMESH PASS
                            visin_edge_index = tuple(np.nonzero(edge_mask_visin)[0])
                            in_face_index = [[face.index for face in bm.edges[index].link_faces]
                                             for index in visin_edge_index]

                            from itertools import chain
                            in_face_index = set(chain.from_iterable(in_face_index))
                            _c = len(in_face_index)
                            in_face_index = np.fromiter(in_face_index, "i", _c)
                        else:
                            # NUMPY PASS
                            # indices of face edges
                            loop_edges_index = np.empty(loops_count, "i")
                            loops.foreach_get("edge_index", loop_edges_index)

                            # index of face for each edge in loop
                            face_index = np.arange(faces_count)
                            loop_face_index = np.repeat(face_index, face_loop_total)

                            # indices of edges inside selection border
                            visin_edge_index = np.nonzero(edge_mask_visin)[0]

                            # find match between edge indices of loops and edge in selection border
                            loop_edges_mask_visin = np.isin(loop_edges_index, visin_edge_index)

                            # indices of faces inside selection border
                            in_face_index = np.unique(loop_face_index[loop_edges_mask_visin])

                        # FINISH SELECTION FACES FROM EDGES
                        # includes hidden faces
                        face_mask_in = np.full(faces_count, False, "?")
                        face_mask_in[in_face_index] = np.True_
                        # leave only visible faces
                        face_mask_visin = face_mask_vis & face_mask_in
                    else:
                        face_mask_in = face_mask_visin = np.full(faces_count, False, "?")

                    # FACE POLY PASS ######################################################
                    # select faces under cursor (faces that have selection inside their area)

                    # visible and not in
                    face_mask_visnoin = ~face_mask_in & face_mask_vis

                    # number of vertices of each visible face outside selection border
                    visnoin_face_loop_total = face_loop_total[face_mask_visnoin]

                    # skip if all faces was already selected
                    if visnoin_face_loop_total.size > 0:
                        # box select
                        if shape == 0:
                            cursor_co = (box_xmax, box_ymin)  # bottom right box corner
                        # circle select or loop select
                        else:
                            cursor_co = poly_path[0]

                        # sequence of vertices of all faces
                        face_verts_index = np.zeros(loops_count, "i")
                        faces.foreach_get("vertices", face_verts_index)

                        # bool mask of vertices of visible faces outside selection border
                        face_verts_mask_visnoin = np.repeat(face_mask_visnoin, face_loop_total)
                        # sequence of vertex indices of visible faces outside selection border
                        visnoin_face_verts_index = face_verts_index[face_verts_mask_visnoin]
                        # coordinates of vertices of visible faces outside selection border
                        visnoin_face_verts_co = vert_co2d[visnoin_face_verts_index]
                        # index of first face vert in face verts sequence
                        visnoin_face_cell_start = np.insert(
                            visnoin_face_loop_total[:-1].cumsum(), 0, 0)

                        # get mask of faces that have cursor in their bbox
                        # if face have nan vert co than xmin of it would be nan
                        visout_face_verts_co_x = visnoin_face_verts_co[:, 0]
                        visout_face_verts_co_y = visnoin_face_verts_co[:, 1]
                        xmin = np.minimum.reduceat(visout_face_verts_co_x, visnoin_face_cell_start)
                        xmax = np.maximum.reduceat(visout_face_verts_co_x, visnoin_face_cell_start)
                        ymin = np.minimum.reduceat(visout_face_verts_co_y, visnoin_face_cell_start)
                        ymax = np.maximum.reduceat(visout_face_verts_co_y, visnoin_face_cell_start)
                        visnoin_face_mask_inbb = point_inside_rectangles(
                            cursor_co, xmin, xmax, ymin, ymax)

                        if np.any(visnoin_face_mask_inbb):
                            # number of verts of each visible face not inside selection border
                            # that have cursor in their bbox
                            inbb_visnoin_face_loop_total = \
                                visnoin_face_loop_total[visnoin_face_mask_inbb]
                            # bool mask of vertices of visible faces not inside selection border
                            # that have cursor in bbox
                            visnoin_face_verts_mask_inbb = np.repeat(
                                visnoin_face_mask_inbb, visnoin_face_loop_total)
                            # coordinates of vertices of visible faces not inside selection border
                            # that have cursor in bbox
                            inbb_visnoin_face_verts_co = \
                                visnoin_face_verts_co[visnoin_face_verts_mask_inbb]
                            # index of first and last face vert in face verts sequence
                            bb_cumsum = inbb_visnoin_face_loop_total.cumsum()
                            inbb_visnoin_face_cell_start = np.insert(bb_cumsum[:-1], 0, 0)
                            inbb_visnoin_face_cell_end = np.subtract(bb_cumsum, 1)

                            # check if visible faces not inside selection border
                            # that have bbox under cursor
                            # have cursor inside their polygon area
                            inbb_visnoin_face_mask_inpoly = point_inside_polygons(
                                cursor_co, inbb_visnoin_face_verts_co,
                                inbb_visnoin_face_cell_start, inbb_visnoin_face_cell_end)

                            # bool mask of visible faces not inside selection border
                            # that have cursor inside their polygon area
                            visnoin_face_mask_inpoly = np.zeros_like(visnoin_face_mask_inbb, "?")
                            visnoin_face_mask_inpoly[visnoin_face_mask_inbb] = \
                                inbb_visnoin_face_mask_inpoly
                            # bool mask of faces
                            # that have cursor inside their polygon area
                            face_mask_visinpoly = np.full(faces_count, False, "?")
                            face_mask_visinpoly[face_mask_visnoin] = visnoin_face_mask_inpoly
                            # bool mask of faces that have cursor inside their polygon area or
                            # intersect selection border
                            face_mask_visin = face_mask_visinpoly | face_mask_visin

                # do selection
                select = get_selection_mask(faces, faces_count, face_mask_visin, mode)

                select_list = select.tolist()
                for i, f in enumerate(bm.faces):
                    f.select = select_list[i]

            # flush face selection after selecting/deselecting edges and vertices
            bm.select_flush_mode()

            bmesh.update_edit_mesh(me, loop_triangles=False, destructive=False)
