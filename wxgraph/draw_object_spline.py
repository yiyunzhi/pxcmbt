from .draw_object_line import DrawObjectLine


class DrawObjectSpline(DrawObjectLine):
    """Draws a spline"""

    def __init__(self, *args, **kwargs):
        """
        Default class constructor.

        see :class:`~lib.floatcanvas.FloatCanvas.Line`

        """
        DrawObjectLine.__init__(self, *args, **kwargs)

    def draw(self, dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc=None):
        _points = world_to_pixel_func(self.points)
        dc.SetPen(self.pen)
        dc.DrawSpline(_points)
        if ht_dc and self.isHitable:
            ht_dc.SetPen(self.hitPen)
            ht_dc.DrawSpline(_points)
