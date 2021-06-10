import numpy as N
from .draw_object import DrawObject
from .draw_object_mixin import *
import util_bbox as BBox

class RectEllipse(PositionObjectMixin, LineAndFillMixin, DrawObject):
    """A RectEllipse draw object."""

    def __init__(self, position, size,
                 line_color="Black",
                 line_style="Solid",
                 line_width=1,
                 fill_color=None,
                 fill_style="Solid",
                 in_foreground=False):
        """
        Default class constructor.

        :param position: the (x, y) coordinate of the corner of RectEllipse, or a 2-tuple,
         or a (2,) `NumPy <http://www.numpy.org/>`_ array
        :param size: a tuple with the Width and Height for the object
        :param line_color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
        :param line_style: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetLineStyle`
        :param line_width: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetLineWidth`
        :param fill_color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
        :param fill_style: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetFillStyle`
        :param in_foreground: put object in foreground

        """

        DrawObject.__init__(self, in_foreground)

        self.set_shape(position, size)
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

    def set_shape(self, pos, size):
        """
        Set the shape of the object.

        :param pos: takes a 2-tuple, or a (2,) `NumPy <http://www.numpy.org/>`_
         array of point coordinates
        :param size: a tuple with the Width and Height for the object

        """
        self.position = N.array(pos, N.float)
        self.position.shape = (2,)
        self.size = N.array(size, N.float)
        self.size.shape = (2,)
        self.calc_bounding_box()

    def calc_bounding_box(self):
        """Calculate the bounding box."""
        # you need this in case Width or Height are negative
        _corners = N.array((self.position, (self.position + self.size)), N.float)
        self.boundingBox = BBox.from_points(_corners)
        if self._canvas:
            self._canvas.boundingBoxDirty = True


class DrawObjectRectangle(RectEllipse):
    """
    Draws a rectangle see :class:`~lib.floatcanvas.FloatCanvas.RectEllipse`
    """

    def draw(self, dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc=None):
        _pos, _size = self.setup_draw(dc,
                                      world_to_pixel_func,
                                      scale_world_to_pixel_func,
                                      ht_dc)
        _size[N.abs(_size) < self.minSize] = self.minSize
        if not (self.disappearWhenSmall and N.abs(_size).min() <= self.minSize):  # don't try to draw it too tiny
            dc.DrawRectangle(_pos, _size)
            if ht_dc and self.isHitable:
                ht_dc.DrawRectangle(_pos, _size)


class DrawObjectEllipse(RectEllipse):
    """
    Draws an ellipse see :class:`~lib.floatcanvas.FloatCanvas.RectEllipse`
    """

    def draw(self, dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc=None):
        _pos, _size = self.setup_draw(dc,
                                  world_to_pixel_func,
                                  scale_world_to_pixel_func,
                                  ht_dc)
        _size[N.abs(_size) < self.minSize] = self.minSize
        if not (self.disappearWhenSmall and N.abs(_size).min() <= self.minSize):  # don't try to draw it too tiny
            dc.DrawEllipse(_pos, _size)
            if ht_dc and self.isHitable:
                ht_dc.DrawEllipse(_pos, _size)
