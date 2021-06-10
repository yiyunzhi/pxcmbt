from .draw_object import DrawObject
from .draw_object_mixin import *


class DrawObjectLine(PointsObjectMixin, LineOnlyMixin, DrawObject):
    """
    Draws a line

    It will draw a straight line if there are two points, and a polyline
    if there are more than two.

    """

    def __init__(self, points,
                 line_color="Black",
                 line_style="Solid",
                 line_width=1,
                 in_foreground=False):
        """
        Default class constructor.

        :param points: takes a 2-tuple, or a (2,)
         `NumPy <http://www.numpy.org/>`_ array of point coordinates
        :param line_color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
        :param line_style: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetLineStyle`
        :param line_width: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetLineWidth`
        :param  in_foreground:boolean should object be in foreground

        """
        DrawObject.__init__(self, in_foreground)

        self.points = N.array(points, N.float)
        self.calc_bounding_box()

        self.lineColor = line_color
        self.lineStyle = line_style
        self.lineWidth = line_width

        self.set_pen(line_color, line_style, line_width)

        self.hitLineWidth = max(line_width, self.minHitLineWidth)

    def draw(self, dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc=None):
        _points = world_to_pixel_func(self.points)
        dc.SetPen(self.pen)
        dc.DrawLines(_points)
        if ht_dc and self.isHitable:
            ht_dc.SetPen(self.hitPen)
            ht_dc.DrawLines(_points)
