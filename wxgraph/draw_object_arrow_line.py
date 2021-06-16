from .draw_object import DrawObject
from .draw_object_mixin import *


class DrawObjectArrowLine(PointsObjectMixin, LineOnlyMixin, DrawObject):
    """
    Draws an arrow line.

    It will draw a set of arrows from point to point.

    It takes a list of 2-tuples, or a NX2 NumPy Float array of point coordinates.

    """

    def __init__(self,
                 points,
                 line_color="Black",
                 line_style="Solid",
                 line_width=1,
                 arrow_head_size=8,
                 arrow_head_angle=30,
                 in_foreground=False):
        """
        Default class constructor.

        :param points: takes a 2-tuple, or a (2,)
         `NumPy <http://www.numpy.org/>`_ array of point coordinates
        :param line_color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
        :param line_style: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetLineStyle`
        :param line_width: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetLineWidth`
        :param arrow_head_size: size of arrow head in pixels
        :param arrow_head_angle: angle of arrow head in degrees
        :param in_foreground:boolean should object be in foreground

        """

        DrawObject.__init__(self, in_foreground)

        self.points = N.asarray(points, N.float)
        self.points.shape = (-1, 2)  # Make sure it is a NX2 array, even if there is only one point
        self.arrowHeadSize = arrow_head_size
        self.arrowHeadAngle = float(arrow_head_angle)
        self.arrowPoints = N.zeros(1)
        self.calc_arrow_points()
        self.calc_bounding_box()

        self.lineColor = line_color
        self.lineStyle = line_style
        self.lineWidth = line_width

        self.set_pen(line_color, line_style, line_width)

        self.hitLineWidth = max(line_width, self.minHitLineWidth)

    def calc_arrow_points(self):
        """
        Calculate the arrow points.
        """
        _s = self.arrowHeadSize
        _phi = self.arrowHeadAngle * N.pi / 360
        _points = self.points
        _n = _points.shape[0]
        self.arrowPoints = N.zeros((_n - 1, 3, 2), N.float)
        for i in range(_n - 1):
            _dx, _dy = self.points[i] - self.points[i + 1]
            _theta = N.arctan2(_dy, _dx)
            _ap = N.array((
                (N.cos(_theta - _phi), -N.sin(_theta - _phi)),
                (0, 0),
                (N.cos(_theta + _phi), -N.sin(_theta + _phi))
            ),
                N.float)
            self.arrowPoints[i, :, :] = _ap
        self.arrowPoints *= _s

    def draw(self, dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc=None):
        _points = world_to_pixel_func(self.points)
        _arrowPoints = _points[1:, N.newaxis, :] + self.arrowPoints
        dc.SetPen(self.pen)
        dc.DrawLines(_points)
        for arrow in _arrowPoints:
            dc.DrawLines(arrow)
        if ht_dc and self.isHitable:
            ht_dc.SetPen(self.hitPen)
            ht_dc.DrawLines(_points)
            for arrow in _arrowPoints:
                ht_dc.DrawLines(arrow)
