# ----------------------------------------------------------------------------
# Name:         wxcanvas.py
# Purpose:
#
# Author:
#
# Created:
# Version:
# Date:
# Licence:
# Tags:         phoenix-port, unittest, documented, py3-port
# ----------------------------------------------------------------------------
"""
This module is reimplemented base on the floatcanvas.

This is the main module of the wxcanvaspackage, it contains the :class:`~lib.floatcanvas.FloatCanvas.FloatCanvas`
and all the all the different objects which are sub-classed from :class:`~lib.floatcanvas.FloatCanvas.DrawObject`.

In the following very simple sample ``self`` is a frame, but it could be another
container type control::

    from wx.lib.wxcanvasimport FloatCanvas

    self.Canvas = FloatCanvas.FloatCanvas(self, -1,
                                 size=(500, 500),
                                 projection_func=None,
                                 debug=0,
                                 background_color="White",
                                 )


    # add a circle
    cir = FloatCanvas.Circle((10, 10), 100)
    self.Canvas.AddObject(cir)

    # add a rectangle
    rect = FloatCanvas.Rectangle((110, 10), (100, 100), FillColor='Red')
    self.Canvas.AddObject(rect)

    self.Canvas.Draw()


Many samples are available in the `wxPhoenix/samples/floatcanvas` folder.

"""
import sys

IS_MAC = sys.platform.startswith("darwin")
try:
    from time import process_time as clock
except ImportError:
    from time import clock
import wx
import six
import numpy as N
from .gui_mode import GUIModeBase
from .draw_object import DrawObject
from .events import *
from .define import GLOBAL_VARS
import wxgraph.util_bbox as BBox


# Custom Exceptions:
class WxCanvasError(Exception):
    """Custom wxcanvasexception."""
    pass


class _GraphEvent(wx.PyCommandEvent):
    """
    This event class takes a regular wxWindows mouse event as a parameter,
    and wraps it so that there is access to all the original methods. This
    is similar to subclassing, but you can't subclass a wxWindows event

    The goal is to be able to it just like a regular mouse event.

    It adds the method:

    get_coords() , which returns an (x,y) tuple in world coordinates.

    Another difference is that it is a CommandEvent, which propagates up
    the window hierarchy until it is handled.

    """

    def __init__(self, event_type, native_event, win_id, coords=None):
        super(_GraphEvent, self).__init__()
        self.SetEventType(event_type)
        self._nativeEvent = native_event
        self.coords = coords

    def get_coords(self):
        return self.coords

    def __getattr__(self, name):
        d = self._getAttrDict()
        if name in d:
            return d[name]
        return getattr(self._nativeEvent, name)


class _GraphScaleEvent(wx.PyCommandEvent):
    """
    This event class takes a regular wxWindows mouse event as a parameter,
    and wraps it so that there is access to all the original methods. This
    is similar to subclassing, but you can't subclass a wxWindows event

    The goal is to be able to it just like a regular PyCommandEvent event.

    It adds the method:

    get_scale() , which returns an scale value of canvas.

    Another difference is that it is a CommandEvent, which propagates up
    the window hierarchy until it is handled.

    """

    def __init__(self, event_type, native_event, win_id, scale=None):
        super(_GraphScaleEvent, self).__init__()
        self.SetEventType(event_type)
        self._nativeEvent = native_event
        self.scale = scale

    def get_scale(self):
        return self.scale

    def __getattr__(self, name):
        d = self._getAttrDict()
        if name in d:
            return d[name]
        return getattr(self._nativeEvent, name)


# ---------------------------------------------------------------------------
class WxCanvas(wx.Panel):
    """
    The main class of the wxcanvas package :class:`~wxcanvas.WxCanvas`.

    """

    def __init__(self, parent, wx_id=-1, size=wx.DefaultSize, projection_func=None,
                 background_color="WHITE", debug=False, **kwargs):

        """
        Default class constructor.

        :param wx.Window `parent`: parent window. Must not be ``None``;
        :param integer `id`: window identifier. A value of -1 indicates a default value;
        :param `size`: a tuple or :class:`wx.Size`
        :param `projection_func`: This allows you to change the transform from
         world to pixel coordinates. We can point to :meth:`~lib.floatcanvas.FloatCanvas.FloatCanvas.flat_earth_projection`
         for an example -- though that should really be a class method, or even
         better, simply a function in the module. There is a tiny bit on info
         in the error message in FloatCanvas.Setprojection_func()

         (Note: this really should get re-factored to allow more generic
         projections...)
        :param string `background_color`: any value accepted by :class:`wx.Brush`
        :param `debug`: activate debug, currently it prints some debugging
         information, could be improved.

        """

        wx.Panel.__init__(self, parent, wx_id, wx.DefaultPosition, size, **kwargs)
        self.compute_font_scale()
        self.init_all()
        self.backgroundBrush = wx.Brush(background_color, wx.SOLID)
        self.enableGC = True
        self.debug = debug
        # bind event
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)

        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_left_double_click)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.on_middle_down)
        self.Bind(wx.EVT_MIDDLE_UP, self.on_middle_up)
        self.Bind(wx.EVT_MIDDLE_DCLICK, self.on_middle_double_click)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down)
        self.Bind(wx.EVT_RIGHT_UP, self.on_right_up)
        self.Bind(wx.EVT_RIGHT_DCLICK, self.on_right_double_click)
        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_wheel)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)

        # todo: I'm leaving these out for now.
        # self.Bind(wx.EVT_ENTER_WINDOW, self. )
        # self.Bind(wx.EVT_LEAVE_WINDOW, self. )

        self.set_projection_func(projection_func)

        # making sure the attribute exists
        self.GUIMode = None

        # timer to give a delay when re-sizing so that buffers aren't re-built too many times.
        self.sizeTimer = wx.PyTimer(self.on_size_timer)

    def init_all(self):
        """
        Sets everything in the Canvas to default state.

        It can be used to reset the Canvas

        """

        self.hitColorGenerator = None
        self.useHitTest = False

        self.numBetweenBlits = 500

        # create the Hit Test Dicts:
        self.hitDict = None
        self._htDC = None

        self._drawList = []
        self._foreDrawList = []
        self.initialize_panel()
        self.make_new_buffers()
        self.boundingBox = BBox.null_bbox()
        self.boundingBoxDirty = False
        self.minScale = None
        self.maxScale = None
        self.viewPortCenter = N.array((0, 0), N.float)

        self.set_projection_func(None)

        self.mapProjectionVector = N.array((1, 1), N.float)  # No Projection to start!
        self.transformVector = N.array((1, -1), N.float)  # default Transformation

        self.scale = 1
        self.objectUnderMouse = None

        self.gridUnder = None
        self.gridOver = None

        self._backgroundDirty = True

    def enable_gc(self, state):
        self.enableGC = state

    def has_foreground_ht_bitmap(self):
        return self._foregroundHTBitmap is not None

    def has_ht_bitmap(self):
        return self._htBitmap is not None

    def get_fore_draw_list(self):
        return self._foreDrawList

    def get_buffer(self):
        return self._buffer

    def get_foreground_buffer(self):
        return self._foregroundBuffer

    @staticmethod
    def compute_font_scale():
        """
        Compute the font scale.

        A global variable to hold the scaling from pixel size to point size.
        """
        _dc = wx.ScreenDC()
        _dc.SetFont(wx.Font(16, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        _x_ext_w, _x_ext_h = _dc.GetTextExtent("X")
        GLOBAL_VARS['FONT_SCALE'] = 16 / _x_ext_w
        del _dc

    def set_projection_func(self, projection_func):
        """
        Set a custom projection function

        :param projection_func: valid entries are ``FlatEarth``, ``None``
          or a callable object that takes the ``ViewPortCenter`` and returns
          ``MapProjectionVector``

        """
        if projection_func == 'FlatEarth':
            self.projection_func = self.flat_earth_projection
        elif callable(projection_func):
            self.projection_func = projection_func
        elif projection_func is None:
            self.projection_func = lambda x=None: N.array((1, 1), N.float)
        else:
            raise WxCanvasError('projection_func must be either:'
                                ' "FlatEarth", None, or a callable object '
                                '(function, for instance) that takes the '
                                'ViewPortCenter and returns a MapProjectionVector')

    def flat_earth_projection(self, center_point):
        """
        Compute the scaling array for the flat-earth projection

        :param center_point: center point of viewport (lon, lat) -- the
         longitude is scaled to the latitude of this point. a 2-tuple, or a
         (2,) `NumPy <http://www.numpy.org/>`_ array of point coordinates

         :returns : a (2,) numpy array that scales world coordinates. This
          scaling is applied when converting to-from world to pixel coordinates.

        """
        _max_latitude = 75  # these were determined essentially arbitrarily
        _min_latitude = -75
        _lat = min(center_point[1], _max_latitude)
        _lat = max(_lat, _min_latitude)
        return N.array((N.cos(N.pi * _lat / 180), 1), N.float)

    def set_mode(self, mode):
        """
        Set the GUImode to any of the available mode.

        :param mode: a valid GUI Mode, out of the box valid modes
         are subclassed from :class:`~lib.floatcanvas.GUIMode.GUIBase` or a mode
         can also be user defined.
        """
        # Set mode
        if self.GUIMode is not None:
            self.GUIMode.unset()  # this lets the old mode clean up.
        mode.canvas = self  # make sure the mode is linked to this canvas
        self.GUIMode = mode
        self.SetCursor(self.GUIMode.cursor)

    def make_hit_dict(self):
        """
        Initialize the Hit dictonary.
        """
        # fixme: Should this just be None if nothing has been bound?
        self.hitDict = {EVT_FC_LEFT_DOWN: {},
                        EVT_FC_LEFT_UP: {},
                        EVT_FC_LEFT_DCLICK: {},
                        EVT_FC_MIDDLE_DOWN: {},
                        EVT_FC_MIDDLE_UP: {},
                        EVT_FC_MIDDLE_DCLICK: {},
                        EVT_FC_RIGHT_DOWN: {},
                        EVT_FC_RIGHT_UP: {},
                        EVT_FC_RIGHT_DCLICK: {},
                        EVT_FC_ENTER_OBJECT: {},
                        EVT_FC_LEAVE_OBJECT: {},
                        }

    def raise_graph_event(self, event, event_type):
        """
        This is called in various other places to raise a Mouse Event.
        """
        _pt = self.pixel_to_world(event.GetPosition())
        _evt = _GraphEvent(event_type, event, self.GetId(), _pt)
        self.GetEventHandler().ProcessEvent(_evt)

    if wx.__version__ >= "2.8":
        hitTestBitmapDepth = 32

        # print("Using hit test code for 2.8")
        def get_hit_test_color(self, pos):
            """
            Get the hit test colour

            :param pos: the position to get the hit test colour for
            """
            if self._foregroundHTBitmap:
                _pdata = wx.AlphaPixelData(self._foregroundHTBitmap)
            else:
                _pdata = wx.AlphaPixelData(self._htBitmap)
            if not _pdata:
                raise RuntimeError("Trouble Accessing Hit Test bitmap")
            _pacc = _pdata.GetPixels()
            _pacc.MoveTo(_pdata, pos[0], pos[1])
            return _pacc.Get()[:3]
    else:
        hitTestBitmapDepth = 24

        # print("using pre-2.8 hit test code")
        def get_hit_test_color(self, pos):
            """
            Get the hit test colour

            :param pos: the position to get the hit test colour for
            """
            _dc = wx.MemoryDC()
            if self._foregroundHTBitmap:
                _dc.SelectObject(self._foregroundHTBitmap)
            else:
                _dc.SelectObject(self._htBitmap)
            _hit_color = _dc.GetPixel(*pos)
            return _hit_color.Get()

    def unbind_all(self):
        """
        Removes all bindings to Objects.
        """
        self.hitDict = None

    def _call_hit_callback(self, object, pos, hit_event):
        """
        A little book keeping to be done when a callback is called.
        """
        object.hitCoords = self.pixel_to_world(pos)
        object.hitCoordsPixel = pos
        object.callBackFuncs[hit_event](object)

    def HitTest(self, event, hit_event):
        """Check if any objects in the dict for this event."""
        if self.hitDict:
            if hit_event in self.hitDict:
                _pos = event.GetPosition()
                _color = self.get_hit_test_color(_pos)
                if _color in self.hitDict[hit_event]:
                    _object = self.hitDict[hit_event][_color]
                    self._call_hit_callback(_object, _pos, hit_event)
                    return True
            return False

    def mouse_over_test(self, event):
        """
        Check if mouse is over an object.
        """
        # fixme: Can this be cleaned up?
        if self.hitDict and (self.hitDict[EVT_FC_ENTER_OBJECT] or self.hitDict[EVT_FC_LEAVE_OBJECT]):
            _pos = event.GetPosition()
            _color = self.get_hit_test_color(_pos)
            _old_object = self.objectUnderMouse
            _object_callback_called = False
            if _color in self.hitDict[EVT_FC_ENTER_OBJECT]:
                _object = self.hitDict[EVT_FC_ENTER_OBJECT][_color]
                if _old_object is None:
                    try:
                        self._call_hit_callback(_object, _pos, EVT_FC_ENTER_OBJECT)
                        _object_callback_called = True
                    except KeyError:
                        # this means the enter event isn't bound for that object
                        pass
                elif _old_object == _object:  # the mouse is still on the same object
                    pass
                    # Is the mouse on a different object as it was...
                elif not (_object == _old_object):
                    # call the leave object callback
                    try:
                        self._call_hit_callback(_old_object, _pos, EVT_FC_LEAVE_OBJECT)
                        _object_callback_called = True
                    except KeyError:
                        pass  # this means the leave event isn't bound for that object
                    try:
                        self._call_hit_callback(_object, _pos, EVT_FC_ENTER_OBJECT)
                        _object_callback_called = True
                    except KeyError:
                        pass  # this means the enter event isn't bound for that object
                    # set the new object under mouse
                self.objectUnderMouse = _object
            elif _color in self.hitDict[EVT_FC_LEAVE_OBJECT]:
                _object = self.hitDict[EVT_FC_LEAVE_OBJECT][_color]
                self.objectUnderMouse = _object
            else:
                # no objects under mouse bound to mouse-over events
                self.objectUnderMouse = None
                if _old_object:
                    try:
                        # Add the hit coords to the Object
                        self._call_hit_callback(_old_object, _pos, EVT_FC_LEAVE_OBJECT)
                        _object_callback_called = True
                    except KeyError:
                        pass  # this means the leave event isn't bound for that object
            return _object_callback_called
        return False

    # fixme: There is a lot of repeated code here
    #    Is there a better way?
    #    probably -- shouldn't there always be a GUIMode?
    #    there could be a null GUI Mode, and use that instead of None
    def on_left_double_click(self, event):
        """
        Left double click event.
        """
        if self.GUIMode:
            self.GUIMode.on_left_double_click(event)
        event.Skip()

    def on_middle_down(self, event):
        """
        Middle down event.
        """
        if self.GUIMode:
            self.GUIMode.on_middle_down(event)
        event.Skip()

    def on_middle_up(self, event):
        """
        Middle up event.
        """
        if self.GUIMode:
            self.GUIMode.on_middle_up(event)
        event.Skip()

    def on_middle_double_click(self, event):
        """
        Middle double click event.
        """
        if self.GUIMode:
            self.GUIMode.on_middle_double_click(event)
        event.Skip()

    def on_right_double_click(self, event):
        """
        Right double click event.
        """
        if self.GUIMode:
            self.GUIMode.on_right_double_click(event)
        event.Skip()

    def on_wheel(self, event):
        """
        Wheel event.
        """
        if self.GUIMode:
            self.GUIMode.on_wheel(event)
        event.Skip()

    def on_left_down(self, event):
        """
        Left down event.
        """
        if self.GUIMode:
            self.GUIMode.on_left_down(event)
        event.Skip()

    def on_left_up(self, event):
        """
        Left up event.
        """
        if self.HasCapture():
            self.ReleaseMouse()
        if self.GUIMode:
            self.GUIMode.on_left_up(event)
        event.Skip()

    def on_motion(self, event):
        """
        Motion event.
        """
        if self.GUIMode:
            self.GUIMode.on_motion(event)
        event.Skip()

    def on_right_down(self, event):
        """
        Right down event.
        """
        if self.GUIMode:
            self.GUIMode.on_right_down(event)
        event.Skip()

    def on_right_up(self, event):
        """
        Right up event.
        """
        if self.GUIMode:
            self.GUIMode.on_right_up(event)
        event.Skip()

    def on_key_down(self, event):
        """
        Key down event.
        """
        if self.GUIMode:
            self.GUIMode.on_key_down(event)
        event.Skip()

    def on_key_up(self, event):
        """
        Key up event.
        """
        if self.GUIMode:
            self.GUIMode.on_key_up(event)
        event.Skip()

    def make_new_buffers(self):
        """
        Make a new buffer.
        """
        # fixme: this looks like tortured logic!
        self._backgroundDirty = True
        # Make new offscreen bitmap:
        self._buffer = wx.Bitmap(*self.panelSize)
        if self._foreDrawList:
            self._foregroundBuffer = wx.Bitmap(*self.panelSize)
            if self.useHitTest:
                self.make_new_foreground_ht_bitmap()
            else:
                self._foregroundHTBitmap = None
        else:
            self._foregroundBuffer = None
            self._foregroundHTBitmap = None

        if self.useHitTest:
            self.make_new_ht_bitmap()
        else:
            self._htBitmap = None
            self._foregroundHTBitmap = None

    def put_object_in_background(self, obj):
        self._foreDrawList.remove(obj)
        self._drawList.append(obj)
        self._backgroundDirty = True

    def put_object_in_foreground(self, obj):
        self._foreDrawList.append(obj)
        self._drawList.remove(obj)
        self._backgroundDirty = True

    def make_new_ht_bitmap(self):
        """
        Off screen Bitmap used for Hit tests on background objects

        """
        self._htBitmap = wx.Bitmap(self.panelSize[0],
                                   self.panelSize[1],
                                   depth=self.hitTestBitmapDepth)

    def make_new_foreground_ht_bitmap(self):
        # Note: the foreground and backround HT bitmaps are in separate functions
        #       so that they can be created separate --i.e. when a foreground is
        #       added after the background is drawn
        """
        Off screen Bitmap used for Hit tests on foreground objects

        """
        self._foregroundHTBitmap = wx.Bitmap(self.panelSize[0],
                                             self.panelSize[1],
                                             depth=self.hitTestBitmapDepth)

    def on_size(self, event=None):
        """
        On size handler.
        """
        self.initialize_panel()
        self.sizeTimer.Start(50, oneShot=True)

    def on_size_timer(self, event=None):
        """
        On size timer handler.
        """
        self.make_new_buffers()
        self.draw()

    def initialize_panel(self):
        """
        Initialize the panel.
        """
        _panelSize = N.array(self.GetClientSize(), N.int32)
        # OS-X sometimes gives a Size event when the panel is size (0,0)
        self.panelSize = N.maximum(_panelSize, (2, 2))
        # lrk: added for speed in WorldToPixel
        self.halfPanelSize = self.panelSize / 2
        self.aspectRatio = float(self.panelSize[0]) / self.panelSize[1]

    def on_paint(self, event):
        """
        On paint handler.
        """
        _dc = wx.PaintDC(self)
        _dc.Clear()
        if self.enableGC:
            _dc = wx.GCDC(_dc)
        if self._foregroundBuffer:
            _dc.DrawBitmap(self._foregroundBuffer, 0, 0)
        else:
            _dc.DrawBitmap(self._buffer, 0, 0)
        # this was so that rubber band boxes and the like could get drawn here
        #  but it looks like a wx.ClientDC is a better bet still.
        # try:
        #    self.GUIMode.DrawOnTop(dc)
        # except AttributeError:
        #    pass

    def draw(self, force=False):
        """

        Canvas.draw(force=False)

        Re-draws the canvas.

        Note that the buffer will not be re-drawn unless something has
        changed. If you change a DrawObject directly, then the canvas
        will not know anything has changed. In this case, you can force
        a re-draw by passing int True for the Force flag:

        Canvas.Draw(Force=True)

        There is a main buffer set up to double buffer the screen, so
        you can get quick re-draws when the window gets uncovered.

        If there are any objects in self._foreDrawList, then the
        background gets drawn to a new buffer, and the foreground
        objects get drawn on top of it. The final result if blitted to
        the screen, and stored for future Paint events.  This is done so
        that you can have a complicated background, but have something
        changing on the foreground, without having to wait for the
        background to get re-drawn. This can be used to support simple
        animation, for instance.

        """

        if N.sometrue(self.panelSize <= 2):
            # it's possible for this to get called before being properly initialized.
            return
        if self.debug: _t_start = clock()
        _screen_dc = wx.ClientDC(self)
        _viewport_world = N.array((self.pixel_to_world((0, 0)), self.pixel_to_world(self.panelSize)))
        self.viewPortBB = N.array((N.minimum.reduce(_viewport_world), N.maximum.reduce(_viewport_world)))
        _mdc = wx.MemoryDC()
        _mdc.SelectObject(self._buffer)
        if self.enableGC:
            _dc = wx.GCDC(_mdc)
        else:
            _dc = _mdc
        if self._backgroundDirty or force:
            _dc.SetBackground(self.backgroundBrush)
            _dc.Clear()
            if self._htBitmap is not None:
                _ht_mdc = wx.MemoryDC()
                _ht_mdc.SelectObject(self._htBitmap)
                if self.enableGC:
                    _ht_dc = wx.GCDC(_ht_mdc)
                else:
                    _ht_dc = _ht_mdc
                _ht_dc.Clear()
            else:
                _ht_dc = None
            if self.gridUnder is not None:
                self.gridUnder.draw(_dc, self)
            self._draw_objects(_dc, self._drawList, _screen_dc, self.viewPortBB, _ht_dc)
            self._backgroundDirty = False
            del _ht_dc

        if self._foreDrawList:
            # If an object was just added to the Foreground, there might not yet be a buffer
            if self._foregroundBuffer is None:
                self._foregroundBuffer = wx.Bitmap(self.panelSize[0], self.panelSize[1])
            # I got some strange errors (linewidths wrong) if I didn't make a new DC here
            _mdc = wx.MemoryDC()
            _mdc.SelectObject(self._foregroundBuffer)
            _dc.DrawBitmap(self._buffer, 0, 0)
            if self._foregroundHTBitmap is not None:
                _foreground_ht_mdc = wx.MemoryDC()
                _foreground_ht_mdc.SelectObject(self._foregroundHTBitmap)
                _foreground_ht_dc = wx.GCDC(_foreground_ht_mdc)
                _foreground_ht_dc.Clear()
                if self._htBitmap is not None:
                    # Draw the background HT buffer to the foreground HT buffer
                    _foreground_ht_dc.DrawBitmap(self._htBitmap, 0, 0)
            else:
                _foreground_ht_dc = None
            self._draw_objects(_dc,
                               self._foreDrawList,
                               _screen_dc,
                               self.viewPortBB,
                               _foreground_ht_dc)
        if self.gridOver is not None:
            self.gridOver.draw(_dc, self)
        _screen_dc.Blit(0, 0, self.panelSize[0], self.panelSize[1], _mdc, 0, 0)
        # If the canvas is in the middle of a zoom or move,
        # the Rubber Band box needs to be re-drawn
        # fixme: maybe GUIModes should never be None, and rather have a Do-nothing GUI-Mode.
        if self.GUIMode is not None:
            self.GUIMode.update_screen()

        if self.debug:
            print("Drawing took %f seconds of CPU time" % (clock() - _t_start))
            if self._htBitmap is not None:
                self._htBitmap.SaveFile('junk.png', wx.BITMAP_TYPE_PNG)

        # Clear the font cache. If you don't do this, the X font server
        # starts to take up Massive amounts of memory This is mostly a
        # problem with very large fonts, that you get with scaled text
        # when zoomed in.
        DrawObject.fontList = {}

    @staticmethod
    def _should_redraw(draw_list, viewport_bb):
        # lrk: Returns the objects that should be redrawn
        # fixme: should this check be moved into the object?
        _bb = viewport_bb
        _redraw_list = []
        for obj in draw_list:
            if obj.boundingBox.overlaps(_bb):
                _redraw_list.append(obj)
        return _redraw_list

    def move_image(self, shift, coord_type, redraw=True):
        """
        Move the image in the window.

        :param shift: tuple ` is an (x, y) tuple defining amount to shift in
         each direction
        :param coord_type: defines what coordinates to use, valid entries
        :param redraw: bool, if canvas should be redrawed

         ============== ======================================================
         Coordtype      Description
         ============== ======================================================
         `Panel`        shift the image by some fraction of the size of the
                        displayed image
         `Pixel`        shift the image by some number of pixels
         `World`        shift the image by an amount of floating point world
                        coordinates
         ============== ======================================================

        """
        # todo: coord type in enum defined
        shift = N.asarray(shift, N.float)
        if coord_type.lower() == 'panel':  # convert from panel coordinates
            shift = shift * N.array((-1, 1), N.float) * self.panelSize / self.transformVector
        elif coord_type.lower() == 'pixel':  # convert from pixel coordinates
            shift = shift / self.transformVector
        elif coord_type.lower() == 'world':  # No conversion
            pass
        else:
            raise WxCanvasError('CoordType must be either "Panel", "Pixel", or "World"')

        self.viewPortCenter = self.viewPortCenter + shift
        self.mapProjectionVector = self.projection_func(self.viewPortCenter)
        self.transformVector = N.array((self.scale, -self.scale), N.float) * self.mapProjectionVector
        self._backgroundDirty = True
        if redraw:
            self.draw()

    def zoom(self, factor, center=None, center_coords="World", keep_point_in_place=False):
        """
        Zoom(factor, center) changes the amount of zoom of the image by factor.
        If factor is greater than one, the image gets larger.
        If factor is less than one, the image gets smaller.
        :param factor: amount to zoom in or out If factor is greater than one,
                       the image gets larger. If factor is less than one, the
                       image gets smaller.
        :param center: a tuple of (x,y) coordinates of the center of the viewport,
                       after zooming. If center is not given, the center will stay the same.

        :param center_coords: flag indicating whether the center given is in pixel or world
                             coords. Options are: "World" or "Pixel"
        :param keep_point_in_place: boolean flag. If False, the center point is what's given.
                                 If True, the image is shifted so that the given center point
                                 is kept in the same pixel space. This facilitates keeping the
                                 same point under the mouse when zooming with the scroll wheel.
        """
        if center is None:
            center = self.viewPortCenter
            center_coords = 'World'  # override input if they don't give a center point.

        if center_coords.lower() == "pixel":
            _old_point = self.pixel_to_world(center)
        elif center_coords.lower() == 'world':
            _old_point = N.array(center, N.float)
        else:
            raise WxCanvasError('centerCoords must be either "World" or "Pixel"')

        self.scale = self.scale * factor
        if keep_point_in_place:
            self.set_to_new_scale(False)

            if center_coords.lower() == "pixel":
                _new_point = self.pixel_to_world(center)
            else:
                _new_point = N.array(center, N.float)
            _delta = (_new_point - _old_point)
            self.move_image(-_delta, 'World')
        else:
            self.viewPortCenter = _old_point
            self.set_to_new_scale()

    def zoom_to_bb(self, new_bb=None, draw_flag=True):

        """

        Zooms the image to the bounding box given, or to the bounding
        box of all the objects on the canvas, if none is given.

        """
        if new_bb is not None:
            _bounding_box = new_bb
        else:
            if self.boundingBoxDirty:
                self._reset_bounding_box()
            _bounding_box = self.boundingBox
        if _bounding_box is not None and not _bounding_box.IsNull():
            self.viewPortCenter = N.array(((_bounding_box[0, 0] + _bounding_box[1, 0]) / 2,
                                           (_bounding_box[0, 1] + _bounding_box[1, 1]) / 2), N.float_)
            self.mapProjectionVector = self.projection_func(self.viewPortCenter)
            # Compute the new Scale
            _bounding_box = _bounding_box * self.mapProjectionVector  # this does need to make a copy!
            try:
                self.scale = min(abs(self.panelSize[0] / (_bounding_box[1, 0] - _bounding_box[0, 0])),
                                 abs(self.panelSize[1] / (_bounding_box[1, 1] - _bounding_box[0, 1]))) * 0.95
            except ZeroDivisionError:  # this will happen if the BB has zero width or height
                try:  # width == 0
                    self.scale = (self.panelSize[0] / (_bounding_box[1, 0] - _bounding_box[0, 0])) * 0.95
                except ZeroDivisionError:
                    try:  # height == 0
                        self.scale = (self.panelSize[1] / (_bounding_box[1, 1] - _bounding_box[0, 1])) * 0.95
                    except ZeroDivisionError:  # zero size! (must be a single point)
                        self.scale = 1

            if draw_flag:
                self._backgroundDirty = True
        else:
            # Reset the shifting and scaling to defaults when there is no BB
            self.viewPortCenter = N.array((0, 0), N.float)
            self.scale = 1
        self.set_to_new_scale(draw_flag=draw_flag)

    def set_to_new_scale(self, draw_flag=True):
        """
        Set to the new scale

        :param draw_flag: boolean draw the canvas

        """
        _scale = self.scale
        if self.minScale is not None:
            _scale = max(_scale, self.minScale)
        if self.maxScale is not None:
            _scale = min(_scale, self.maxScale)
        self.mapProjectionVector = self.projection_func(self.viewPortCenter)
        self.transformVector = N.array((_scale, -_scale), N.float) * self.mapProjectionVector
        self.scale = _scale
        self._backgroundDirty = True
        if draw_flag:
            self.draw()
        _evt = _GraphScaleEvent(EVT_FC_SCALE_CHANGED, EVT_SCALE_CHANGED, self.GetId(), self.scale)
        self.GetEventHandler().ProcessEvent(_evt)

    def remove_objects(self, objects):
        """"
        Remove objects from canvas

        :param objects: list ` a list of :class:`DrawObjects` to remove

        """
        for obj in objects:
            self.remove_object(obj, reset_bb=False)
        self.boundingBoxDirty = True

    def remove_object(self, obj, reset_bb=True):
        """"
        Remove object from canvas

        :param obj:DrawObject ` a :class:`DrawObjects` to remove
        :param reset_bb: boolean reset the bounding box

        """
        # fixme: Using the list.remove method is kind of slow
        if obj.inForeground:
            self._foreDrawList.remove(obj)
            if not self._foreDrawList:
                self._foregroundBuffer = None
                self._foregroundHTdc = None
        else:
            self._drawList.remove(obj)
            self._backgroundDirty = True
        if reset_bb:
            self.boundingBoxDirty = True

    def clear_all(self, reset_bb=True):
        """
        ClearAll(ResetBB=True)

        Removes all DrawObjects from the Canvas

        If ResetBB is set to False, the original bounding box will remain

        """
        self._drawList = []
        self._foreDrawList = []
        self._backgroundDirty = True
        self.hitColorGenerator = None
        self.useHitTest = False
        if reset_bb:
            self._reset_bounding_box()
        self.make_new_buffers()
        self.hitDict = None

    def _reset_bounding_box(self):
        _set_to_null = False
        if self._drawList or self._foreDrawList:
            _bb_list = []
            for obj in self._drawList + self._foreDrawList:
                if not obj.BoundingBox.IsNull():
                    _bb_list.append(obj.BoundingBox)
            if _bb_list:  # if there are only NullBBoxes in DrawLists
                self.boundingBox = BBox.from_bb_array(_bb_list)
            else:
                _set_to_null = True
            if self.boundingBox.Width == 0 or self.boundingBox.Height == 0:
                _set_to_null = True
        else:
            _set_to_null = True
        if _set_to_null:
            self.boundingBox = BBox.null_bbox()
            self.viewPortCenter = N.array((0, 0), N.float)
            self.transformVector = N.array((1, -1), N.float)
            self.mapProjectionVector = N.array((1, 1), N.float)
            self.scale = 1
        self.boundingBoxDirty = False

    def pixel_to_world(self, points):
        """
        Converts coordinates from Pixel coordinates to world coordinates.

        Points is a tuple of (x,y) coordinates, or a list of such tuples,
        or a NX2 Numpy array of x,y coordinates.

        """
        return (((N.asarray(points, N.float) -
                  (self.panelSize / 2)) / self.transformVector) +
                self.viewPortCenter)

    def world_to_pixel(self, coordinates):
        """
        This function will get passed to the drawing functions of the objects,
        to transform from world to pixel coordinates.
        Coordinates should be a NX2 array of (x,y) coordinates, or
        a 2-tuple, or sequence of 2-tuples.
        """
        # Note: this can be called by users code for various reasons, so N.asarray is needed.
        return (((N.asarray(coordinates, N.float) -
                  self.viewPortCenter) * self.transformVector) + self.halfPanelSize).astype('i')

    def scale_world_to_pixel(self, lengths):
        """
        This function will get passed to the drawing functions of the objects,
        to Change a length from world to pixel coordinates.

        Lengths should be a NX2 array of (x,y) coordinates, or
        a 2-tuple, or sequence of 2-tuples.
        """
        return (N.asarray(lengths, N.float) * self.transformVector).astype('i')

    def scale_pixel_to_world(self, lengths):
        """
        This function computes a pair of x.y lengths,
        to change then from pixel to world coordinates.

        Lengths should be a NX2 array of (x,y) coordinates, or
        a 2-tuple, or sequence of 2-tuples.
        """
        return N.asarray(lengths, N.float) / self.transformVector

    def add_object(self, obj):
        """
        Add an object to the canvas

        :param  obj: DrawObject the object to add

        :return: DrawObject

        """
        # put in a reference to the Canvas, so remove and other stuff can work
        obj.set_canvas(self)
        if obj.isInForeground:
            self._foreDrawList.append(obj)
            self.useForeground = True
        else:
            self._drawList.append(obj)
            self._backgroundDirty = True
        self.boundingBoxDirty = True
        return obj

    def add_objects(self, objects):
        """
        Add objects to the canvas

        :param  objects: list a list of :class:`DrawObject`

        """
        for obj in objects:
            self.add_object(obj)

    def _draw_objects(self, dc, draw_list, screen_dc, viewport_bb, ht_dc=None):
        """
        This is a convenience function;

        This function takes the list of objects and draws them to specified
        device context.
        """
        dc.SetBackground(self.backgroundBrush)
        # i = 0
        _panel_w, _panel_h = self.panelSize  # for speed
        _func_world_to_pixel = self.world_to_pixel  # for speed
        _func_scale_world_to_pixel = self.scale_world_to_pixel  # for speed
        _func_blit = screen_dc.Blit  # for speed
        _num_between_blits = self.numBetweenBlits  # for speed
        for i, obj in enumerate(self._should_redraw(draw_list, viewport_bb)):
            if obj.isVisible:
                obj.draw(dc, _func_world_to_pixel, _func_scale_world_to_pixel, ht_dc)
                if (i + 1) % _num_between_blits == 0:
                    _func_blit(0, 0, _panel_w, _panel_h, dc, 0, 0)

    def save_as_image(self, file_name, image_type=wx.BITMAP_TYPE_PNG):
        """
        Saves the current image as an image file.

        :param file_name: string the name of the image file
        :param image_type: format to use, see :ref:`wx.BitmapType` and the note in
         :meth:`wx.Bitmap.SaveFile`

        """

        self._buffer.SaveFile(file_name, image_type)
