import wx
from .draw_object import DrawObject
from .draw_object_mixin import *
from .define import GLOBAL_VARS
import wxgraph.util_bbox as BBox


class DrawObjectText(TextObjectMixin, DrawObject):
    """
    Draws a text object

    The size is fixed, and does not scale with the drawing.

    The hit-test is done on the entire text extent

    """

    def __init__(self, text, pos,
                 size=14,
                 color="Black",
                 background_color=None,
                 family=wx.FONTFAMILY_MODERN,
                 style=wx.FONTSTYLE_NORMAL,
                 weight=wx.FONTWEIGHT_NORMAL,
                 underlined=False,
                 align='tl',
                 in_foreground=False,
                 font=None):
        """
        Default class constructor.

        :param  text:string the text to draw
        :param pos: the (x, y) coordinate of the corner of the text, or a 2-tuple,
         or a (2,) `NumPy <http://www.numpy.org/>`_ array
        :param size: the font size
        :param color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
        :param background_color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
        :param family:wx.FontFamily  a valid :ref:`wx.FontFamily`
        :param style: wx.FontStyle a valid :ref:`wx.FontStyle`
        :param weight:wx.FontWeight  a valid :ref:`wx.FontWeight`
        :param underlined:boolean underline the text
        :param align :string a two character string indicating where in
         relation to the coordinates the box should be oriented
        :param in_foreground:boolean should object be in foreground
        :param font:wx.Font alternatively you can define :ref:`wx.Font` and the
         above will be ignored.

         ============== ==========================
         1st character  Meaning
         ============== ==========================
         ``t``          top
         ``c``          center
         ``b``          bottom
         ============== ==========================

         ============== ==========================
         2nd character  Meaning
         ============== ==========================
         ``l``          left
         ``c``          center
         ``r``          right
         ============== ==========================

        :param wx.Font `Font`: a valid :class:`wx.Font`
        :param boolean `InForeground`: should object be in foreground

        """
        DrawObject.__init__(self, in_foreground)

        self.text = text
        # Input size in in Pixels, compute points size from FontScaleinfo.
        # fixme: for printing, we'll have to do something a little different
        self.size = size * GLOBAL_VARS['FONT_SCALE']

        self.color = color
        self.backgroundColor = background_color

        if font is None:
            face_name = ''
        else:
            face_name = font.GetFaceName()
            family = font.GetFamily()
            size = font.GetPointSize()
            style = font.GetStyle()
            underlined = font.GetUnderlined()
            weight = font.GetWeight()
        self.set_font(size, family, style, weight, underlined, face_name)

        self.boundingBox = BBox.as_bbox((pos, pos))

        self.position = N.asarray(pos)
        self.position.shape = (2,)

        self.textWidth, self.textHeight = None, None
        self.shiftFun = self.shiftFunDict[align]

    def draw(self, dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc=None):
        _pos = world_to_pixel_func(self.position)
        dc.SetFont(self.font)
        dc.SetTextForeground(self.color)
        if self.backgroundColor:
            dc.SetBackgroundMode(wx.SOLID)
            dc.SetTextBackground(self.backgroundColor)
        else:
            dc.SetBackgroundMode(wx.TRANSPARENT)
        if self.textWidth is None or self.textHeight is None:
            self.textWidth, self.textHeight = dc.GetTextExtent(self.text)
        _pos = self.shiftFun(_pos[0], _pos[1], self.textWidth, self.textHeight)
        dc.DrawText(self.text, _pos)
        if ht_dc and self.isHitable:
            ht_dc.SetPen(self.hitPen)
            ht_dc.SetBrush(self.hitBrush)
            ht_dc.DrawRectangle(_pos, (self.textWidth, self.textHeight))


class DrawObjectScaledText(TextObjectMixin, DrawObject):
    """
    #fixme: this can be depricated and jsut use ScaledTextBox with different defaults.

    This class creates a text object that is scaled when zoomed.  It is
    placed at the coordinates, x,y. the "Position" argument is a two
    charactor string, indicating where in relation to the coordinates
    the string should be oriented.

    The first letter is: t, c, or b, for top, center and bottom The
    second letter is: l, c, or r, for left, center and right The
    position refers to the position relative to the text itself. It
    defaults to "tl" (top left).

    Size is the size of the font in world coordinates.

    * Family: Font family, a generic way of referring to fonts without
      specifying actual facename. One of:

            * wx.FONTFAMILY_DEFAULT:  Chooses a default font.
            * wx.FONTFAMILY_DECORATIVE: A decorative font.
            * wx.FONTFAMILY_ROMAN: A formal, serif font.
            * wx.FONTFAMILY_SCRIPT: A handwriting font.
            * wx.FONTFAMILY_SWISS: A sans-serif font.
            * wx.FONTFAMILY_MODERN: A fixed pitch font.

      .. note:: these are only as good as the wxWindows defaults, which aren't so good.

    * Style: One of wx.FONTSTYLE_NORMAL, wx.FONTSTYLE_SLANT and wx.FONTSTYLE_ITALIC.
    * Weight: One of wx.FONTWEIGHT_NORMAL, wx.FONTWEIGHT_LIGHT and wx.FONTWEIGHT_BOLD.
    * Underlined: The value can be True or False. At present this may have an an
      effect on Windows only.


    Alternatively, you can set the kw arg: Font, to a wx.Font, and the
    above will be ignored. The size of the font you specify will be
    ignored, but the rest of its attributes will be preserved.

    The size will scale as the drawing is zoomed.

    Bugs/Limitations:

    As fonts are scaled, the do end up a little different, so you don't
    get exactly the same picture as you scale up and doen, but it's
    pretty darn close.

    On wxGTK1 on my Linux system, at least, using a font of over about
    3000 pts. brings the system to a halt. It's the Font Server using
    huge amounts of memory. My work around is to max the font size to
    3000 points, so it won't scale past there. GTK2 uses smarter font
    drawing, so that may not be an issue in future versions, so feel
    free to test. Another smarter way to do it would be to set a global
    zoom limit at that point.

    The hit-test is done on the entire text extent. This could be made
    optional, but I haven't gotten around to it.

    """

    def __init__(self,
                 text,
                 pos,
                 size,
                 color="Black",
                 background_color=None,
                 family=wx.FONTFAMILY_MODERN,
                 style=wx.FONTSTYLE_NORMAL,
                 weight=wx.FONTWEIGHT_NORMAL,
                 underlined=False,
                 align='tl',
                 font=None,
                 in_foreground=False):

        DrawObject.__init__(self, in_foreground)

        self.text = text
        self.position = N.array(pos, N.float)
        self.position.shape = (2,)
        self.size = size
        self.color = color
        self.backgroundColor = background_color
        self.family = family
        self.style = style
        self.weight = weight
        self.underlined = underlined
        if font is None:
            self.faceName = ''
        else:
            self.faceName = font.GetFaceName()
            self.family = font.GetFamily()
            self.style = font.GetStyle()
            self.underlined = font.GetUnderlined()
            self.weight = font.GetWeight()

        # Experimental max font size value on wxGTK2: this works OK on
        # my system. If it's a lot  larger, there is a crash, with the
        # message:
        #
        # The application 'FloatCanvasDemo.py' lost its
        # connection to the display :0.0; most likely the X server was
        # shut down or you killed/destroyed the application.
        #
        # Windows and OS-X seem to be better behaved in this regard.
        # They may not draw it, but they don't crash either!
        self.maxFontSize = 1000
        self.minFontSize = 1  # this can be changed to set a minimum size
        self.disappearWhenSmall = True
        self.shiftFun = self.shiftFunDict[align]

        self.calc_bounding_box()

    def layout_text(self):
        # This will be called when the text is re-set
        # nothing much to be done here
        self.calc_bounding_box()

    def calc_bounding_box(self):
        # this isn't exact, as fonts don't scale exactly.
        dc = wx.MemoryDC()
        _bitmap = wx.Bitmap(1, 1)
        # wxMac needs a Bitmap selected for GetTextExtent to work.
        dc.SelectObject(_bitmap)
        # pts This effectively determines the resolution that the BB is computed to.
        _drawing_size = 40
        _scale_factor = float(self.size) / _drawing_size
        self.set_font(_drawing_size, self.family, self.style, self.weight, self.underlined, self.faceName)
        dc.SetFont(self.font)
        _w, _h = dc.GetTextExtent(self.text)
        _w = _w * _scale_factor
        _h = _h * _scale_factor
        _x, _y = self.shiftFun(self.position[0], self.position[1], _w, _h, world=1)
        self.boundingBox = BBox.as_bbox(((_x, _y - _h), (_x + _w, _y)))

    def draw(self, dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc=None):
        _x, _y = world_to_pixel_func(self.position)
        # compute the font size:
        # only need a y coordinate length
        _size = abs(scale_world_to_pixel_func(self.size, self.size)[1])
        # Check to see if the font size is large enough to blow up the X font server
        # If so, limit it. Would it be better just to not draw it?
        # note that this limit is dependent on how much memory you have, etc.
        # smallest size you want - default to 0
        _size = min(_size, self.maxFontSize)
        _size = max(_size, self.minFontSize)
        # Draw the Text
        if not (self.disappearWhenSmall and _size <= self.minFontSize):
            # don't try to draw a zero sized font!
            self.set_font(_size, self.family, self.style, self.weight, self.underlined, self.faceName)
            dc.SetFont(self.font)
            dc.SetTextForeground(self.color)
            if self.backgroundColor:
                dc.SetBackgroundMode(wx.SOLID)
                dc.SetTextBackground(self.backgroundColor)
            else:
                dc.SetBackgroundMode(wx.TRANSPARENT)
            _w, _h = dc.GetTextExtent(self.text)
            # compute the shift, and adjust the coordinates, if neccesary
            # This had to be put in here, because it changes with Zoom, as
            # fonts don't scale exactly.
            _xy = self.shiftFun(_x, _y, _w, _h)
            dc.DrawText(self.text, _xy)

            if ht_dc and self.isHitable:
                ht_dc.SetPen(self.hitPen)
                ht_dc.SetBrush(self.hitBrush)
                ht_dc.DrawRectangle(_xy, _w, _h)


class DrawObjectScaledTextBox(TextObjectMixin, DrawObject):
    """
    Draws a text object box

    The object is scaled when zoomed.

    The hit-test is done on the entire text extent

    Bugs/Limitations:

    As fonts are scaled, they do end up a little different, so you don't
    get exactly the same picture as you scale up and down, but it's
    pretty darn close.

    On wxGTK1 on my Linux system, at least, using a font of over about
    1000 pts. brings the system to a halt. It's the Font Server using
    huge amounts of memory. My work around is to max the font size to
    1000 points, so it won't scale past there. GTK2 uses smarter font
    drawing, so that may not be an issue in future versions, so feel
    free to test. Another smarter way to do it would be to set a global
    zoom limit at that point.

    """

    def __init__(self, text,
                 pos,
                 size,
                 color="Black",
                 background_color=None,
                 line_color='Black',
                 line_style='Solid',
                 line_width=1,
                 width=None,
                 pad_size=None,
                 family=wx.FONTFAMILY_MODERN,
                 style=wx.FONTSTYLE_NORMAL,
                 weight=wx.FONTWEIGHT_NORMAL,
                 underlined=False,
                 align='tl',
                 alignment="left",
                 font=None,
                 line_spacing=1.0,
                 in_foreground=False):
        """
        Default class constructor.

        :param pos: takes a 2-tuple, or a (2,) `NumPy <http://www.numpy.org/>`_
         array of point coordinates
        :param integer size: size in World units
        :param color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
        :param background_color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
        :param line_color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
        :param line_width: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetLineWidth`
        :param width: width in pixels or ``None``, text will be wrapped to
         the given width.
        :param pad_size: padding in world units or ``None``, if specified it
         will creating a space (margin) around the text
        :param wx.FontFamily family: a valid :ref:`wx.FontFamily`
        :param wx.FontStyle style: a valid :ref:`wx.FontStyle`
        :param wx.FontWeight weight: a valid :ref:`wx.FontWeight`
        :param boolean underlined: underline the text
        :param string align: a two character string indicating where in
         relation to the coordinates the box should be oriented

         ============== ==========================
         1st character  Meaning
         ============== ==========================
         ``t``          top
         ``c``          center
         ``b``          bottom
         ============== ==========================

         ============== ==========================
         2nd character  Meaning
         ============== ==========================
         ``l``          left
         ``c``          center
         ``r``          right
         ============== ==========================

        :param alignment: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetLineWidth`
        :param font: wx.Font  alternatively a valid :class:`wx.Font` can be defined
         in which case the above will be ignored
        :param  line_spacing:float the line space to be used
        :param  in_foreground: boolean should object be in foreground

        """
        DrawObject.__init__(self, in_foreground)

        self.position = N.array(pos, N.float)
        self.size = size
        self.color = color
        self.backgroundColor = background_color
        self.lineColor = line_color
        self.lineStyle = line_style
        self.lineWidth = line_width
        self.width = width
        if pad_size is None:
            # the default is just a little bit of padding
            self.padSize = size / 10.0
        else:
            self.padSize = float(pad_size)
        self.family = family
        self.style = style
        self.weight = weight
        self.underlined = underlined
        self.alignment = alignment.lower()
        self.lineSpacing = float(line_spacing)
        self.align = align

        if font is None:
            self.faceName = ''
        else:
            self.faceName = font.GetFaceName()
            self.family = font.GetFamily()
            self.style = font.GetStyle()
            self.underlined = font.GetUnderlined()
            self.weight = font.GetWeight()

        # Experimental max font size value on wxGTK2: this works OK on
        # my system. If it's a lot  larger, there is a crash, with the
        # message:
        #
        # The application 'FloatCanvasDemo.py' lost its
        # connection to the display :0.0; most likely the X server was
        # shut down or you killed/destroyed the application.
        #
        # Windows and OS-X seem to be better behaved in this regard.
        # They may not draw it, but they don't crash either!

        self.maxFontSize = 1000
        self.minFontSize = 1  # this can be changed to set a larger minimum size
        self.disappearWhenSmall = True

        self.shiftFun = self.shiftFunDict[align]

        self.text = text
        self.layout_text()
        self.calc_bounding_box()

        self.set_pen(line_color, line_style, line_width)
        self.set_brush(background_color, "Solid")

    def wrap_to_width(self):
        dc = wx.MemoryDC()
        _bitmap = wx.Bitmap(1, 1)
        # wxMac needs a Bitmap selected for GetTextExtent to work.
        dc.SelectObject(_bitmap)
        # pts This effectively determines the resolution that the BB is computed to.
        _drawing_size = self.layoutFontSize
        _scale_factor = float(self.size) / _drawing_size
        # Width to wrap to
        _width = (self.width - 2 * self.padSize) / _scale_factor
        self.set_font(_drawing_size, self.family, self.style, self.weight, self.underlined, self.faceName)
        dc.SetFont(self.font)
        _new_strings = []
        for s in self.text:
            # beginning = True
            _text = s.split(" ")
            _text.reverse()
            _line_length = 0
            _new_text = _text[-1]
            del _text[-1]
            while _text:
                _w = dc.GetTextExtent(' ' + _text[-1])[0]
                if _line_length + _w <= _width:
                    _new_text += ' '
                    _new_text += _text[-1]
                    _line_length = dc.GetTextExtent(_new_text)[0]
                else:
                    _new_strings.append(_new_text)
                    _new_text = _text[-1]
                    _line_length = dc.GetTextExtent(_text[-1])[0]
                del _text[-1]
            _new_strings.append(_new_text)
        self.text = _new_strings

    def rewrap(self, width):
        self.width = width
        self.layout_text()

    def layout_text(self):
        """
        Calculates the positions of the words of text.

        This isn't exact, as fonts don't scale exactly.
        To help this, the position of each individual word
        is stored separately, so that the general layout stays
        the same in world coordinates, as the fonts scale.

        """
        self.text = self.text.split("\n")
        if self.width:
            self.wrap_to_width()

        dc = wx.MemoryDC()
        _bitmap = wx.Bitmap(1, 1)
        # wxMac needs a Bitmap selected for GetTextExtent to work.
        dc.SelectObject(_bitmap)
        # pts This effectively determines the resolution that the BB is computed to.
        _drawing_size = self.layoutFontSize
        _scale_factor = float(self.size) / _drawing_size
        self.set_font(_drawing_size, self.family, self.style, self.weight, self.underlined, self.faceName)
        dc.SetFont(self.font)
        _text_height = dc.GetTextExtent("X")[1]
        _space_width = dc.GetTextExtent(" ")[0]
        _line_height = _text_height * self.lineSpacing
        _line_widths = N.zeros((len(self.text),), N.float)
        _y = 0
        _words = []
        _all_line_points = []

        for i, s in enumerate(self.text):
            _line_widths[i] = 0
            _line_words = s.split(" ")
            _line_points = N.zeros((len(_line_words), 2), N.float)
            for j, word in enumerate(_line_words):
                if j > 0:
                    _line_widths[i] += _space_width
                _words.append(word)
                _line_points[j] = (_line_widths[i], _y)
                w = dc.GetTextExtent(word)[0]
                _line_widths[i] += w
            _y -= _line_height
            _all_line_points.append(_line_points)
        _text_width = N.maximum.reduce(_line_widths)
        self.words = _words

        if self.width is None:
            _box_width = _text_width * _scale_factor + 2 * self.padSize
        else:  # use the defined Width
            _box_width = self.width
        _points = N.zeros((0, 2), N.float)

        for i, linePoints in enumerate(_all_line_points):
            # Scale to World Coords.
            linePoints *= (_scale_factor, _scale_factor)
            if self.alignment == 'left':
                linePoints[:, 0] += self.padSize
            elif self.alignment == 'center':
                linePoints[:, 0] += (_box_width - _line_widths[i] * _scale_factor) / 2.0
            elif self.alignment == 'right':
                linePoints[:, 0] += (_box_width - _line_widths[i] * _scale_factor - self.padSize)
            _points = N.concatenate((_points, linePoints))

        _box_height = -(_points[-1, 1] - (_text_height * _scale_factor)) + 2 * self.padSize
        # (x,y) = self.ShiftFun(self.XY[0], self.XY[1], BoxWidth, BoxHeight, world=1)
        _points += (0, -self.padSize)
        self.points = _points
        self.boxWidth = _box_width
        self.boxHeight = _box_height
        self.calc_bounding_box()

    def calc_bounding_box(self):
        """Calculates the Bounding Box"""
        _w, _h = self.boxWidth, self.boxHeight
        _x, _y = self.shiftFun(self.position[0], self.position[1], _w, _h, world=1)
        self.boundingBox = BBox.as_bbox(((_x, _y - _h), (_x + _w, _y)))

    def get_box_rect(self):
        _wh = (self.boxWidth, self.boxHeight)
        _xy = (self.boundingBox[0, 0], self.boundingBox[1, 1])

        return _xy, _wh

    def draw(self, dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc=None):
        _xy, _wh = self.get_box_rect()

        _points = self.points + _xy
        _points = world_to_pixel_func(_points)
        _xy = world_to_pixel_func(_xy)
        _wh = scale_world_to_pixel_func(_wh) * (1, -1)

        # compute the font size:
        _size = abs(scale_world_to_pixel_func((self.size, self.size))[1])  # only need a y coordinate length
        # Check to see if the font size is large enough to blow up the X font server
        # If so, limit it. Would it be better just to not draw it?
        # note that this limit is dependent on how much memory you have, etc.
        _size = min(_size, self.maxFontSize)

        _size = max(_size, self.minFontSize)  # smallest size you want - default to 1

        # Draw The Box
        if (self.lineStyle and self.lineColor) or self.backgroundColor:
            dc.SetBrush(self.brush)
            dc.SetPen(self.pen)
            dc.DrawRectangle(_xy, _wh)

        # Draw the Text
        if not (self.disappearWhenSmall and _size <= self.minFontSize):  # don't try to draw a zero sized font!
            self.set_font(_size, self.family, self.style, self.weight, self.underlined, self.faceName)
            dc.SetFont(self.font)
            dc.SetTextForeground(self.color)
            dc.SetBackgroundMode(wx.TRANSPARENT)
            dc.DrawTextList(self.words, _points)

        # Draw the hit box.
        if ht_dc and self.isHitable:
            ht_dc.SetPen(self.hitPen)
            ht_dc.SetBrush(self.hitBrush)
            ht_dc.DrawRectangle(_xy, _wh)
