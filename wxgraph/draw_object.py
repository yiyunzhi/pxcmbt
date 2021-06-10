import wx
import six
from .utils import color_generator

class DrawObject:
    """
    This is the base class for all the objects that can be drawn.

    One must subclass from this (and an assortment of Mixins) to create
    a new DrawObject, see for example :class:`~lib.floatcanvas.FloatCanvas.Circle`.

    """
    # I pre-define all these as class variables to provide an easier
    # interface, and perhaps speed things up by caching all the Pens
    # and Brushes, although that may not help, as I think wx now
    # does that on it's own. Send me a note if you know!

    brushList = {
        (None, "Transparent"): wx.TRANSPARENT_BRUSH,
        ("Blue", "Solid"): wx.BLUE_BRUSH,
        ("Green", "Solid"): wx.GREEN_BRUSH,
        ("White", "Solid"): wx.WHITE_BRUSH,
        ("Black", "Solid"): wx.BLACK_BRUSH,
        ("Grey", "Solid"): wx.GREY_BRUSH,
        ("MediumGrey", "Solid"): wx.MEDIUM_GREY_BRUSH,
        ("LightGrey", "Solid"): wx.LIGHT_GREY_BRUSH,
        ("Cyan", "Solid"): wx.CYAN_BRUSH,
        ("Red", "Solid"): wx.RED_BRUSH
    }
    penList = {
        (None, "Transparent", 1): wx.TRANSPARENT_PEN,
        ("Green", "Solid", 1): wx.GREEN_PEN,
        ("White", "Solid", 1): wx.WHITE_PEN,
        ("Black", "Solid", 1): wx.BLACK_PEN,
        ("Grey", "Solid", 1): wx.GREY_PEN,
        ("MediumGrey", "Solid", 1): wx.MEDIUM_GREY_PEN,
        ("LightGrey", "Solid", 1): wx.LIGHT_GREY_PEN,
        ("Cyan", "Solid", 1): wx.CYAN_PEN,
        ("Red", "Solid", 1): wx.RED_PEN
    }

    fillStyleList = {
        "Transparent": wx.BRUSHSTYLE_TRANSPARENT,
        "Solid": wx.BRUSHSTYLE_SOLID,
        "BiDiagonalHatch": wx.BRUSHSTYLE_BDIAGONAL_HATCH,
        "CrossDiagHatch": wx.BRUSHSTYLE_CROSSDIAG_HATCH,
        "FDiagonal_Hatch": wx.BRUSHSTYLE_FDIAGONAL_HATCH,
        "CrossHatch": wx.BRUSHSTYLE_CROSS_HATCH,
        "HorizontalHatch": wx.BRUSHSTYLE_HORIZONTAL_HATCH,
        "VerticalHatch": wx.BRUSHSTYLE_VERTICAL_HATCH
    }

    lineStyleList = {
        "Solid": wx.PENSTYLE_SOLID,
        "Transparent": wx.PENSTYLE_TRANSPARENT,
        "Dot": wx.PENSTYLE_DOT,
        "LongDash": wx.PENSTYLE_LONG_DASH,
        "ShortDash": wx.PENSTYLE_SHORT_DASH,
        "DotDash": wx.PENSTYLE_DOT_DASH,
    }

    def __init__(self, in_foreground=False, is_visible=True):
        """
        Default class constructor.

        :param in_foreground:boolean Define if object should be in foreground
         or not
        :param  is_visible: boolean Define if object should be visible

        """
        self.isInForeground = in_foreground
        self._canvas = None
        self.hitColor = None
        self.callBackFuncs = {}

        # these are the defaults
        self.isHitable = False
        self.isHitLine = True
        self.isHitFill = True
        self.minHitLineWidth = 3
        # this gets re-set by the subclasses if necessary
        self.hitLineWidth = 3

        self.brush = None
        self.pen = None

        self.fillStyle = "Solid"
        self.lineStyle = 'Transparent'
        self.hitBrush = wx.TRANSPARENT_BRUSH
        self.hitPen = wx.TRANSPARENT_PEN
        self.isVisible = is_visible
        self.boundingBox=None

    def set_canvas(self, canvas):
        self._canvas = canvas

    def bind(self, event, callback_func):
        """
        Bind an event to the DrawObject

        :param event: see below for supported event types

         - EVT_FC_LEFT_DOWN
         - EVT_FC_LEFT_UP
         - EVT_FC_LEFT_DCLICK
         - EVT_FC_MIDDLE_DOWN
         - EVT_FC_MIDDLE_UP
         - EVT_FC_MIDDLE_DCLICK
         - EVT_FC_RIGHT_DOWN
         - EVT_FC_RIGHT_UP
         - EVT_FC_RIGHT_DCLICK
         - EVT_FC_ENTER_OBJECT
         - EVT_FC_LEAVE_OBJECT

        :param callback_func: the call back function for the event

        """
        # fixme: Way too much Canvas Manipulation here!
        self.callBackFuncs[event] = callback_func
        self.isHitable = True
        self._canvas.useHitTest = True
        if self.isInForeground and not self._canvas.has_foreground_ht_bitmap():
            self._canvas.make_new_foreground_ht_bitmap()
        elif not self._canvas.has_ht_bitmap() is None:
            self._canvas.make_new_ht_bitmap()
        if not self.hitColor:
            if not self._canvas.hitColorGenerator:
                # first call to prevent the background color from being used.
                self._canvas.hitColorGenerator = color_generator()
                if six.PY3:
                    next(self._canvas.hitColorGenerator)
                else:
                    self._canvas.hitColorGenerator.next()
            if six.PY3:
                self.hitColor = next(self._canvas.hitColorGenerator)
            else:
                self.hitColor = self._canvas.hitColorGenerator.next()
            self.set_hit_pen(self.hitColor, self.hitLineWidth)
            self.set_hit_brush(self.hitColor)
        # put the object in the hit dict, indexed by it's color
        if not self._canvas.hitDict:
            self._canvas.make_hit_dict()
        # put the object in the hit dict, indexed by its color
        self._canvas.hitDict[event][self.hitColor] = self

    def unbind_all(self):
        """
        Unbind all events

        .. note:: Currently only removes one from each list

        """
        # fixme: this only removes one from each list, there could be more.
        # + patch by Tim Ansel
        if self._canvas.hitDict:
            for event in self._canvas.hitDict.itervalues():
                try:
                    del event[self.hitColor]
                except KeyError:
                    pass
        self.isHitable = False

    def set_brush(self, fill_color, fill_style):
        """
        Set the brush for this DrawObject

        :param fill_color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
         for valid entries
        :param fill_style: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetFillStyle`
         for valid entries
        """
        if fill_color is None or fill_style is None:
            self.brush = wx.TRANSPARENT_BRUSH
            # fixme: should I really re-set the style?
            self.fillStyle = "Transparent"
        else:
            self.brush = self.brushList.setdefault((fill_color, fill_style),
                                                   wx.Brush(fill_color, self.fillStyleList[fill_style]))
            # print("Setting Brush, BrushList length:", len(self.brushList))

    def set_pen(self, line_color, line_style, line_width):
        """
        Set the Pen for this DrawObject

        :param line_color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
         for valid entries
        :param line_style: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetLineStyle`
         for valid entries
        :param  line_width:integer the width in pixels
        """
        if (line_color is None) or (line_style is None):
            self.pen = wx.TRANSPARENT_PEN
            self.lineStyle = 'Transparent'
        else:
            self.pen = self.penList.setdefault(
                (line_color, line_style, line_width),
                wx.Pen(line_color, line_width, self.lineStyleList[line_style]))

    def set_hit_brush(self, hit_color):
        """
        Set the brush used for hit test, do not call directly.

        :param hit_color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`

        """
        if not self.isHitFill:
            self.hitBrush = wx.TRANSPARENT_BRUSH
        else:
            self.hitBrush = self.brushList.setdefault(
                (hit_color, "solid"),
                wx.Brush(hit_color, self.fillStyleList["Solid"]))

    def set_hit_pen(self, hit_color, line_width):
        """
        Set the pen used for hit test, do not call directly.

        :param hit_color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
        :param line_width: integerthe line width in pixels

        """
        if not self.isHitLine:
            self.hitPen = wx.TRANSPARENT_PEN
        else:
            self.hitPen = self.penList.setdefault((hit_color, "solid", self.hitLineWidth),
                                                  wx.Pen(hit_color, self.hitLineWidth, self.lineStyleList["Solid"]))

    # Just to make sure that they will always be there
    #  the appropriate ones should be overridden in the subclasses
    def set_color(self, color):
        """
        Set the Color - this method is overridden in the subclasses

        :param color: use one of the following values any valid entry from
         :class:`wx.ColourDatabase`

         - ``Green``
         - ``White``
         - ``Black``
         - ``Grey``
         - ``MediumGrey``
         - ``LightGrey``
         - ``Cyan``
         - ``Red``

        """

        pass

    def set_line_color(self, line_color):
        """
        Set the LineColor - this method is overridden in the subclasses

        :param line_color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
         for valid values

        """
        pass

    def set_line_style(self, line_style):
        """
        Set the LineStyle - this method is overridden in the subclasses

        :param line_style: Use one of the following values or ``None`` :

          ===================== =============================
          Style                 Description
          ===================== =============================
          ``Solid``             Solid line
          ``Transparent``       A transparent line
          ``Dot``               Dotted line
          ``LongDash``          Dashed line (long)
          ``ShortDash``         Dashed line (short)
          ``DotDash``           Dash-dot-dash line
          ===================== =============================

        """
        pass

    def set_line_width(self, line_width):
        """
        Set the LineWidth

        :param line_width: integer sets the line width in pixel

        """
        pass

    def set_fill_color(self, fill_color):
        """
        Set the FillColor - this method is overridden in the subclasses

        :param fill_color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
         for valid values

        """
        pass

    def set_fill_style(self, fill_style):
        """
        Set the FillStyle - this method is overridden in the subclasses

        :param  fill_style: string following is a list of valid values:

          ===================== =========================================
          Style                 Description
          ===================== =========================================
          ``Transparent``       Transparent fill
          ``Solid``             Solid fill
          ``BiDiagonalHatch``   Bi Diagonal hatch fill
          ``CrossDiagHatch``    Cross Diagonal hatch fill
          ``FDiagonal_Hatch``   F Diagonal hatch fill
          ``CrossHatch``        Cross hatch fill
          ``HorizontalHatch``   Horizontal hatch fill
          ``VerticalHatch``     Vertical hatch fill
          ===================== =========================================

        """
        pass

    def put_in_background(self):
        """
        Put the object in the background.
        """
        if self._canvas and self.isInForeground:
            self._canvas.put_object_in_background(self)
            self.isInForeground = False

    def put_in_foreground(self):
        """
        Put the object in the foreground.
        """
        if self._canvas and (not self.isInForeground):
            self._canvas.put_object_in_foreground(self)
            self.isInForeground = True

    def hide(self):
        """
        Hide the object.
        """
        self.isVisible = False

    def show(self):
        """
        Show the object.
        """
        self.isVisible = True
