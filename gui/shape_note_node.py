import wx
import wx.propgrid as wxpg
from wxgraph import DrawObjectPolygon, DrawObjectGroup, DrawObjectScaledTextBox
from .define_gui import *
from .base_state_chart_node import StateChartNode
from application.define import EnumItemRole


class NoteNodeShape(StateChartNode):
    def __init__(self, pos, text='Notes...', in_foreground=False, visible=True):
        StateChartNode.__init__(self, in_foreground=in_foreground, is_visible=visible)
        self.connectionStyle = EnumShapeConnectionStyle.NONE
        self.role = EnumItemRole.ITEM_NODE_NOTE
        self.text = text
        self.position = pos
        self.textBoxBgColor = '#abc'
        self.textBox = DrawObjectScaledTextBox('', pos, 10, pad_size=5, line_width=0, line_color=self.textBoxBgColor,
                                               background_color=self.textBoxBgColor)
        self._cornerBgPoly = DrawObjectPolygon([pos], fill_color=self.textBoxBgColor)
        self.add_object(self._cornerBgPoly)
        self.add_object(self.textBox)
        self._cornerW = 10
        self._cornerH = 10
        self.set_text(text)

    def serialize(self):
        _d = dict()
        _d.update({'class': self.__class__.__name__})
        _d.update({'uuid': self.uuid})
        _d.update({'role': self.role})
        _d.update({'text': self.text})
        _d.update({'isVisible': self.isVisible})
        _d.update({'position': self.position})
        _d.update({'connectionStyle': self.connectionStyle})
        return _d

    def deserialize(self, data):
        pass

    def set_text(self, text):
        self.text = text
        self.textBox.set_text(text)
        self._build_corner_style()
        self.calc_bounding_box()

    def set_selected(self, state):
        if state:
            self.textBox.set_line_color(self.selectedBorderLineColor)
        else:
            self.textBox.set_line_color(self.defaultBorderLineColor)
        self.isSelected = state

    def _build_corner_style(self):
        _xy, _wh = self.textBox.get_box_rect()
        _rect = wx.Rect(_xy, _wh).Inflate(2, 2)
        _rect.Offset(0, -1 * _wh[1])
        _pt1 = _rect.GetTopLeft()
        _pt2 = _rect.GetBottomLeft()
        _pt3 = _rect.GetBottomRight() - wx.Point(self._cornerW, 0)
        _pt4 = _rect.GetBottomRight() + wx.Point(0, self._cornerH)
        _pt5 = _rect.GetTopRight()
        self._cornerBgPoly.set_points([_pt1, _pt2, _pt3, _pt4, _pt5])

    def get_properties(self, pg_parent):
        _pg_main = wxpg.PropertyGridManager(pg_parent, wx.ID_ANY,
                                            style=wxpg.PG_SPLITTER_AUTO_CENTER | wxpg.PG_BOLD_MODIFIED)
        _pg_uuid = wxpg.StringProperty("uuid", 'uuid', value=self.uuid)
        _pg_main.SetPropertyReadOnly(_pg_uuid)
        _pg_main.Append(_pg_uuid)

        _pg_role = wxpg.StringProperty("role", 'role', value=EnumItemRole(self.role).name)
        _pg_main.SetPropertyReadOnly(_pg_role)
        _pg_main.Append(_pg_role)

        _pg_position = wxpg.StringProperty("position", 'position',
                                           value='(%s,%s)' % (self.position[0], self.position[1]))
        _pg_main.SetPropertyReadOnly(_pg_position)
        _pg_main.Append(_pg_position)

        return _pg_main

    def on_left_down(self, *args):
        print('state left down', *args)

    def on_enter(self, *args):
        print('state on_enter', *args)

    def on_leave(self, *args):
        print('state on_leave', *args)

    def on_left_up(self, *args):
        print('state on left up', *args)
