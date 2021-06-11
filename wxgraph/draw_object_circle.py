from .draw_object import DrawObject
from .draw_object_mixin import *
import wxgraph.util_bbox as BBox


class DrawObjectCircle(PositionObjectMixin, LineAndFillMixin, DrawObject):
    """Draws a circle"""

    def __init__(self, pos, diameter,
                 line_color="Black",
                 line_style="Solid",
                 line_width=1,
                 fill_color=None,
                 fill_style="Solid",
                 in_foreground=False):
        """
        Default class constructor.

        :param pos: the (x, y) coordinate of the center of the circle, or a 2-tuple,
         or a (2,) `NumPy <http://www.numpy.org/>`_ array
        :param integer diameter: the diameter for the object
        :param line_color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
        :param line_style: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetLineStyle`
        :param line_width: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetLineWidth`
        :param fill_color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
        :param fill_style: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetFillStyle`
        :param  in_foreground:boolean should object be in foreground

        """
        DrawObject.__init__(self, in_foreground)

        self.position = N.array(pos, N.float)
        self.size = N.array((diameter / 2, diameter / 2), N.float)  # just to keep it compatible with others
        self.calc_bounding_box()

        self.lineColor = line_color
        self.lineStyle = line_style
        self.lineWidth = line_width
        self.fillColor = fill_color
        self.fillStyle = fill_style

        self.hitLineWidth = max(line_width, self.minHitLineWidth)

        # these define the behaviour when zooming makes the objects really small.
        self.minSize = 1
        self.disappearWhenSmall = True

        self.set_pen(line_color, line_style, line_width)
        self.set_brush(fill_color, fill_style)

    def set_diameter(self, diameter):
        """
        Set the diameter of the object

        :param  diameter:integer the diameter for the object

        """
        self.size = N.array((diameter / 2, diameter / 2), N.float)  # just to keep it compatible with others

    def calc_bounding_box(self):
        """
        Calculate the bounding box of the object.
        """
        # you need this in case Width or Height are negative
        self.boundingBox = BBox.from_points((self.position + self.size, self.position - self.size))
        if self._canvas:
            self._canvas.boundingBoxDirty = True

    def draw(self, dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc=None):
        _pos, _size = self.setup_draw(dc,
                                      world_to_pixel_func,
                                      scale_world_to_pixel_func,
                                      ht_dc)

        _size[N.abs(_size) < self.minSize] = self.minSize
        if not (self.disappearWhenSmall and N.abs(_size).min() <= self.minSize):  # don't try to draw it too tiny
            dc.DrawCircle(_pos, _size[0])
            if ht_dc and self.isHitable:
                ht_dc.DrawCircle(_pos, _size[0])
