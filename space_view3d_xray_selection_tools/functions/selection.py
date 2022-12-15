import numpy as np


def get_ob_selection_mask(select_mask, inside_mask, mode):
    # https://stackoverflow.com/questions/33384529/difference-between-numpy-logical-and-and
    match mode:
        case 'SET':
            select = inside_mask
        case 'ADD':
            select = select_mask | inside_mask
        case 'SUB':
            select = select_mask & ~inside_mask
        case 'XOR':
            select = select_mask ^ inside_mask
        case 'AND':
            select = select_mask & inside_mask
        case _:
            raise ValueError("mode is invalid")

    return select


def get_mesh_selection_mask(elem, shape, inside_mask, mode):
    # https://stackoverflow.com/questions/33384529/difference-between-numpy-logical-and-and
    match mode:
        case 'SET':
            select = inside_mask
        case 'ADD':
            select = np.zeros(shape, "?")
            elem.foreach_get("select", select)
            select = select | inside_mask
        case 'SUB':
            select = np.zeros(shape, "?")
            elem.foreach_get("select", select)
            select = select & ~inside_mask
        case 'XOR':
            select = np.zeros(shape, "?")
            elem.foreach_get("select", select)
            select = select ^ inside_mask
        case 'AND':
            select = np.zeros(shape, "?")
            elem.foreach_get("select", select)
            select = select & inside_mask
        case _:
            raise ValueError("mode is invalid")

    return select
