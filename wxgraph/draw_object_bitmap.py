from .draw_object import DrawObject
from .draw_object_mixin import *
import util_bbox as BBox


class DrawObjectScaledBitmap(TextObjectMixin, DrawObject):
    """
    Draws a scaled bitmap

    The size scales with the drawing

    """

    def __init__(self,
                 bitmap,
                 pos,
                 height,
                 align='tl',
                 in_foreground=False):
        """
        Default class constructor.

        :param bitmap:wx.Bitmap  the bitmap to be drawn
        :param pos: the (x, y) coordinate of the corner of the scaled bitmap,
         or a 2-tuple, or a (2,) `NumPy <http://www.numpy.org/>`_ array
        :param height: height to be used, width is calculated from the aspect ratio of the bitmap
        :param  align:string a two character string indicating where in relation to the coordinates
         the bitmap should be oriented

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

        :param in_foreground:boolean  should object be in foreground

        """

        DrawObject.__init__(self, in_foreground)

        if isinstance(bitmap, wx.Bitmap):
            self.image = bitmap.ConvertToImage()
        elif isinstance(bitmap, wx.Image):
            self.image = bitmap
        else:
            raise ValueError("'Bitmap' must be a wx.Bitmap or wx.Image object not %s" % type(bitmap))

        self.position = pos
        self.height = height
        self.bmpWidth, self.bmpHeight = float(self.image.GetWidth()), float(self.image.GetHeight())
        self.width = self.bmpWidth / self.bmpHeight * height
        self.shiftFun = self.shiftFunDict[align]
        self.calc_bounding_box()
        self.scaledBitmap = None
        self.scaledHeight = None

    def calc_bounding_box(self):
        """
        Calculate the bounding box.
        """
        # this isn't exact, as fonts don't scale exactly.
        _w, _h = self.width, self.height
        _x, _y = self.shiftFun(self.position[0], self.position[1], _w, _h, world=1)
        self.boundingBox = BBox.as_bbox(((_x, _y - _h), (_x + _w, _y)))

    def draw(self, dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc=None):
        _pos = world_to_pixel_func(self.position)
        _h = scale_world_to_pixel_func(self.height)[0]
        _w = _h * (self.bmpWidth / self.bmpHeight)
        if self.scaledBitmap is None or _h != self.scaledHeight:
            self.scaledHeight = _h
            _img = self.image.Scale(_w, _h)
            self.scaledBitmap = wx.Bitmap(_img)

        _pos = self.shiftFun(_pos[0], _pos[1], _w, _h)
        dc.DrawBitmap(self.scaledBitmap, _pos, True)
        if ht_dc and self.isHitable:
            ht_dc.SetPen(self.hitPen)
            ht_dc.SetBrush(self.hitBrush)
            ht_dc.DrawRectangle(_pos, (_w, _h))


class DrawObjectScaledBitmapEx(TextObjectMixin, DrawObject):
    """
    Draws a scaled bitmap

    An alternative scaled bitmap that only scaled the required amount of
    the main bitmap when zoomed in: EXPERIMENTAL!

    """

    def __init__(self,
                 bitmap,
                 pos,
                 height,
                 width=None,
                 align='tl',
                 in_foreground=False):
        """
        Default class constructor.

        :param bitmap:wx.Bitmap  the bitmap to be drawn
        :param pos: the (x, y) coordinate of the corner of the scaled bitmap,
         or a 2-tuple, or a (2,) `NumPy <http://www.numpy.org/>`_ array
        :param height: height to be used
        :param width: width to be used, if ``None`` width is calculated from the aspect ratio of the bitmap
        :param align:string  a two character string indicating where in relation to the coordinates
         the bitmap should be oriented

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

        :param in_foreground:boolean  should object be in foreground

        """

        DrawObject.__init__(self, in_foreground)

        if isinstance(bitmap, wx.Bitmap):
            self.image = bitmap.ConvertToImage()
        elif isinstance(bitmap, wx.Image):
            self.image = bitmap

        self.position = N.array(pos, N.float)
        self.height = height
        self.bmpWidth, self.bmpHeight = float(self.image.GetWidth()), float(self.image.GetHeight())
        self.bmpWH = N.array((self.bmpWidth, self.bmpHeight), N.int32)
        # fixme: this should all accommodate different scales for X and Y
        if width is None:
            self.bmpScale = float(self.bmpHeight) / height
            self.width = self.bmpWidth / self.bmpScale
        self.size = N.array((self.width, height), N.float)
        # fixme: should this have a y = -1 to shift to y-up?
        self.bmpScale = self.bmpWH / self.size
        self.shiftFun = self.shiftFunDict[align]
        self.calc_bounding_box()
        self.scaledBitmap = None  # cache of the last existing scaled bitmap

    def calc_bounding_box(self):
        """
        Calculate the bounding box.
        """
        # this isn't exact, as fonts don't scale exactly.
        _w, _h = self.width, self.height
        _x, _y = self.shiftFun(self.position[0], self.position[1], _w, _h, world=1)
        self.boundingBox = BBox.as_bbox(((_x, _y - _h), (_x + _w, _y)))

    def world_to_bitmap(self, pt):
        """
        Computes the bitmap coords from World coords.
        """
        _delta = pt - self.position
        _pb = _delta * self.bmpScale
        # fixme: this may only works for Yup projection!
        _pb *= (1, -1)
        # and may only work for top left position
        return _pb.astype(N.int_)

    def draw_entire_bitmap(self, dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc=None):
        """
        this is pretty much the old code

        Scales and Draws the entire bitmap.

        """
        _pos = world_to_pixel_func(self.position)
        _h = scale_world_to_pixel_func(self.height)[0]
        _w = _h * (self.bmpWidth / self.bmpHeight)
        if self.scaledBitmap is None or self.scaledBitmap[0] != (0, 0, self.bmpWidth, self.bmpHeight, _w, _h):
            # if True:
            # fixme: (self.ScaledBitmap is None) or (H != self.ScaledHeight) :
            self.scaledHeight = _h
            # print("Scaling to:", W, H)
            _img = self.image.Scale(_w, _h)
            _bmp = wx.Bitmap(_img)
            self.scaledBitmap = ((0, 0, self.bmpWidth, self.bmpHeight, _w, _h), _bmp)  # this defines the cached bitmap
        else:
            # print("Using Cached bitmap")
            _bmp = self.scaledBitmap[1]
        _pos = self.shiftFun(_pos[0], _pos[1], _w, _h)
        dc.DrawBitmap(_bmp, _pos, True)
        if ht_dc and self.isHitable:
            ht_dc.SetPen(self.hitPen)
            ht_dc.SetBrush(self.hitBrush)
            ht_dc.DrawRectangle(_pos, (_w, _h))

    def draw_sub_bitmap(self, dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc=None):
        """
        Subsets just the part of the bitmap that is visible
        then scales and draws that.

        """
        _bb_world = BBox.as_bbox(self._canvas.viewPortBB)
        _bb_bitmap = BBox.from_points(self.world_to_bitmap(_bb_world))

        _pos = world_to_pixel_func(self.position)
        # figure out subimage:
        # fixme: this should be able to be done more succinctly!

        if _bb_bitmap[0, 0] < 0:
            _xb = 0
        elif _bb_bitmap[0, 0] > self.bmpWH[0]:  # off the bitmap
            _xb = 0
        else:
            _xb = _bb_bitmap[0, 0]
            _pos[0] = 0  # draw at origin

        if _bb_bitmap[0, 1] < 0:
            _yb = 0
        elif _bb_bitmap[0, 1] > self.bmpWH[1]:  # off the bitmap
            _yb = 0
            _should_draw = False
        else:
            _yb = _bb_bitmap[0, 1]
            _pos[1] = 0  # draw at origin

        if _bb_bitmap[1, 0] < 0:
            # off the screen --  This should never happen!
            _wb = 0
        elif _bb_bitmap[1, 0] > self.bmpWH[0]:
            _wb = self.bmpWH[0] - _xb
        else:
            _wb = _bb_bitmap[1, 0] - _xb

        if _bb_bitmap[1, 1] < 0:
            # off the screen --  This should never happen!
            _hb = 0
            _should_draw = False
        elif _bb_bitmap[1, 1] > self.bmpWH[1]:
            _hb = self.bmpWH[1] - _yb
        else:
            _hb = _bb_bitmap[1, 1] - _yb

        _full_height = scale_world_to_pixel_func(self.height)[0]
        _scale = float(_full_height) / float(self.bmpWH[1])
        _ws = int(_scale * _wb + 0.5)  # add the 0.5 to  round
        _hs = int(_scale * _hb + 0.5)
        if self.scaledBitmap is None or self.scaledBitmap[0] != (_xb, _yb, _wb, _hb, _ws, _ws):
            _img = self.image.GetSubImage(wx.Rect(_xb, _yb, _wb, _hb))
            # print("rescaling with High quality")
            _img.Rescale(_ws, _hs, quality=wx.IMAGE_QUALITY_HIGH)
            _bmp = wx.Bitmap(_img)
            # this defines the cached bitmap
            self.scaledBitmap = ((_xb, _yb, _wb, _hb, _ws, _ws), _bmp)
            # fixme: get the shiftfun working!
        else:
            # print("Using cached bitmap")
            # fixme: The cached bitmap could be used if the one needed is the same scale, but
            #       a subset of the cached one.
            _bmp = self.scaledBitmap[1]
        dc.DrawBitmap(_bmp, _pos, True)

        if ht_dc and self.isHitable:
            ht_dc.SetPen(self.hitPen)
            ht_dc.SetBrush(self.hitBrush)
            ht_dc.DrawRectangle(_pos, (_ws, _hs))

    def draw(self, dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc=None):
        _bb_world = BBox.as_bbox(self._canvas.viewPortBB)
        # first see if entire bitmap is displayed:
        if _bb_world.Inside(self.boundingBox):
            # print("Drawing entire bitmap with old code")
            self.draw_entire_bitmap(dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc)
            return None
        elif _bb_world.Overlaps(self.boundingBox):
            # BBbitmap = BBox.fromPoints(self.WorldToBitmap(BBworld))
            # print("Drawing a sub-bitmap")
            self.draw_sub_bitmap(dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc)
        else:
            # print("Not Drawing -- no part of image is showing")
            pass
