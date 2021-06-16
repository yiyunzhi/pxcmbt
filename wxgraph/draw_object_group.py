import six
from .draw_object import DrawObject
import wxgraph.util_bbox as BBox
from .utils import util_color_generator


class DrawObjectGroup(DrawObject):
    """
    A group of other FloatCanvas Objects

    Not all DrawObject methods may apply here.

    Note that if an object is in more than one group, it will get drawn more than once.

    """

    def __init__(self, object_list=[], in_foreground=False, is_visible=True):
        """
        Default class constructor.

        :param  object_list:list a list of :class:`DrawObject` to be grouped
        :param  in_foreground:boolean keep in foreground
        :param  is_visible:boolean keep it visible

        """
        self.objectList = []
        DrawObject.__init__(self, in_foreground, is_visible)

        # this one uses a proprty for _Canvas...
        self._actualCanvas = None

        self.calc_bounding_box()
        for obj in object_list:
            self.add_object(obj)
        self.calc_bounding_box()

    # re-define _Canvas property so that the sub-objects get set up right

    def set_canvas(self, canvas):
        """
        setter for Canvas property
        """
        self._canvas = canvas
        for obj in self.objectList:
            obj.set_canvas(canvas)

    def add_object(self, obj):
        """
        Add an object to the group.

        :param obj:DrawObject  object to add

        """
        self.objectList.append(obj)
        self.boundingBox.merge(obj.boundingBox)

    def add_objects(self, objects):
        """
        Add objects to the group.

        :param  objects:list a list of :class:`DrawObject` to be grouped

        """
        for obj in objects:
            self.add_object(obj)

    def calc_bounding_box(self):
        """
        Calculate the bounding box.
        """
        if self.objectList:
            _bb = BBox.BBox(self.objectList[0].boundingBox).copy()
            for obj in self.objectList[1:]:
                _bb.merge(obj.boundingBox)
        else:
            _bb = BBox.null_bbox()
        self.boundingBox = _bb

    def set_color(self, color):
        """
        Set the Color

        :param color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
         for valid values

        """
        for obj in self.objectList:
            obj.SetColor(color)

    def set_line_color(self, color):
        """
        Set the LineColor

        :param color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
         for valid values

        """
        for obj in self.objectList:
            obj.set_line_color(color)

    def set_line_style(self, line_style):
        """
        Set the LineStyle

        :param line_style: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetLineStyle`
         for valid values

        """
        for obj in self.objectList:
            obj.set_line_style(line_style)

    def set_line_width(self, line_width):
        """
        Set the LineWidth

        :param  line_width:integer line width in pixels

        """
        for obj in self.objectList:
            obj.set_line_width(line_width)

    def set_fill_color(self, color):
        """
        Set the FillColor

        :param color: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetColor`
         for valid values

        """
        for obj in self.objectList:
            obj.set_fill_color(color)

    def set_fill_style(self, fill_style):
        """
        Set the FillStyle

        :param fill_style: see :meth:`~lib.floatcanvas.FloatCanvas.DrawObject.SetFillStyle`
         for valid values

        """
        for obj in self.objectList:
            obj.set_fill_style(fill_style)

    def move(self, delta):
        """
        Moves the object by delta, where delta is a (dx, dy) pair.

        :param delta: is a (dx, dy) pair ideally a `NumPy <http://www.numpy.org/>`_
         array of shape (2, )

        """
        for obj in self.objectList:
            obj.move(delta)
        self.boundingBox += delta

    def bind(self, event, callback_func):
        """
        Bind an event to the Group object

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
        # slight variation on DrawObject Bind Method:
        # fixme: There is a lot of repeated code from the DrawObject method, but
        #   it all needs a lot of cleaning up anyway.
        self.callBackFuncs[event] = callback_func
        self.isHitable = True
        self._canvas.useHitTest = True
        if self.isInForeground and not self._canvas.has_foreground_ht_bitmap():
            self._canvas.make_new_foreground_ht_bitmap()
        elif not self._canvas.has_ht_bitmap() is None:
            self._canvas.make_new_ht_bitmap()
        if not self.hitColor:
            if not self._canvas.hitColorGenerator:
                self._canvas.hitColorGenerator = util_color_generator()
                # first call to prevent the background color from being used.
                if six.PY2:
                    self._canvas.hitColorGenerator.next()
                else:
                    next(self._canvas.hitColorGenerator)
            # Set all contained objects to the same Hit color:
            if six.PY2:
                self.hitColor = self._canvas.hitColorGenerator.next()
            else:
                self.hitColor = next(self._canvas.hitColorGenerator)
        self._change_children_hit_color(self.objectList)
        # put the object in the hit dict, indexed by it's color
        if not self._canvas.hitDict:
            self._canvas.make_hit_dict()
        self._canvas.hitDict[event][self.hitColor] = self

    def _change_children_hit_color(self, obj_list):
        for obj in obj_list:
            obj.set_hit_pen(self.hitColor, self.hitLineWidth)
            obj.set_hit_brush(self.hitColor)
            obj.isHitable = True

            if isinstance(obj, DrawObjectGroup):
                self._change_children_hit_color(obj.objectList)

    def draw(self, dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc=None):
        for obj in self.objectList:
            obj.draw(dc, world_to_pixel_func, scale_world_to_pixel_func, ht_dc)
