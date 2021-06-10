from .draw_object import DrawObject
from .draw_object_mixin import *


class DrawObjectPolygon(PointsObjectMixin, LineAndFillMixin, DrawObject):
    """
    Draws a polygon

    Points is a list of 2-tuples, or a NX2 NumPy array of
    point coordinates.  so that Points[N][0] is the x-coordinate of
    point N and Points[N][1] is the y-coordinate or Points[N,0] is the
    x-coordinate of point N and Points[N,1] is the y-coordinate for
    arrays.

    """

    def __init__(self,
                 points,
                 line_color="Black",
                 line_style="Solid",
                 line_width=1,
                 fill_color=None,
                 fill_style="Solid",
                 in_foreground=False):
        """
        Default class constructor.

        :param points: start point, takes a 2-tuple, or a (2,)
         `NumPy <http://www.numpy.org/>`_ array of point coordinates
        :param line_color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
        :param line_style: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetLineStyle`
        :param line_width: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetLineWidth`
        :param fill_color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
        :param fill_style: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetFillStyle`
        :param in_foreground:boolean should object be in foreground

        """
        DrawObject.__init__(self, in_foreground)
        self.points = N.array(points, N.float)  # this DOES need to make a copy
        self.calc_bounding_box()

        self.lineColor = line_color
        self.lineStyle = line_style
        self.lineWidth = line_width
        self.fillColor = fill_color
        self.fillStyle = fill_style

        self.hitLineWidth = max(line_width, self.minHitLineWidth)

        self.set_pen(line_color, line_style, line_width)
        self.set_brush(fill_color, fill_style)

    def draw(self, dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc=None):
        _points = world_to_pixel_func(self.points)  # .tolist()
        dc.SetPen(self.pen)
        dc.SetBrush(self.brush)
        dc.DrawPolygon(_points)
        if ht_dc and self.isHitable:
            ht_dc.SetPen(self.hitPen)
            ht_dc.SetBrush(self.hitBrush)
            ht_dc.DrawPolygon(_points)
