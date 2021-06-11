import numpy as N
from wxgraph.gui_mode import GUIModeBase, GraphCursors
from wxgraph.events import *
import wxgraph.util_bbox as bbox
from .shape_state_node import StateNodeShape, FinalStateNodeShape, InitStateNodeShape
from .shape_note_node import NoteNodeShape
from .define_gui import *


# some mix-ins for use with the other modes:
class GUIModeZoomWithMouseWheelMixin:
    def on_wheel(self, event: wx.MouseEvent):
        _scale = self.canvas.scale
        _scale += event.GetWheelRotation() / (event.GetWheelDelta() * 10)
        _pos = event.GetPosition()
        if event.ControlDown():
            if _scale < self.canvas.minScale: _scale = self.canvas.minScale
            if _scale > self.canvas.maxScale: _scale = self.canvas.maxScale
            self.canvas.zoom(_scale / self.canvas.scale, _pos, center_coords="Pixel", keep_point_in_place=True)
        super(GUIModeZoomWithMouseWheelMixin, self).on_wheel(event)


class GUIModePlace(GUIModeBase):
    def __init__(self, shape_type=None, canvas=None):
        GUIModeBase.__init__(self, canvas)
        self._shapeType = shape_type
        self._isShapeTypeReady = False

    def _add_item(self, item):
        _canvas_parent = self.canvas.GetParent()
        if item is None:
            return
        _obj = self.canvas.add_object(item)
        if _canvas_parent is not None:
            _obj.bind(EVT_FC_LEFT_DOWN, _canvas_parent.on_left_down_item)
            _obj.bind(EVT_FC_LEFT_UP, _canvas_parent.on_left_up_item)
            _obj.bind(EVT_FC_ENTER_OBJECT, _canvas_parent.on_enter_item)
            _obj.bind(EVT_FC_LEAVE_OBJECT, _canvas_parent.on_leave_item)
        self.canvas.draw()

    def set_shape_type(self, shape_type):
        self._shapeType = shape_type

    def on_left_down(self, event):
        self._isShapeTypeReady = self._shapeType is not None
        super(GUIModePlace, self).on_left_down(event)

    def on_left_up(self, event: wx.MouseEvent):
        _pos = event.GetPosition()
        _world_pos = wx.RealPoint(self.canvas.pixel_to_world(_pos))
        if self._isShapeTypeReady:
            _item = None
            if self._shapeType == EnumCanvasToolbarMode.STATE:
                _item = StateNodeShape(_world_pos, 'Untitled State')
            elif self._shapeType == EnumCanvasToolbarMode.INIT_STATE:
                _item = InitStateNodeShape(_world_pos)
            elif self._shapeType == EnumCanvasToolbarMode.SUB_STATE:
                _item = None
            elif self._shapeType == EnumCanvasToolbarMode.FINAL_STATE:
                _item = FinalStateNodeShape(_world_pos)
            elif self._shapeType == EnumCanvasToolbarMode.NOTE:
                _str = "This is a note component.\nyou could add more text\n..."
                _item = NoteNodeShape(_world_pos, _str)
            if _item is not None:
                self._add_item(_item)
            self._isShapeTypeReady = False
        super(GUIModePlace, self).on_left_up(event)


class GUIModeConnection(GUIModeBase):
    def __init__(self, canvas=None):
        GUIModeBase.__init__(self, canvas)


class GUIModeMouse(GUIModeZoomWithMouseWheelMixin, GUIModeBase):
    """

    Mouse mode checks for a hit test, and if nothing is hit,
    raises a FloatCanvas mouse event for each event.

    """

    def __init__(self, canvas=None):
        GUIModeBase.__init__(self, canvas)
        self.item = None
        self.orgPos = None
        self.curPos = None
        self.inWires = None
        self.outWires = None
        self.panCursor = self.cursors.handCursor
        self.panGrabCursor = self.cursors.grabHandCursor
        self.panStartMove = None
        self.panMidMove = None
        self.panPrevMoveXY = None
        self.panEndMove = None
        self.panMoveTimer = wx.PyTimer(self.on_pan_move_timer)
        self.panRedrawDelayMs = 10

    def _update_position(self, pos):
        self.orgPos = self.curPos
        self.curPos = pos

    def _get_position_diff(self, reverse=False):
        if self.orgPos is None or self.curPos is None:
            return 0, 0
        if reverse:
            return self.orgPos - self.curPos
        return self.curPos - self.orgPos

    def on_pan_move_timer(self):
        self.canvas.draw()

    # Handlers
    def on_left_down(self, event):
        _pos = event.GetPosition()
        _world_pos = wx.RealPoint(self.canvas.pixel_to_world(_pos))
        _hit_object = self.canvas.objectUnderMouse
        if _hit_object is not None:
            self.item = _hit_object
            self.orgPos = _world_pos
            self.curPos = _world_pos
        super(GUIModeMouse, self).on_left_down(event)

    def on_left_up(self, event):
        if self.item is not None:
            self.item = None
            self.curPos = None
            self.orgPos = None
        super(GUIModeMouse, self).on_left_up(event)

    def on_middle_down(self, event):
        self.canvas.SetCursor(self.panGrabCursor)
        self.panStartMove = N.array(event.GetPosition())
        self.panMidMove = self.panStartMove
        self.panPrevMoveXY = (0, 0)
        super(GUIModeMouse, self).on_middle_down(event)

    def on_middle_up(self, event):
        self.canvas.SetCursor(self.cursor)
        if self.panStartMove is not None:
            self.panEndMove = N.array(event.GetPosition())
            _diff_move = self.panMidMove - self.panEndMove
            self.canvas.move_image(_diff_move, 'Pixel', redraw=True)
        super(GUIModeMouse, self).on_middle_up(event)

    def on_motion(self, event: wx.MouseEvent):
        _pos = event.GetPosition()
        _world_pos = wx.RealPoint(self.canvas.pixel_to_world(_pos))
        if event.Dragging():
            if event.LeftIsDown():
                if self.item is not None:
                    self._update_position(_world_pos)
                    self.item.move(self._get_position_diff())
                    self.canvas.draw(True)
            elif event.MiddleIsDown() and self.panStartMove is not None:
                self.panEndMove = N.array(_pos)
                _diff_move = self.panMidMove - self.panEndMove
                # reset the canvas without re-drawing
                self.canvas.move_image(_diff_move, 'Pixel', redraw=False)
                self.panMidMove = self.panEndMove
                self.panMoveTimer.Start(self.panRedrawDelayMs, oneShot=True)
        super(GUIModeMouse, self).on_motion(event)

    def update_screen(self):
        # The screen has been re-drawn, so StartMove needs to be reset.
        self.panStartMove = self.panMidMove
