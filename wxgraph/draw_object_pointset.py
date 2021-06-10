import numpy as N
from .draw_object import DrawObject
from .draw_object_mixin import *


class PointSet(PointsObjectMixin, ColorOnlyMixin, DrawObject):
    """
    Draws a set of points

    If Points is a sequence of tuples: Points[N][0] is the x-coordinate of
    point N and Points[N][1] is the y-coordinate.

    If Points is a NumPy array: Points[N,0] is the x-coordinate of point
    N and Points[N,1] is the y-coordinate for arrays.

    Each point will be drawn the same color and Diameter. The Diameter
    is in screen pixels, not world coordinates.

    The hit-test code does not distingish between the points, you will
    only know that one of the points got hit, not which one. You can use
    PointSet.FindClosestPoint(WorldPoint) to find out which one

    In the case of points, the HitLineWidth is used as diameter.

    """

    def __init__(self, points, color="Black", diameter=1, in_foreground=False):
        """
        Default class constructor.

        :param points: takes a 2-tuple, or a (2,)
         `NumPy <http://www.numpy.org/>`_ array of point coordinates
        :param color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
        :param  diameter:integer the points diameter
        :param  in_foreground:boolean should object be in foreground

        """
        DrawObject.__init__(self, in_foreground)

        self.points = N.array(points, N.float)
        self.points.shape = (-1, 2)  # Make sure it is a NX2 array, even if there is only one point
        self.calc_bounding_box()
        self.diameter = diameter

        self.hitLineWidth = min(self.minHitLineWidth, diameter)
        self.set_color(color)

    def set_diameter(self, diameter):
        """
        Sets the diameter

        :param  diameter:integer the points diameter

        """
        self.diameter = diameter

    def find_closest_point(self, pos):
        """
        Returns the index of the closest point to the point, XY, given
        in World coordinates. It's essentially random which you get if
        there are more than one that are the same.

        This can be used to figure out which point got hit in a mouse
        binding callback, for instance. It's a lot faster that using a
        lot of separate points.

        :param pos: the (x,y) coordinates of the point to look for, it takes a
         2-tuple or (2,) numpy array in World coordinates

        """
        _d = self.points - pos
        return N.argmin(N.hypot(_d[:, 0], _d[:, 1]))

    def draw_d2(self, dc, points):
        # A Little optimization for a diameter2 - point
        dc.DrawPointList(points)
        dc.DrawPointList(points + (1, 0))
        dc.DrawPointList(points + (0, 1))
        dc.DrawPointList(points + (1, 1))

    def draw(self, dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc=None):
        dc.SetPen(self.pen)
        _points = world_to_pixel_func(self.points)
        _radius = int(round(self.diameter / 2))
        if self.diameter <= 1:
            dc.DrawPointList(_points)
        elif self.diameter <= 2:
            self.draw_d2(dc, _points)
        else:
            dc.SetBrush(self.brush)
            #fixme: I really should add a DrawCircleList to wxPython
            if len(_points) > 100:
                _xy = _points
                _xywh = N.concatenate((_xy - _radius, N.ones(_xy.shape) * self.diameter), 1)
                dc.DrawEllipseList(_xywh)
            else:
                for xy in _points:
                    dc.DrawCircle(xy[0], xy[1], _radius)
        if ht_dc and self.isHitable:
            ht_dc.SetPen(self.hitPen)
            ht_dc.SetBrush(self.hitBrush)
            if self.diameter <= 1:
                ht_dc.DrawPointList(_points)
            elif self.diameter <= 2:
                self.draw_d2(ht_dc, _points)
            else:
                if len(_points) > 100:
                    _xy = _points
                    _xywh = N.concatenate((_xy - _radius, N.ones(_xy.shape) * self.diameter), 1)
                    ht_dc.DrawEllipseList(_xywh)
                else:
                    for xy in _points:
                        ht_dc.DrawCircle(xy[0], xy[1], _radius)
