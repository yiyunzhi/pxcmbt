import numpy as N
import wx


class DrawGraphDotGrid:
    """
    An example of a Grid Object -- it is set on the FloatCanvas with one of::

        FloatCanvas.GridUnder = Grid
        FloatCanvas.GridOver = Grid

    It will be drawn every time, regardless of the viewport.

    In its _Draw method, it computes what to draw, given the ViewPortBB
    of the Canvas it's being drawn on.

    """

    def __init__(self, spacing, size=2, color="Black", cross=False, cross_thickness=1):

        self.spacing = N.array(spacing, N.float)
        self.spacing.shape = (2,)
        self.size = size
        self.color = color
        self.cross = cross
        self.crossThickness = cross_thickness

    def calc_points(self, canvas):
        _viewPortBB = canvas.viewPortBB
        _spacing = self.spacing
        _minx, _miny = N.floor(_viewPortBB[0] / _spacing) * _spacing
        _maxx, _maxy = N.ceil(_viewPortBB[1] / _spacing) * _spacing
        # fixme: this could use vstack or something with numpy
        _x = N.arange(_minx, _maxx + _spacing[0], _spacing[0])  # making sure to get the last point
        _y = N.arange(_miny, _maxy + _spacing[1], _spacing[1])  # an extra is OK
        _points = N.zeros((len(_y), len(_x), 2), N.float)
        _x.shape = (1, -1)
        _y.shape = (-1, 1)
        _points[:, :, 0] += _x
        _points[:, :, 1] += _y
        _points.shape = (-1, 2)
        return _points

    def draw(self, dc, canvas):
        _points = self.calc_points(canvas)
        _points = canvas.world_to_pixel(_points)
        dc.SetPen(wx.Pen(self.color, self.crossThickness))
        if self.cross:
            # Use cross shaped markers Horizontal lines
            _line_points = N.concatenate((_points + (self.size, 0), _points + (-self.size, 0)), 1)
            dc.DrawLineList(_line_points)
            # Vertical Lines
            _line_points = N.concatenate((_points + (0, self.size), _points + (0, -self.size)), 1)
            dc.DrawLineList(_line_points)
            pass
        else:
            # use dots
            # Note: this code borrowed from Pointset -- it really shouldn't be repeated here!.
            if self.size <= 1:
                dc.DrawPointList(_points)
            elif self.size <= 2:
                dc.DrawPointList(_points + (0, -1))
                dc.DrawPointList(_points + (0, 1))
                dc.DrawPointList(_points + (1, 0))
                dc.DrawPointList(_points + (-1, 0))
            else:
                dc.SetBrush(wx.Brush(self.color))
                _radius = int(round(self.size / 2))
                # fixme: I really should add a DrawCircleList to wxPython
                if len(_points) > 100:
                    _xy = _points
                    _xywh = N.concatenate((_xy - _radius, N.ones(_xy.shape) * self.size), 1)
                    dc.DrawEllipseList(_xywh)
                else:
                    for xy in _points:
                        dc.DrawCircle(xy[0], xy[1], _radius)
