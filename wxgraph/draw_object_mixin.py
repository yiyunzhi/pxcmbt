import numpy as N
import wx
import wxgraph.util_bbox as BBox


class ColorOnlyMixin:
    """
    Mixin class for objects that have just one color, rather than a fill
    color and line color

    """

    def set_color(self, color):
        """
        Set the Color

        :param color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
         for valid values

        """
        self.set_pen(color, "Solid", 1)
        self.set_brush(color, "Solid")

    # Just to provide a consistant interface
    set_fill_color = set_color


class LineOnlyMixin:
    """
    Mixin class for objects that have just a line, rather than a fill
    color and line color

    """

    def set_line_color(self, line_color):
        """
        Set the LineColor

        :param line_color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
         for valid values

        """
        self.lineColor = line_color
        self.set_pen(line_color, self.lineStyle, self.lineWidth)

    # so that it will do something reasonable
    set_color = set_line_color

    def set_line_style(self, line_style):
        """
        Set the LineStyle

        :param line_style: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetLineStyle`
         for valid values

        """
        self.lineStyle = line_style
        self.set_pen(self.lineColor, line_style, self.lineWidth)

    def set_line_width(self, line_width):
        """
        Set the LineWidth

        :param  line_width:integer line width in pixels

        """
        self.lineWidth = line_width
        self.set_pen(self.lineColor, self.lineStyle, line_width)


class LineAndFillMixin(LineOnlyMixin):
    """
    Mixin class for objects that have both a line and a fill color and
    style.

    """

    def set_fill_color(self, fill_color):
        """
        Set the FillColor

        :param fill_color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
         for valid values

        """
        self.fillColor = fill_color
        self.set_brush(fill_color, self.fillStyle)

    def set_fill_style(self, fill_style):
        """
        Set the FillStyle

        :param `FillStyle`: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetFillStyle`
         for valid values

        """
        self.fillStyle = fill_style
        self.set_brush(self.fillColor, fill_style)

    def setup_draw(self, dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc):
        """
        Setup for draw

        :param dc: the dc to draw ???
        :param world_to_pixel_func: ???
        :param scale_world_to_pixel_func: ???
        :param ht_dc: ???

        """
        dc.SetPen(self.pen)
        dc.SetBrush(self.brush)
        if ht_dc and self.isHitable:
            ht_dc.SetPen(self.hitPen)
            ht_dc.SetBrush(self.hitBrush)
        return world_to_pixel_func(self.position), scale_world_to_pixel_func(self.size)


class PositionObjectMixin:
    """
    This is a mixin class that provides some methods suitable for use
    with objects that have a single (x,y) coordinate pair.
    """

    def move(self, delta):
        """
        Moves the object by delta, where delta is a (dx, dy) pair.

        :param delta: is a (dx, dy) pair ideally a `NumPy <http://www.numpy.org/>`_
         array of shape (2, )

        """
        delta = N.asarray(delta, N.float)
        self.position += delta
        self.boundingBox += delta

        if self._canvas:
            self._canvas.boundingBoxDirty = True

    def calc_bounding_box(self):
        """Calculate the bounding box."""
        # This may get overwritten in some subclasses
        self.boundingBox = BBox.asBBox((self.position, self.position))

    def set_position(self, pos):
        pos = N.array(pos, N.float)
        pos.shape = (2,)

        self.position = pos
        self.calc_bounding_box()

        if self._canvas:
            self._canvas.boundingBoxDirty = True


class PointsObjectMixin:
    """
    A mixin class that provides some methods suitable for use
    with objects that have a set of (x, y) coordinate pairs.

    """

    def move(self, delta):
        """
        Moves the object by delta, where delta is a (dx, dy) pair.

        :param delta: is a (dx, dy) pair ideally a `NumPy <http://www.numpy.org/>`_
         array of shape (2, )

        """
        delta = N.asarray(delta, N.float)
        delta.shape = (2,)
        self.points += delta
        self.boundingBox += delta
        if self._canvas:
            self._canvas.boundingBoxDirty = True

    def calc_bounding_box(self):
        """
        Calculate the bounding box.
        """
        self.boundingBox = BBox.from_points(self.points)
        if self._canvas:
            self._canvas.boundingBoxDirty = True

    def set_points(self, points, copy=True):
        """
        Sets the coordinates of the points of the object to Points (NX2 array).

        :param points: takes a 2-tuple, or a (2,)
         `NumPy <http://www.numpy.org/>`_ array of point coordinates
        :param  copy:boolean By default, a copy is made, if copy is set to
         ``False``, a reference is used, if Points is a NumPy array of Floats.
         This allows you to change some or all of the points without making
         any copies.

        For example::

            Points = Object.Points
            # shifts the points 5 in the x dir, and 10 in the y dir.
            Points += (5, 10)
            # Sets the points to the same array as it was
            Object.SetPoints(Points, False)

        """
        if copy:
            self.points = N.array(points, N.float)
            self.points.shape = (-1, 2)  # Make sure it is a NX2 array, even if there is only one point
        else:
            self.points = N.asarray(points, N.float)
        self.calc_bounding_box()


class TextObjectMixin(PositionObjectMixin):
    """
    A mix in class that holds attributes and methods that are needed by
    the Text objects

    """

    # I'm caching fonts, because on GTK, getting a new font can take a
    # while. However, it gets cleared after every full draw as hanging
    # on to a bunch of large fonts takes a massive amount of memory.

    fontList = {}

    layoutFontSize = 16  # font size used for calculating layout

    def set_font(self, size, family, style, weight, underlined, face_name):
        self.font = self.fontList.setdefault((size, family,
                                              style, weight,
                                              underlined, face_name),
                                             wx.Font(size, family,
                                                     style, weight,
                                                     underlined, face_name))

    def set_color(self, color):
        self.color = color

    def set_background_color(self, background_color):
        self.backgroundColor = background_color

    def set_text(self, text):
        """
        Re-sets the text displayed by the object

        In the case of the ScaledTextBox, it will re-do the layout as appropriate

        Note: only tested with the ScaledTextBox

        """

        self.text = text
        self.layout_text()

    def layout_text(self):
        """
        A dummy method to re-do the layout of the text.

        A derived object needs to override this if required.

        """
        pass

    # store the function that shift the coords for drawing text. The
    # "c" parameter is the correction for world coordinates, rather
    # than pixel coords as the y axis is reversed
    # pad is the extra space around the text
    # if world = 1, the vertical shift is done in y-up coordinates
    shiftFunDict = {'tl': lambda x, y, w, h, world=0, pad=0: (x + pad, y + pad - 2 * world * pad),
                    'tc': lambda x, y, w, h, world=0, pad=0: (x - w / 2, y + pad - 2 * world * pad),
                    'tr': lambda x, y, w, h, world=0, pad=0: (x - w - pad, y + pad - 2 * world * pad),
                    'cl': lambda x, y, w, h, world=0, pad=0: (x + pad, y - h / 2 + world * h),
                    'cc': lambda x, y, w, h, world=0, pad=0: (x - w / 2, y - h / 2 + world * h),
                    'cr': lambda x, y, w, h, world=0, pad=0: (x - w - pad, y - h / 2 + world * h),
                    'bl': lambda x, y, w, h, world=0, pad=0: (x + pad, y - h + 2 * world * h - pad + world * 2 * pad),
                    'bc': lambda x, y, w, h, world=0, pad=0: (x - w / 2, y - h + 2 * world * h - pad + world * 2 * pad),
                    'br': lambda x, y, w, h, world=0, pad=0: (
                    x - w - pad, y - h + 2 * world * h - pad + world * 2 * pad)}
