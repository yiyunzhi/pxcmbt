import wx
import numpy as np
from .define import IS_MAC

__testBitmap = None


def _cycle_indexes(index_count, max_value, step):
    """
    Utility function used by _colorGenerator
    """

    def color_match(color):
        """
        Return True if the color comes back from the bitmap identically.
        """
        if len(color) < 3:
            return True
        global __testBitmap
        _dc = wx.MemoryDC()
        if not __testBitmap:
            __testBitmap = wx.Bitmap(1, 1)
        _dc.SelectObject(__testBitmap)
        _dc.SetBackground(wx.BLACK_BRUSH)
        _dc.Clear()
        _dc.SetPen(wx.Pen(wx.Colour(*color), 4))
        _dc.DrawPoint(0, 0)
        if IS_MAC:  # NOTE: can the Mac not just use the DC?
            del _dc  # Mac can't work with bitmap when selected into a DC.
            _pdata = wx.AlphaPixelData(__testBitmap)
            _pacc = _pdata.GetPixels()
            _pacc.MoveTo(_pdata, 0, 0)
            _out_color = _pacc.Get()[:3]
        else:
            _out_color = _dc.GetPixel(0, 0)
        return _out_color == color

    if index_count == 0:
        yield ()
    else:
        for idx in range(0, max_value, step):
            for tail in _cycle_indexes(index_count - 1, max_value, step):
                color = (idx,) + tail
                if not color_match(color):
                    continue
                yield color


def util_color_generator():
    """
    Generates a series of unique colors used to do hit-tests with the Hit
    Test bitmap
    """
    return _cycle_indexes(index_count=3, max_value=256, step=1)


def util_vector_angle(v1, v2):
    """
    Function calculate the angle between two vectors
    :param v1: tuple, etc. (0,1) y-axis
    :param v2: tuple, etc. (0,1) y-axis
    :return: radians value
    """
    v1_u = v1 / np.linalg.norm(v1)
    v2_u = v2 / np.linalg.norm(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def util_is_close(a, b, rel_tol=1e-04, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def util_find_closest_pt_idx(pts, pos):
    _d = pts - pos
    return np.argmin(np.hypot(_d[:, 0], _d[:, 1]))


def util_angle_between_degree(p1, p2):
    ang1 = np.arctan2(*p1[::-1])
    ang2 = np.arctan2(*p2[::-1])
    return np.rad2deg((ang1 - ang2) % (2 * np.pi))
