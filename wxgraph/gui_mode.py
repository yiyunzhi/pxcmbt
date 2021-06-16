# ----------------------------------------------------------------------------
# Name:         GUIMode.py
# Purpose:
#
# Author:
#
# Created:
# Version:
# Date:
# Licence:
# Tags:         phoenix-port
# ----------------------------------------------------------------------------
"""

Module that holds the GUI modes used by FloatCanvas

Note that this can only be imported after a wx.App() has been created.

This approach was inspired by Christian Blouin, who also wrote the initial
version of the code.

"""

import wx
import numpy as N
from .events import *
from .util_bbox import BBox
import wxgraph.ressources as resources


class GraphCursors(object):
    """
    Class to hold the standard Cursors

    """

    def __init__(self):
        if "wxMac" in wx.PlatformInfo:  # use 16X16 cursors for wxMac
            self.handCursor = wx.Cursor(resources.get_hand_16_image())
            self.grabHandCursor = wx.Cursor(resources.get_grab_hand_16_image())

            _img = resources.get_mag_plus_16_image()
            _img.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 6)
            _img.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 6)
            self.magPlusCursor = wx.Cursor(_img)

            _img = resources.get_mag_minus_16_image()
            _img.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 6)
            _img.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 6)
            self.magMinusCursor = wx.Cursor(_img)
        else:  # use 24X24 cursors for GTK and Windows
            self.handCursor = wx.Cursor(resources.get_hand_image())
            self.grabHandCursor = wx.Cursor(resources.get_grab_hand_image())

            _img = resources.get_mag_plus_image()
            _img.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 9)
            _img.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 9)
            self.magPlusCursor = wx.Cursor(_img)

            _img = resources.get_mag_minus_image()
            _img.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 9)
            _img.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 9)
            self.magMinusCursor = wx.Cursor(_img)


class GUIModeBase(object):
    """
    Basic Mouse mode and baseclass for other GUImode.

    This one does nothing with any event

    """

    def __init__(self, canvas=None):
        """
        Default class constructor.

        :param canvas: the canvas the GUI mode is attached too

        """
        # set the FloatCanvas for the mode
        # it gets set when the Mode is set on the Canvas.
        self.canvas = canvas
        self.cursors = GraphCursors()
        self.cursor = wx.NullCursor
        self.blockGraphEvent = False

    def _fire_graph_event(self, event, event_type):
        if self.blockGraphEvent:
            return
        if not self.canvas.HitTest(event, event_type):
            self.canvas.raise_graph_event(event, event_type)

    def unset(self):
        """
        this method gets called by canvas when a new mode is being set
        on the Canvas
        """
        pass

    def on_left_down(self, event):
        _event_type = EVT_FC_LEFT_DOWN
        self._fire_graph_event(event, _event_type)

    def on_left_up(self, event):
        _event_type = EVT_FC_LEFT_UP
        self._fire_graph_event(event, _event_type)

    def on_left_double_click(self, event):
        _event_type = EVT_FC_LEFT_DCLICK
        self._fire_graph_event(event, _event_type)

    def on_middle_down(self, event):
        _event_type = EVT_FC_MIDDLE_DOWN
        self._fire_graph_event(event, _event_type)

    def on_middle_up(self, event):
        _event_type = EVT_FC_MIDDLE_UP
        self._fire_graph_event(event, _event_type)

    def on_middle_double_click(self, event):
        _event_type = EVT_FC_MIDDLE_DCLICK
        self._fire_graph_event(event, _event_type)

    def on_right_down(self, event):
        _event_type = EVT_FC_RIGHT_DOWN
        self._fire_graph_event(event, _event_type)

    def on_right_up(self, event):
        _event_type = EVT_FC_RIGHT_UP
        self._fire_graph_event(event, _event_type)

    def on_right_double_click(self, event):
        _event_type = EVT_FC_RIGHT_DCLICK
        self._fire_graph_event(event, _event_type)

    def on_wheel(self, event):
        _event_type = EVT_FC_MOUSEWHEEL
        self._fire_graph_event(event, _event_type)

    def on_motion(self, event):
        if self.blockGraphEvent:
            return
        # The Move event always gets raised, even if there is a hit-test
        _event_type = EVT_FC_MOTION
        # process the object hit test for EVT_MOTION bindings
        self.canvas.HitTest(event, _event_type)
        # process enter and leave events
        self.canvas.mouse_over_test(event)
        # then raise the event on the canvas
        self._fire_graph_event(event, _event_type)

    def on_key_down(self, event):
        pass

    def on_key_up(self, event):
        pass

    def update_screen(self):
        """
        Update gets called if the screen has been repainted in the middle of a zoom in
        so the Rubber Band Box can get updated. Other GUIModes may require something similar
        """
        pass
