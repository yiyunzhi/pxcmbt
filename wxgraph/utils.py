import wx
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


def color_generator():
    """
    Generates a series of unique colors used to do hit-tests with the Hit
    Test bitmap
    """
    return _cycle_indexes(index_count=3, max_value=256, step=1)
