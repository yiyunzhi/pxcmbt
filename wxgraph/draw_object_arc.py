from .draw_object import DrawObject
from .draw_object_mixin import *
import wxgraph.util_bbox as BBox


class DrawObjectArc(PositionObjectMixin, LineAndFillMixin, DrawObject):
    """
    Draws an arc of a circle, centered on point ``CenterXY``, from
    the first point ``StartXY`` to the second ``EndXY``.

    The arc is drawn in an anticlockwise direction from the start point to
    the end point.

    """

    def __init__(self,
                 start_pos,
                 end_pos,
                 center_pos,
                 line_color="Black",
                 line_style="Solid",
                 line_width=1,
                 fill_color=None,
                 fill_style="Solid",
                 in_foreground=False):
        """
        Default class constructor.

        :param start_pos: start point, takes a 2-tuple, or a (2,)
         `NumPy <http://www.numpy.org/>`_ array of point coordinates
        :param end_pos: end point, takes a 2-tuple, or a (2,)
         `NumPy <http://www.numpy.org/>`_ array of point coordinates
        :param center_pos: center point, takes a 2-tuple, or a (2,)
         `NumPy <http://www.numpy.org/>`_ array of point coordinates
        :param line_color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
        :param line_style: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetLineStyle`
        :param line_width: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetLineWidth`
        :param fill_color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
        :param fill_style: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetFillStyle`
        :param in_foreground:boolean  should object be in foreground

        """

        DrawObject.__init__(self, in_foreground)

        # There is probably a more elegant way to do this next section
        # The bounding box just gets set to the WH of a circle, with center at CenterXY
        # This is suitable for a pie chart as it will be a circle anyway
        _radius = N.sqrt((start_pos[0] - center_pos[0]) ** 2 + (start_pos[1] - center_pos[1]) ** 2)
        _min_x = center_pos[0] - _radius
        _min_y = center_pos[1] - _radius
        _max_x = center_pos[0] + _radius
        _max_y = center_pos[1] + _radius
        _pos = [_min_x, _min_y]
        _size = [_max_x - _min_x, _max_y - _min_y]

        self.position = N.asarray(_pos, N.float).reshape((2,))
        self.size = N.asarray(_size, N.float).reshape((2,))

        self.startPosition = N.asarray(start_pos, N.float).reshape((2,))
        self.centerPosition = N.asarray(center_pos, N.float).reshape((2,))
        self.endPosition = N.asarray(end_pos, N.float).reshape((2,))

        # self.BoundingBox = array((self.XY, (self.XY + self.WH)), Float)
        self.calc_bounding_box()

        # Finish the setup; allocate color,style etc.
        self.lineColor = line_color
        self.lineStyle = line_style
        self.lineWidth = line_width
        self.fillColor = fill_color
        self.fillStyle = fill_style

        self.hitLineWidth = max(line_width, self.minHitLineWidth)

        self.set_pen(line_color, line_style, line_width)
        self.set_brush(fill_color, fill_style)  # Why isn't this working ???

    def move(self, delta):
        """
        Move the object by delta

        :param delta: delta is a (dx, dy) pair. Ideally a `NumPy <http://www.numpy.org/>`_
         array of shape (2,)

        """

        _delta = N.asarray(delta, N.float)
        self.position += _delta
        self.startPosition += _delta
        self.centerPosition += _delta
        self.endPosition += _delta
        self.boundingBox += _delta

        if self._canvas:
            self._canvas.boundingBoxDirty = True

    def draw(self, dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc=None):
        self.setup_draw(dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc)
        _start_pos = world_to_pixel_func(self.startPosition)
        _end_pos = world_to_pixel_func(self.endPosition)
        _center_pos = world_to_pixel_func(self.centerPosition)

        dc.DrawArc(_start_pos, _end_pos, _center_pos)
        if ht_dc and self.isHitable:
            ht_dc.DrawArc(_start_pos, _end_pos, _center_pos)

    def calc_bounding_box(self):
        """
        Calculate the bounding box.
        """
        self.boundingBox = BBox.as_bbox(N.array((self.position, (self.position + self.size)),
                                               N.float))
        if self._canvas:
            self._canvas.boundingBoxDirty = True
