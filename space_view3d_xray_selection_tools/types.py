from typing import Literal, TypeAlias

import numpy as np

Float1DArray: TypeAlias = np.ndarray[tuple[int], np.dtype[np.float32]]
Float2DArray: TypeAlias = np.ndarray[tuple[int, Literal[2]], np.dtype[np.float32]]
Float3DArray: TypeAlias = np.ndarray[tuple[int, Literal[3]], np.dtype[np.float32]]

Float2x2DArray: TypeAlias = np.ndarray[tuple[int, Literal[2], Literal[2]], np.dtype[np.float32]]
Float4x4DArray: TypeAlias = np.ndarray[tuple[int, Literal[4], Literal[4]], np.dtype[np.float32]]
FloatNx3DArray: TypeAlias = np.ndarray[tuple[int, int, Literal[3]], np.dtype[np.float32]]

Int1DArray: TypeAlias = np.ndarray[tuple[int], np.dtype[np.int32]]
Int2DArray: TypeAlias = np.ndarray[tuple[int, Literal[2]], np.dtype[np.int32]]

Bool1DArray: TypeAlias = np.ndarray[tuple[int], np.dtype[np.bool_]]
Bool2DArray: TypeAlias = np.ndarray[tuple[int, Literal[2]], np.dtype[np.bool_]]
