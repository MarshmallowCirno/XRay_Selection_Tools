from typing import Literal

from ...types import Bool1DArray


def calculate_selection_mask(
    cur_selection_mask: Bool1DArray,
    inside_mask: Bool1DArray,
    mode: Literal['SET', 'ADD', 'SUB', 'XOR', 'AND'],
) -> Bool1DArray:
    """
    Calculate the new selection mask by combining a current one with the mask of elements within the tool region.

    Args:
        cur_selection_mask: Current selection state of elements.
        inside_mask: A mask of elements within the tool region.
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

    return new_selection_mask
