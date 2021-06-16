from .draw_object import DrawObject
from .draw_object_mixin import *


class DrawObjectPoint(PositionObjectMixin, ColorOnlyMixin, DrawObject):
    """
    A point DrawObject

    .. note::

       The Bounding box is just the point, and doesn't include the Diameter.

       The HitLineWidth is used as diameter for the Hit Test.

    """

    def __init__(self, pos, color="Black", diameter=1, in_foreground=False):
        """
        Default class constructor.

        :param pos: the (x, y) coordinate of the center of the point, or a
         2-tuple, or a (2,) `NumPy <http://www.numpy.org/>`_ array
        :param color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
        :param  diameter: integer in screen points
        :param in_foreground: define if object is in foreground

        """

        DrawObject.__init__(self, in_foreground)

        self.position = N.array(pos, N.float)
        self.position.shape = (2,)  # Make sure it is a length 2 vector
        self.calc_bounding_box()
        self.set_color(color)
        self.diameter = diameter

        self.hitLineWidth = self.minHitLineWidth

    def set_diameter(self, diameter):
        """
        Set the diameter of the object.

        :param  diameter: integer in screen points

        """
        self.diameter = diameter

    def draw(self, dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc=None):
        dc.SetPen(self.pen)
        _pos = world_to_pixel_func(self.position)
        _radius = int(round(self.diameter / 2))
        if self.diameter <= 1:
            dc.DrawPoint(*_pos)
        else:
            dc.SetBrush(self.brush)
            dc.DrawCircle(_pos[0], _pos[1], _radius)
        if ht_dc and self.isHitable:
            ht_dc.SetPen(self.hitPen)
            if self.diameter <= 1:
                ht_dc.DrawPoint(*_pos)
            else:
                ht_dc.SetBrush(self.hitBrush)
                ht_dc.DrawCircle(*_pos, _radius)
