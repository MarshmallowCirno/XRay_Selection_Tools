from collections.abc import Sequence

import numpy as np

from ..types import Bool1DArray, Float1DArray, Float2DArray, Float2x2DArray, Int1DArray


def circle_bbox(center: tuple[float, float], radius: float) -> tuple[float, float, float, float]:
    """
    Computes the bounding box of a circle.

    Args:
        center: Coordinates (x, y) of the center of the circle.
        radius: The radius of the circle.

    Returns:
        Bounding box coordinates (xmin, xmax, ymin, ymax).
    """
    xmin = center[0] - radius
    xmax = center[0] + radius
    ymin = center[1] - radius
    ymax = center[1] + radius
    return xmin, xmax, ymin, ymax


def polygon_bbox(poly: Sequence[tuple[float, float]]) -> tuple[float, float, float, float]:
    """
    Computes the bounding box of a polygon.

    Args:
        poly: Coordinates (x, y) of the polygon's vertices.

    Returns:
        Bounding box coordinates (xmin, xmax, ymin, ymax).
    """
    np_poly = np.array(poly, "f")
    xmin = np.amin(np_poly[:, 0])
    xmax = np.amax(np_poly[:, 0])
    ymin = np.amin(np_poly[:, 1])
    ymax = np.amax(np_poly[:, 1])
    return xmin, xmax, ymin, ymax


def point_inside_rectangles(
    co: tuple[float, float], xmin: Float1DArray, xmax: Float1DArray, ymin: Float1DArray, ymax: Float1DArray
) -> Bool1DArray:
    """
    Determines if a single point lies inside multiple rectangles.

    Args:
        co: Coordinates (x, y) of the point.
        xmin: Minimum x-coordinates of the rectangles.
        xmax: Maximum x-coordinates of the rectangles.
        ymin: Minimum y-coordinates of the rectangles.
        ymax: Maximum y-coordinates of the rectangles.

    Returns:
        A boolean mask where each element is `True` if the point is inside
        the corresponding rectangle, and `False` otherwise.
    """
    x, y = co
    with np.errstate(invalid="ignore"):
        return (xmin < x) & (x < xmax) & (ymin < y) & (y < ymax)


def points_inside_rectangle(co: Float2DArray, xmin: float, xmax: float, ymin: float, ymax: float) -> Bool1DArray:
    """
    Determines if multiple points lie inside a single rectangle.

    Args:
        co: Coordinates of the points, where each row represents (x, y).
        xmin: Minimum x-coordinate of the rectangle.
        xmax: Maximum x-coordinate of the rectangle.
        ymin: Minimum y-coordinate of the rectangle.
        ymax: Maximum y-coordinate of the rectangle.

    Returns:
        A boolean mask where each element is `True` if the corresponding point is inside
        the rectangle, and `False` otherwise.
    """
    x = co[:, 0]
    y = co[:, 1]
    with np.errstate(invalid="ignore"):
        return (xmin < x) & (x < xmax) & (ymin < y) & (y < ymax)


def segments_on_same_rectangle_side(
    segment_co: Float2x2DArray, xmin: float, xmax: float, ymin: float, ymax: float
) -> Bool1DArray:
    """
    Determines if both endpoints of multiple line segments lie on the same side of a given rectangle.

    This is a fast check for segments that are guaranteed not to intersect the rectangle.
    Segments passing this test may still not intersect the rectangle.

    Args:
        segment_co: Line segments defined by their endpoints, where each segment is ((x1, y1), (x2, y2)).
        xmin: The minimum x-coordinate of the rectangle.
        xmax: The maximum x-coordinate of the rectangle.
        ymin: The minimum y-coordinate of the rectangle.
        ymax: The maximum y-coordinate of the rectangle.

    Returns:
        A boolean mask where each element is `True` if both endpoints of the corresponding segment
        lie on the same side of the rectangle, and `False` otherwise.

    Reference:
        Blender's implementation: https://github.com/blender/blender/blob/594f47ecd2d5367ca936cf6fc6ec8168c2b360d0/source/blender/editors/space_view3d/view3d_select.c#L486
    """
    v1x = segment_co[:, 0, 0]
    v1y = segment_co[:, 0, 1]
    v2x = segment_co[:, 1, 0]
    v2y = segment_co[:, 1, 1]

    with np.errstate(invalid="ignore"):
        return (
            np.isnan(v1x)
            | np.isnan(v2x)
            | (v1x < xmin) & (v2x < xmin)
            | (v1x > xmax) & (v2x > xmax)
            | (v1y < ymin) & (v2y < ymin)
            | (v1y > ymax) & (v2y > ymax)
        )


def lines_intersect_rectangle(
    line_co: Float2x2DArray, xmin: float, xmax: float, ymin: float, ymax: float
) -> Bool1DArray:
    """
    Determines if multiple lines intersect a single rectangle.

    A line is considered to intersect the rectangle if it passes through or touches any part of the rectangle,
    including its edges.

    Args:
        line_co: Lines defined by their points, where each line is ((x1, y1), (x2, y2)).
        xmin: The minimum x-coordinate of the rectangle.
        xmax: The maximum x-coordinate of the rectangle.
        ymin: The minimum y-coordinate of the rectangle.
        ymax: The maximum y-coordinate of the rectangle.

    Returns:
        A boolean mask where each element is `True` if the corresponding line intersects the rectangle,
        and `False` otherwise.

    Reference:
        Blender's implementation: https://github.com/blender/blender/blob/594f47ecd2d5367ca936cf6fc6ec8168c2b360d0/source/blender/editors/space_view3d/view3d_select.c#L500
    """
    v1x = line_co[:, 0, 0]
    v1y = line_co[:, 0, 1]
    v2x = line_co[:, 1, 0]
    v2y = line_co[:, 1, 1]

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
        segments_mask_not_isect: Bool1DArray = (
            np.isnan(v1x)
            | np.isnan(v2x)
            | ((d1 < 0) & (d2 < 0) & (d3 < 0) & (d4 < 0))
            | ((d1 > 0) & (d2 > 0) & (d3 > 0) & (d4 > 0))
        )
        return ~segments_mask_not_isect


def segments_intersect_rectangle(
    segment_co: Float2x2DArray, xmin: float, xmax: float, ymin: float, ymax: float
) -> Bool1DArray:
    """
    Determines if multiple line segments intersect a single rectangle or lie fully within it.

    A segment is considered to intersect the rectangle if it passes through or touches any part of the rectangle,
    including its edges, or if both endpoints lie entirely within the rectangle.

    Args:
        segment_co: Line segments defined by their endpoints, where each segment is ((x1, y1), (x2, y2)).
        xmin: The minimum x-coordinate of the rectangle.
        xmax: The maximum x-coordinate of the rectangle.
        ymin: The minimum y-coordinate of the rectangle.
        ymax: The maximum y-coordinate of the rectangle.

    Returns:
        A boolean mask where each element is `True` if the corresponding segment intersects the rectangle,
        and `False` otherwise.
    """
    segment_count = segment_co.shape[0]
    segments_mask_isect = np.zeros(segment_count, "?")
    segments_mask_prefiltered = ~segments_on_same_rectangle_side(segment_co, xmin, xmax, ymin, ymax)
    if not np.any(segments_mask_prefiltered):
        return segments_mask_isect

    prefiltered_segment_co = segment_co[segments_mask_prefiltered]
    prefiltered_segments_mask_isect = lines_intersect_rectangle(prefiltered_segment_co, xmin, xmax, ymin, ymax)

    segments_mask_isect[segments_mask_prefiltered] = prefiltered_segments_mask_isect
    return segments_mask_isect


def points_inside_circle(co: Float2DArray, center: tuple[float, float], radius: float) -> Bool1DArray:
    """
    Determines if multiple points lie inside a single circle.

    Args:
        co: Coordinates of the points, where each row represents (x, y).
        center: Coordinates (x, y) of the circle's center.
        radius: The radius of the circle.

    Returns:
        A boolean mask where each element is `True` if the corresponding point is inside
        the circle, and `False` otherwise.
    """
    with np.errstate(invalid="ignore"):
        return ((co[:, 0] - center[0]) ** 2 + (co[:, 1] - center[1]) ** 2) ** 0.5 < radius


def segments_intersect_circle(segment_co: Float2x2DArray, center: tuple[float, float], radius: float) -> Bool1DArray:
    """
    Determines if multiple line segments intersect a single circle or lie fully within it.

    A segment is considered to intersect the circle if any part of it passes through or touches the circle's boundary,
    or if both endpoints lie entirely within the circle.

    Args:
        segment_co: Line segments defined by their endpoints, where each segment is ((x1, y1), (x2, y2)).
        center: Coordinates (x, y) of the center of the circle.
        radius: The radius of the circle.

    Returns:
        A boolean mask where each element is `True` if the corresponding segment intersects the circle
        or lies entirely within it, and `False` otherwise.

    References:
        - Blender's implementation: https://github.com/blender/blender/blob/594f47ecd2d5367ca936cf6fc6ec8168c2b360d0/source/blender/editors/space_view3d/view3d_select.c#L2595
        - Shortest distance between a point and a line segment: https://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment/6853926#6853926
    """
    x1 = segment_co[:, 0, 0]
    y1 = segment_co[:, 0, 1]
    x2 = segment_co[:, 1, 0]
    y2 = segment_co[:, 1, 1]
    cx, cy = center

    # closest_to_line_v2
    # https://github.com/dfelinto/blender/blob/c4ef90f5a0b1d05b16187eb6e32323defe6461c0/source/blender/blenlib/intern/math_geom.c#L3364
    # Find the closest point to the circle center on the line through (x, y) and find param
    # where (0 <= param <= 1) when cp is in the line segment (x, y).
    ux = x2 - x1
    uy = y2 - y1
    hx = cx - x1
    hy = cy - y1
    dot = ux * hx + uy * hy
    len_sq = ux**2 + uy**2
    # len_sq == 0 in the case of 0 length line
    param = np.divide(dot, len_sq, out=np.full_like(dot, -1), where=len_sq != 0)
    param[np.isnan(param)] = -1

    cp_x = x1 + ux * param
    cp_y = y1 + uy * param

    # closest_to_line_segment_v2
    # https://github.com/dfelinto/blender/blob/c4ef90f5a0b1d05b16187eb6e32323defe6461c0/source/blender/blenlib/intern/math_geom.c#L353
    # Point closest to the circle center on the line segment (x, y).
    bound1 = param < 0
    bound2 = param > 1
    cp_x[bound1] = x1[bound1]
    cp_y[bound1] = y1[bound1]
    cp_x[bound2] = x2[bound2]
    cp_y[bound2] = y2[bound2]

    # dist_squared_to_line_segment_v2
    # https://github.com/dfelinto/blender/blob/c4ef90f5a0b1d05b16187eb6e32323defe6461c0/source/blender/blenlib/intern/math_geom.c#L338
    # Distance from the circle center to line-piece (x, y).
    dx = cx - cp_x
    dy = cy - cp_y
    len_squared = dx**2 + dy**2

    # Segments intersect circle.
    with np.errstate(invalid="ignore"):
        segments_mask_isect = len_squared < radius**2

    return segments_mask_isect


def segments_intersect_circle_prefiltered(
    segment_co: Float2x2DArray, center: tuple[float, float], radius: float
) -> Bool1DArray:
    """
    Determines if multiple line segments intersect a single circle or lie fully within it, with pre-filtering
    for efficiency.

    A segment is considered to intersect the circle if any part of it passes through or touches the circle's boundary,
    or if both endpoints lie entirely within the circle.

    For optimization, segments with both endpoints on the same side of the bounding box of the circle are filtered out
    before performing a detailed intersection check.

    Args:
        segment_co: Line segments defined by their endpoints, where each segment is ((x1, y1), (x2, y2)).
        center: Coordinates (x, y) of the center of the circle.
        radius: The radius of the circle.

    Returns:
        A boolean array where each element is `True` if the corresponding segment intersects the circle
        or lies entirely within it, and `False` otherwise.
    """
    segment_count = segment_co.shape[0]
    segments_mask_isect = np.zeros(segment_count, "?")
    xmin, xmax, ymin, ymax = circle_bbox(center, radius)
    segments_mask_prefiltered = ~segments_on_same_rectangle_side(segment_co, xmin, xmax, ymin, ymax)
    if not np.any(segments_mask_prefiltered):
        return segments_mask_isect

    prefiltered_segment_co = segment_co[segments_mask_prefiltered]
    prefiltered_segment_mask_isect = segments_intersect_circle(prefiltered_segment_co, center, radius)

    segments_mask_isect[segments_mask_prefiltered] = prefiltered_segment_mask_isect
    return segments_mask_isect


def point_inside_polygons(
    co: tuple[float, float],
    poly_vert_co: Float2DArray,
    poly_cell_starts: Int1DArray,
    poly_cell_ends: Int1DArray,
) -> Bool1DArray:
    """
    Determines if a single point lie inside multiple polygons using the even–odd rule.

    Args:
        co: Coordinates (x, y) of the point.
        poly_vert_co: Flattened coordinates of polygon vertices, where each row represents (x, y).
        poly_cell_starts: Index of the starting vertex for each polygon.
        poly_cell_ends: Index of the ending vertex for each polygon.

    Returns:
        A boolean mask where each element is `True` if the point is inside the corresponding polygon,
        and `False` otherwise.

    References:
        - Even–odd rule: https://en.wikipedia.org/wiki/Even–odd_rule
        - Point-in-polygon algorithm: https://wrf.ecse.rpi.edu/Research/Short_Notes/pnpoly.html
        - Blender implementation: https://github.com/blender/blender/blob/594f47ecd2d5367ca936cf6fc6ec8168c2b360d0/source/blender/blenlib/intern/math_geom.c#L1541
    """
    # Prepare points
    # [0, 1, 2, 3], [0, 1, 2, 3, 4], [0, 1, 2] polygons example
    # [0, 1, 2, 3, 0, 1, 2, 3, 4, 0, 1, 2] first vertex indices example
    # [0, 1, 2, 4, 0, 1, 2, 3, 2, 0, 1, 3] second vertex indices example after replacing
    # [3, 0, 1, 2, 4, 0, 1, 2, 3, 2, 0, 1] second vertex indices example after roll
    # Replacing example:
    # p2[3] = p1[8]
    # p2[8] = p1[11]
    # p2[11] = p1[3]
    # Then roll
    mask1 = poly_cell_ends
    mask2 = np.roll(mask1, 1)

    pt1 = poly_vert_co
    pt2 = pt1.copy()
    pt2[mask2] = pt1[mask1]
    pt2 = np.roll(pt2, 1, axis=0)

    # Extract point and vertex coordinates
    x, y = co
    pt1x = pt1[:, 0]
    pt1y = pt1[:, 1]
    pt2x = pt2[:, 0]
    pt2y = pt2[:, 1]

    # isect_point_poly_v2
    # Apply the even–odd rule for point-in-polygon testing
    with np.errstate(invalid="ignore", divide="ignore"):
        vert_odd_even = ((pt1y > y) != (pt2y > y)) & (x < (pt2x - pt1x) * (y - pt1y) / (pt2y - pt1y) + pt1x)

    # Aggregate results for each polygon
    poly_odd_even = np.add.reduceat(vert_odd_even, poly_cell_starts)
    polys_mask_has = poly_odd_even % 2 == 1

    return polys_mask_has


def point_inside_polygons_prefiltered(
    co: tuple[float, float],
    poly_vert_co: Float2DArray,
    poly_cell_starts: Int1DArray,
    poly_loop_totals: Int1DArray,
) -> Bool1DArray:
    """
    Determines if a single point lie inside multiple polygons using the even–odd rule,
    with pre-filtering for efficiency.

    For optimization, points outside the polygon bounding box are filtered out before performing
    a detailed intersection check.

    Args:
        co: Coordinates (x, y) of the point.
        poly_vert_co: Flattened coordinates of polygon vertices, where each row represents (x, y).
        poly_cell_starts: Index of the starting vertex for each polygon.
        poly_loop_totals: Number of vertices or sides for each polygon.

    Returns:
        A boolean mask where each element is `True` if the point is inside the corresponding polygon,
        and `False` otherwise.
    """
    polys_count = poly_loop_totals.size
    polys_mask_has = np.zeros(polys_count, "?")
    # Polygon bboxes.
    # If polygon has nan vert than bbox is composed of nan.
    poly_vert_co_x = poly_vert_co[:, 0]
    poly_vert_co_y = poly_vert_co[:, 1]
    xmin = np.minimum.reduceat(poly_vert_co_x, poly_cell_starts)
    xmax = np.maximum.reduceat(poly_vert_co_x, poly_cell_starts)
    ymin = np.minimum.reduceat(poly_vert_co_y, poly_cell_starts)
    ymax = np.maximum.reduceat(poly_vert_co_y, poly_cell_starts)
    # Mask of polygons that have point in their bbox.
    polys_mask_prefiltered = point_inside_rectangles(co, xmin, xmax, ymin, ymax)
    if not np.any(polys_mask_prefiltered):
        return polys_mask_has

    # Number of vertices for each prefiltered polygon.
    prefiltered_poly_loop_totals = poly_loop_totals[polys_mask_prefiltered]
    # Mask of prefiltered vertices of polygons.
    poly_verts_mask_prefiltered = np.repeat(polys_mask_prefiltered, poly_loop_totals)

    prefiltered_poly_vert_co = poly_vert_co[poly_verts_mask_prefiltered]

    # Index of the first and the last polygon vertex in the polygon vertices sequence.
    cumsum: Int1DArray = prefiltered_poly_loop_totals.cumsum()
    prefiltered_poly_cell_starts = np.insert(cumsum[:-1], 0, 0)
    prefiltered_poly_cell_ends = np.subtract(cumsum, 1)

    prefilter_polys_mask_has = point_inside_polygons(
        co,
        prefiltered_poly_vert_co,
        prefiltered_poly_cell_starts,
        prefiltered_poly_cell_ends,
    )

    polys_mask_has[polys_mask_prefiltered] = prefilter_polys_mask_has
    return polys_mask_has


def points_inside_polygon(co: Float2DArray, poly: Sequence[tuple[float, float]]) -> Bool1DArray:
    """
    Determines if multiple points lie inside a single polygon using the ray-casting method.

    Args:
        co: Line segments defined by their endpoints, where each segment is ((x1, y1), (x2, y2)).
        poly: Coordinates (x, y) of the polygon's vertices.

    Returns:
        A boolean mask where each element is `True` if the corresponding point is inside the polygon,
        and `False` otherwise.

    References:
        - Even–odd rule: https://en.wikipedia.org/wiki/Even–odd_rule
        - Point-in-polygon algorithm: https://wrf.ecse.rpi.edu/Research/Short_Notes/pnpoly.html
        - Blender implementation: https://github.com/blender/blender/blob/594f47ecd2d5367ca936cf6fc6ec8168c2b360d0/source/blender/blenlib/intern/math_geom.c#L1541
    """
    x = co[:, 0]
    y = co[:, 1]

    np_poly = np.array(poly, "f")
    poly1 = np_poly
    poly2 = np.roll(np_poly, 2)

    point_count = co.shape[0]
    points_mask_in = np.zeros(point_count, "?")

    def loop(p1x: float, p1y: float, p2x: float, p2y: float) -> None:
        xints = 0.0

        with np.errstate(invalid="ignore"):
            predicate: Bool1DArray = (y > min(p1y, p2y)) & (y <= max(p1y, p2y)) & (x <= max(p1x, p2x))
            idx = np.nonzero(predicate)[0]

        if idx.size > 0:
            if p1y != p2y:
                xints = (y[idx] - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
            if p1x == p2x:
                points_mask_in[idx] = ~points_mask_in[idx]
            else:
                idxx = idx[x[idx] <= xints]
                points_mask_in[idxx] = ~points_mask_in[idxx]

    np.frompyfunc(loop, 4, 1)(poly1[:, 0], poly1[:, 1], poly2[:, 0], poly2[:, 1])
    return points_mask_in


def points_inside_polygon_prefiltered(co: Float2DArray, poly: Sequence[tuple[float, float]]) -> Bool1DArray:
    """
    Determines if multiple points lie inside a single polygon using the ray-casting method,
    with pre-filtering for efficiency.

    For optimization, points outside the polygon bounding box are filtered out before performing
    a detailed check.

    Args:
        co: Line segments defined by their endpoints, where each segment is ((x1, y1), (x2, y2)).
        poly: Coordinates (x, y) of the polygon's vertices.

    Returns:
        A boolean mask where each element is `True` if the corresponding point is inside the polygon,
        and `False` otherwise.
    """
    point_count = co.shape[0]
    points_mask_in = np.zeros(point_count, "?")
    xmin, xmax, ymin, ymax = polygon_bbox(poly)
    points_mask_prefiltered = points_inside_rectangle(co, xmin, xmax, ymin, ymax)
    if not np.any(points_mask_prefiltered):
        return points_mask_in

    prefiltered_co = co[points_mask_prefiltered]
    prefiltered_points_mask_in = points_inside_polygon(prefiltered_co, poly)

    points_mask_in[points_mask_prefiltered] = prefiltered_points_mask_in
    return points_mask_in


def segments_intersect_polygon(segment_co: Float2x2DArray, poly: Sequence[tuple[float, float]]) -> Bool1DArray:
    """
    Determines if multiple line segments intersect a single polygon or lie fully inside it.

    A segment is considered to intersect the rectangle if it passes through or touches any part of the polygon,
    including its edges, or if both endpoints lie entirely within the polygon.

    Args:
        segment_co: Line segments defined by their endpoints, where each segment is ((x1, y1), (x2, y2)).
        poly: Coordinates (x, y) of the polygon's vertices.

    Returns:
        A boolean mask where each element is `True` if the corresponding segment intersects the polygon,
        and `False` otherwise.

    References:
        - Even–odd rule: https://en.wikipedia.org/wiki/Even–odd_rule
        - Point-in-polygon algorithm: https://wrf.ecse.rpi.edu/Research/Short_Notes/pnpoly.html
        - Blender implementation: https://github.com/blender/blender/blob/594f47ecd2d5367ca936cf6fc6ec8168c2b360d0/source/blender/blenlib/intern/lasso_2d.c#L69
    """
    s1x = segment_co[:, 0, 0]
    s1y = segment_co[:, 0, 1]
    s2x = segment_co[:, 1, 0]
    s2y = segment_co[:, 1, 1]

    poly_sides = len(poly)
    np_poly = np.array(poly, "f")
    poly1 = np_poly
    poly2 = np.roll(np_poly, 2)

    # isect_seg_seg_v2_int
    # https://github.com/blender/blender/blob/594f47ecd2d5367ca936cf6fc6ec8168c2b360d0/source/blender/blenlib/intern/math_geom.c#L1105  # noqa
    def loop(p1x: Float1DArray, p1y: Float1DArray, p2x: Float1DArray, p2y: Float1DArray) -> Bool1DArray:
        dx0 = s1x - p1x
        dy0 = s1y - p1y
        dx1 = s2x - s1x
        dy1 = s2y - s1y
        dx2 = p2x - p1x
        dy2 = p2y - p1y

        div = dx1 * dy2 - dy1 * dx2
        with np.errstate(invalid="ignore", divide="ignore"):
            param = (dy0 * dx2 - dx0 * dy2) / div
        with np.errstate(invalid="ignore", divide="ignore"):
            mu = (dy0 * dx1 - dx0 * dy1) / div
        with np.errstate(invalid="ignore"):
            poly_segments_mask_isect_segment = (0.0 <= param) & (param <= 1.0) & (0.0 <= mu) & (mu <= 1.0)

        return poly_segments_mask_isect_segment

    poly_segments_mask_isect_segments = np.frompyfunc(loop, 4, 1)(poly1[:, 0], poly1[:, 1], poly2[:, 0], poly2[:, 1])
    poly_segments_mask_isect_segments = np.hstack(poly_segments_mask_isect_segments)
    poly_segments_mask_isect_segments.shape = (poly_sides, segment_co.shape[0])
    segments_mask_isect = np.any(poly_segments_mask_isect_segments, axis=0)
    return segments_mask_isect


def segments_intersect_polygon_prefiltered(
    segment_co: Float2x2DArray, poly: Sequence[tuple[float, float]]
) -> Bool1DArray:
    """
    Determines if multiple line segments intersect a single polygon or lie fully inside it,
    with pre-filtering for efficiency.

    A segment is considered to intersect the rectangle if it passes through or touches any part of the polygon,
    including its edges, or if both endpoints lie entirely within the polygon.

    For optimization, segments with both endpoints on the same side of the bounding box of the polygon are
    filtered out before performing a detailed intersection check.

    Args:
        segment_co: Line segments defined by their endpoints, where each segment is ((x1, y1), (x2, y2)).
        poly: Coordinates (x, y) of the polygon's vertices.

    Returns:
        A boolean mask where each element is `True` if the corresponding segment intersects the polygon,
        and `False` otherwise.
    """
    segment_count = segment_co.shape[0]
    segments_mask_isect = np.zeros(segment_count, "?")
    xmin, xmax, ymin, ymax = polygon_bbox(poly)
    segments_mask_prefiltered = ~segments_on_same_rectangle_side(segment_co, xmin, xmax, ymin, ymax)
    if not np.any(segments_mask_prefiltered):
        return segments_mask_isect

    prefiltered_segment_co = segment_co[segments_mask_prefiltered]
    prefiltered_segments_mask_isect = segments_intersect_polygon(prefiltered_segment_co, poly)

    segments_mask_isect[segments_mask_prefiltered] = prefiltered_segments_mask_isect
    return segments_mask_isect
