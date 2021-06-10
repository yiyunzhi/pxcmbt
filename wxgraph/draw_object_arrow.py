from .draw_object import DrawObject
from .draw_object_mixin import *


class Arrow(PositionObjectMixin, LineOnlyMixin, DrawObject):
    """
    Draws an arrow

    It will draw an arrow , starting at the point ``XY`` points at an angle
    defined by ``Direction``.

    """

    def __init__(self,
                 pos,
                 length,
                 direction,
                 line_color="Black",
                 line_style="Solid",
                 line_width=2,
                 arrow_head_size=8,
                 arrow_head_angle=30,
                 in_foreground=False):
        """
        Default class constructor.

        :param pos: the (x, y) coordinate of the starting point, or a 2-tuple,
         or a (2,) `NumPy <http://www.numpy.org/>`_ array
        :param  length:integer length of arrow in pixels
        :param  direction:integer angle of arrow in degrees, zero is straight
          up `+` angle is to the right
        :param line_color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
        :param line_style: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetLineStyle`
        :param line_width: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetLineWidth`
        :param arrow_head_size: size of arrow head in pixels
        :param arrow_head_angle: angle of arrow head in degrees
        :param boolean `in_foreground`: should object be in foreground

        """

        DrawObject.__init__(self, in_foreground)

        self.position = N.array(pos, N.float)
        self.position.shape = (2,)  # Make sure it is a length 2 vector
        self.length = length
        self.direction = float(direction)
        self.arrowHeadSize = arrow_head_size
        self.arrowHeadAngle = float(arrow_head_angle)
        self.arrowPoints = None
        self.calc_arrow_points()
        self.calc_bounding_box()

        self.lineColor = line_color
        self.lineStyle = line_style
        self.lineWidth = line_width

        self.set_pen(line_color, line_style, line_width)

        # fixme: How should the HitTest be drawn?
        self.hitLineWidth = max(line_width, self.minHitLineWidth)

    def set_direction(self, direction):
        """
        Set the direction

        :param  direction:integer angle of arrow in degrees, zero is straight
          up `+` angle is to the right

        """
        self.direction = float(direction)
        self.calc_arrow_points()

    def set_length(self, length):
        """
        Set the length

        :param  length:integer length of arrow in pixels

        """
        self.length = length
        self.calc_arrow_points()

    def set_length_direction(self, length, direction):
        """
        Set the lenght and direction

        :param  length:integer length of arrow in pixels
        :param  direction:integer angle of arrow in degrees, zero is straight
          up `+` angle is to the right

        """
        self.direction = float(direction)
        self.length = length
        self.calc_arrow_points()

    def calc_arrow_points(self):
        """
        Calculate the arrow points.
        """
        _l = self.length
        _s = self.arrowHeadSize
        _phi = self.arrowHeadAngle * N.pi / 360
        _theta = (270 - self.direction) * N.pi / 180
        _ap = N.array(((0, 0),
                       (0, 0),
                       (N.cos(_theta - _phi), -N.sin(_theta - _phi)),
                       (0, 0),
                       (N.cos(_theta + _phi), -N.sin(_theta + _phi)),
                       ), N.float)
        _ap *= _s
        _shift = (-_l * N.cos(_theta), _l * N.sin(_theta))
        _ap[1:, :] += _shift
        self.arrowPoints = _ap

    def draw(self, dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc=None):
        dc.SetPen(self.pen)
        _pos = world_to_pixel_func(self.position)
        _arrow_points = _pos + self.arrowPoints
        dc.DrawLines(_arrow_points)
        if ht_dc and self.isHitable:
            ht_dc.SetPen(self.hitPen)
            ht_dc.DrawLines(_arrow_points)
