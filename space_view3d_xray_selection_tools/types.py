from typing import Literal

import numpy as np

Float1DArray = np.ndarray[tuple[int], np.dtype[np.float32]]
Float2DArray = np.ndarray[tuple[int, Literal[2]], np.dtype[np.float32]]
Float3DArray = np.ndarray[tuple[int, Literal[3]], np.dtype[np.float32]]

Float2x2DArray = np.ndarray[tuple[int, Literal[2], Literal[2]], np.dtype[np.float32]]
Float4x4DArray = np.ndarray[tuple[int, Literal[4], Literal[4]], np.dtype[np.float32]]
FloatNx3DArray = np.ndarray[tuple[int, int, Literal[3]], np.dtype[np.float32]]

Int1DArray = np.ndarray[tuple[int], np.dtype[np.int32]]
Int2DArray = np.ndarray[tuple[int, Literal[2]], np.dtype[np.int32]]

Bool1DArray = np.ndarray[tuple[int], np.dtype[np.bool_]]
