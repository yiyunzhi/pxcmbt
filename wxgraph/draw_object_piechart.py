from .draw_object import DrawObject
from .draw_object_mixin import *
import util_bbox as BBox
import gui_color as Colors

class PieChart(PositionObjectMixin, LineOnlyMixin, DrawObject):
    """
    This is DrawObject for a pie chart

    You can pass in a bunch of values, and it will draw a pie chart for
    you, and it will make the chart, scaling the size of each "slice" to
    match your values.
    """

    #fixme: this should be a longer and better designed set.
    # Maybe one from: http://geography.uoregon.edu/datagraphics/color_scales.htm
    defaultColorList = Colors.CategoricalColor1

    # ["Red", "Green", "Blue", "Purple", "Yellow", "Cyan"]

    def __init__(self,
                 pos,
                 diameter,
                 values,
                 fill_colors=None,
                 fill_styles=None,
                 line_color=None,
                 line_style="Solid",
                 line_width=1,
                 scaled=True,
                 in_foreground=False):
        """
        Default class constructor.

        :param pos`: The (x,y) coords of the center of the chart
        :param diameter: The diamter of the chart in worls coords, unless you
                 set "Scaled" to False, in which case it's in pixel coords.
        :param values: sequence of values you want to make the chart of.
        :param fill_colors: sequence of colors you want the slices. If
                 None, it will choose (no guarantee you'll like them!)
        :param fill_styles: Fill style you want ("Solid", "Hash", etc)
        :param line_color: Color of lines separating the slices
        :param line_style: style of lines separating the slices
        :param line_width: With of lines separating the slices
        :param scaled: Do you want the pie to scale when zooming?
                 or stay the same size in pixels?
        :param in_foreground: Should it be on the foreground?
        """
        DrawObject.__init__(self, in_foreground)

        self.position = N.asarray(pos, N.float).reshape((2,))
        self.diameter = diameter
        self.values = N.asarray(values, dtype=N.float).reshape((-1, 1))
        if fill_colors is None:
            fill_colors = self.defaultColorList[:len(values)]
        if fill_styles is None:
            fill_styles = ['Solid'] * len(fill_colors)
        self.fillColors = fill_colors
        self.fillStyles = fill_styles
        self.lineColor = line_color
        self.lineStyle = line_style

        self.scaled = scaled
        self.in_foreground = in_foreground

        self.set_pen(line_color, line_style, line_width)
        self.set_brushes()
        self.calculate_points()

    def set_fill_colors(self, fill_colors):
        """
        Set the FillColors and update the Brushes.

        :param fill_colors: sequence of colors
        """
        self.fillColors = fill_colors
        self.set_brushes()

    def set_fill_styles(self, fill_styles):
        """
        Set te FillStyles and update the Brushes.

        :param fill_styles: Fill style you want ("Solid", "Hash", etc)
        """
        self.fillStyles = fill_styles
        self.set_brushes()

    def set_values(self, values):
        """
        Set the values and calculate the points.

        :param values: sequence of values you want to use for the chart
        """
        _values = N.asarray(values, dtype=N.float).reshape((-1, 1))
        self.values = _values
        self.calculate_points()

    def calculate_points(self):
        """
        Calculate the points.
        """
        # add the zero point to start
        _values = N.vstack(((0,), self.values))
        self.angles = 360. * _values.cumsum() / _values.sum()
        self.calc_bounding_box()

    def set_brushes(self):
        """Set the Brushes."""
        self.brushes = []
        for fillColor, fillStyle in zip(self.fillColors, self.fillStyles):
            if fillColor is None or fillStyle is None:
                self.brush = wx.TRANSPARENT_BRUSH
            else:
                self.brushes.append(self.brushList.setdefault((fillColor, fillStyle),
                                                              wx.Brush(fillColor, self.fillStyleList[fillStyle])))

    def calc_bounding_box(self):
        """Calculate the bounding box."""
        if self.scaled:
            self.boundingBox = BBox.as_bbox(((self.position - self.diameter), (self.position + self.diameter)))
        else:
            self.boundingBox = BBox.as_bbox((self.position, self.position))
        if self._canvas:
            self._canvas.boundingBoxDirty = True

    def draw(self, dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc=None):
        _center_pos = world_to_pixel_func(self.position)
        if self.scaled:
            _diameter = scale_world_to_pixel_func((self.diameter, self.diameter))[0]
        else:
            _diameter = self.diameter
        _size = N.array((_diameter, _diameter), dtype=N.float)
        _corner = _center_pos - (_size / 2)
        dc.SetPen(self.pen)
        for i, brush in enumerate(self.brushes):
            dc.SetBrush(brush)
            dc.DrawEllipticArc(_corner[0], _corner[1], _size[0], _size[1], self.angles[i], self.angles[i + 1])
        if ht_dc and self.isHitable:
            if self.scaled:
                _radius = (scale_world_to_pixel_func(self.diameter) / 2)[0]  # just the x-coord
            else:
                _radius = self.diameter / 2
            ht_dc.SetPen(self.hitPen)
            ht_dc.SetBrush(self.hitBrush)
            ht_dc.DrawCircle(_center_pos, _radius)
