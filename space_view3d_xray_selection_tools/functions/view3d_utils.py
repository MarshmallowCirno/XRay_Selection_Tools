import bpy
import mathutils
import numpy as np

from ..types import Bool1DArray, Float2DArray, Float3DArray, Float4x4DArray, FloatNx3DArray


def transform_local_to_world_co(mat_world: mathutils.Matrix, co_local: Float3DArray) -> Float3DArray:
    """
    Transform local coordinates to global/world coordinates using the world space transformation matrix.

    Args:
        mat_world: 4x4 world space transformation matrix.
        co_local: Nx3 array representing local coordinates in the object’s space.

    Returns:
        Nx3 array of global/world coordinates after applying the transformation matrix.
    """
    mat_world_np = np.array(mat_world)
    mat = mat_world_np[:3, :3].T  # rotates backwards without T
    loc = mat_world_np[:3, 3]
    co_world = co_local @ mat + loc
    return co_world


def batch_transform_local_to_world_co(mat_world: Float4x4DArray, co_local: FloatNx3DArray) -> FloatNx3DArray:
    """
    Transform arrays of local coordinates to global/world coordinates using corresponding arrays of
    world space transformation matrices.

    Args:
        mat_world: Mx4x4 array of transformation matrices, where each matrix corresponds to an object's
            world space transformation.
        co_local: MxNx3 array of local coordinates, where each row represents the array of coordinates
            in the object's local space.

    Returns:
        MxNx3 array of global/world coordinates after applying the respective transformation matrices.
    """
    mat = mat_world[:, :3, :3]
    mat = mat.transpose((0, 2, 1))  # rotates backwards without T
    loc = mat_world[:, :3, 3]
    co_world = co_local @ mat + loc[:, None]
    return co_world


def transform_world_to_2d_co(
    region: bpy.types.Region,
    rv3d: bpy.types.RegionView3D,
    co_world: Float3DArray,
    apply_clipping_mask: bool = True,
) -> tuple[Float2DArray, Bool1DArray]:
    """
    Transform global/world coordinates to 2D coordinates using the viewport perspective matrix.

    Args:
        region: Region of the 3D viewport, typically bpy.context.region.
        rv3d: 3D region data, typically bpy.context.space_data.region_3d.
        co_world: Nx3 array of 3D world space coordinates.
        apply_clipping_mask:
            - If True: Replace clipped values with `np.nan`.
            - If False: Keep clipped values unchanged.

    Returns:
        A tuple containing:
            - Nx2 array of 2D coordinates.
            - Clipping mask (`np.True` for clipped values, `np.False` otherwise).

    References:
        - Blender's implementation: https://github.com/blender/blender/blob/594f47ecd2d5367ca936cf6fc6ec8168c2b360d0/release/scripts/modules/bpy_extras/view3d_utils.py#L170
    """
    # Calculate projection.
    # https://blender.stackexchange.com/questions/6155/how-to-convert-coordinates-from-vertex-to-world-space
    rv3d_mat = np.array(rv3d.perspective_matrix)
    c = co_world.shape[0]
    co_world_4d = np.column_stack([co_world, np.ones((c, 1), "f")])
    prj = (rv3d_mat @ co_world_4d.T).T

    # Calculate 2D co.
    width_half = region.width / 2.0
    height_half = region.height / 2.0
    prj_w = prj[:, 3]  # negative if coord is behind the origin of a perspective view

    co_2d = np.empty((c, 2), "f")
    mask_clip = prj_w <= 0

    if not apply_clipping_mask:
        prj_w = np.abs(prj_w)

    co_2d[:, 0] = width_half * (1 + (prj[:, 0] / prj_w))
    co_2d[:, 1] = height_half * (1 + (prj[:, 1] / prj_w))

    if apply_clipping_mask:
        co_2d[mask_clip] = np.nan

    return co_2d, mask_clip
