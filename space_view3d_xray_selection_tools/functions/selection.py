from typing import Literal, Callable

import numpy as np
from numpy.typing import NDArray


def new_object_selection_mask(
    selection_mask: NDArray[np.bool_],
    inside_mask: NDArray[np.bool_],
    mode: Literal['SET', 'ADD', 'SUB', 'XOR', 'AND'],
) -> NDArray[np.bool_]:
    """
    Updates the current selection mask by combining it with the mask of objects inside the tool frame.

    Args:
        selection_mask: Current selection mask of objects.
        inside_mask: The mask of objects within the tool frame.
        mode: Tool selection mode.

    Returns:
        The new selection mask.
    """
    # https://stackoverflow.com/questions/33384529/difference-between-numpy-logical-and-and
    match mode:
        case 'SET':
            selection_mask = inside_mask
        case 'ADD':
            selection_mask |= inside_mask
        case 'SUB':
            selection_mask &= ~inside_mask
        case 'XOR':
            selection_mask ^= inside_mask
        case 'AND':
            selection_mask &= inside_mask
        case _:
            raise ValueError("Mode is invalid")

    return selection_mask


def new_mesh_selection_mask(
    cur_selection_mask: NDArray[np.bool_],
    inside_mask: NDArray[np.bool_],
    mode: Literal['SET', 'ADD', 'SUB', 'XOR', 'AND'],
) -> NDArray[np.bool_]:
    """
    Updates the current selection mask by combining it with the mask of mesh elements inside the tool frame.

    Args:
        cur_selection_mask: Current selection state of mesh elements.
        inside_mask: The mask of mesh elements within the tool frame.
        mode: Tool selection mode.

    Returns:
        The new selection mask.
    """
    # https://stackoverflow.com/questions/33384529/difference-between-numpy-logical-and-and
    match mode:
        case 'SET':
            new_selection_mask = inside_mask
        case 'ADD':
            new_selection_mask = cur_selection_mask | inside_mask
        case 'SUB':
            new_selection_mask = cur_selection_mask & ~inside_mask
        case 'XOR':
            new_selection_mask = cur_selection_mask ^ inside_mask
        case 'AND':
            new_selection_mask = cur_selection_mask & inside_mask
        case _:
            raise ValueError("Mode is invalid")

    return new_selection_mask
