from .draw_object import DrawObject
from .draw_object_mixin import *


class DrawObjectSquarePoint(PositionObjectMixin, ColorOnlyMixin, DrawObject):
    """
    Draws a square point

    The Size is in screen points, not world coordinates, so the
    Bounding box is just the point, and doesn't include the Size.

    The HitLineWidth is used as diameter for the  Hit Test.

    """

    def __init__(self, pos, color="Black", size=4, in_foreground=False):
        """
        Default class constructor.

        :param pos: takes a 2-tuple, or a (2,)
         `NumPy <http://www.numpy.org/>`_ array of point coordinates
        :param color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
        :param integer size: the size of the square point
        :param  in_foreground:boolean should object be in foreground

        """
        DrawObject.__init__(self, in_foreground)

        self.position = N.array(pos, N.float)
        self.position.shape = (2,)  # Make sure it is a length 2 vector
        self.calc_bounding_box()
        self.set_color(color)
        self.size = size

        self.hitLineWidth = self.minHitLineWidth

    def set_size(self, size):
        """
        Sets the size

        :param integer `Size`: the size of the square point

        """
        self.size = size

    def draw(self, dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc=None):
        _size = self.size
        dc.SetPen(self.pen)
        _xc, _yc = world_to_pixel_func(self.position)

        if self.size <= 1:
            dc.DrawPoint(_xc, _yc)
        else:
            _x = _xc - _size / 2.0
            _y = _yc - _size / 2.0
            dc.SetBrush(self.brush)
            dc.DrawRectangle(_x, _y, _size, _size)
        if ht_dc and self.isHitable:
            ht_dc.SetPen(self.hitPen)
            if self.size <= 1:
                ht_dc.DrawPoint(_xc, _xc)
            else:
                ht_dc.SetBrush(self.hitBrush)
                ht_dc.DrawRectangle(_x, _y, _size, _size)
