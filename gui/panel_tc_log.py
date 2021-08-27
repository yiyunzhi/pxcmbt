# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       :
# Sourcefile(s) : panel_console.py
# ------------------------------------------------------------------------------
#
# File          : panel_console.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import wx
import wx.dataview as dv
from pubsub import pub
from application.define import APP_CONSOLE_TIME_WX_FMT, ConsoleItemFlagEnum
from .define_gui import PATH_GUI_IMAGES
from application.utils_helper import util_date_now
from application.define import EnumAppSignals


class ConsoleDataModel(dv.DataViewIndexListModel):
    def __init__(self):
        dv.DataViewIndexListModel.__init__(self)
        self.data = list()
        self._data = [x for x in self.data]

    def GetColumnType(self, col):
        # All of our columns are strings.  If the model or the renderers
        # in the view are other types then that should be reflected here.
        return "string"

    def GetValueByRow(self, row, col):
        # This method is called to provide the data object for a
        # particular row,col
        if row < self.GetCount():
            return self.data[row][col]
        else:
            return None

    def SetValueByRow(self, value, row, col):
        # This method is called when the user edits a data item in the view.
        if row < self.GetCount():
            self.data[row][col] = value
            return True
        else:
            return False

    def GetColumnCount(self):
        # Report how many columns this model provides data for.
        return 4

    def GetCount(self):
        # Report the number of rows in the model
        return len(self.data)

    def GetAttrByRow(self, row, col, attr):
        # Called to check if non-standard attributes should be used in the
        # cell at (row, col)
        if col == 3:
            attr.SetColour('blue')
            attr.SetBold(True)
            return True
        return False

    def Compare(self, item1, item2, col, ascending):
        # This is called to assist with sorting the data in the view.  The
        # first two args are instances of the DataViewItem class, so we
        # need to convert them to row numbers with the GetRow method.
        # Then it's just a matter of fetching the right values from our
        # data set and comparing them.  The return value is -1, 0, or 1,
        # just like Python's cmp() function.
        if not ascending:  # swap sort order?
            item2, item1 = item1, item2
        row1 = self.GetRow(item1)
        row2 = self.GetRow(item2)
        a = self.data[row1][col]
        b = self.data[row2][col]
        if col == 0:
            _t1 = wx.DateTime()
            _t2 = wx.DateTime()
            _t1.ParseFormat(a, APP_CONSOLE_TIME_WX_FMT)
            _t2.ParseFormat(b, APP_CONSOLE_TIME_WX_FMT)
            if _t1.IsEarlierThan(_t2): return -1
            if _t2.IsEarlierThan(_t1): return 1
        elif col == 2:
            if a < b: return -1
            if a > b: return 1
        return 0

    def remove_rows(self, rows):
        # make a copy since we'll be sorting(mutating) the list
        # use reverse order so the indexes don't change as we remove items
        _rows = sorted(rows, reverse=True)

        for row in _rows:
            # remove it from our data structure
            del self.data[row]
            del self._data[row]
            # notify the view(s) using this model that it has been removed
            self.RowDeleted(row)

    def append_a_row(self, value):
        # update data structure
        self.data.append(value)
        self._data.append(value)
        # notify views
        self.RowAppended()

    def filter_func(self, filter_funcs):
        _res = list()
        for filter_func in filter_funcs:
            _res += list(filter(filter_func, self._data))
        self.data = _res
        self.Reset(len(self.data))

    def clear(self):
        self.data.clear()
        self._data.clear()
        self.Reset(len(self.data))
        self.Cleared()

    def restore(self):
        self.data = [x for x in self._data]
        self.Reset(len(self.data))


class TCConsolePanel(wx.Panel):
    REFRESH_BTN_ID = wx.ID_HIGHEST + 200
    CLEAR_BTN_ID = wx.ID_HIGHEST + 201
    ICON_SIZE = (14, 14)
    CONTENT_COL = 2

    def __init__(self, **kwargs):
        wx.Panel.__init__(self, **kwargs)
        self.role = 'EnumPaneRole.CONSOLE'
        self.uuid = None
        self.ICON_INFO = wx.Icon(
            wx.Image(PATH_GUI_IMAGES + '\\icon_info.png', wx.BITMAP_TYPE_PNG).Scale(*self.ICON_SIZE).ConvertToBitmap())
        self.ICON_WARNING = wx.Icon(wx.Image(PATH_GUI_IMAGES + '\\icon_warning.png', wx.BITMAP_TYPE_PNG).Scale(
            *self.ICON_SIZE).ConvertToBitmap())
        self.ICON_ERROR = wx.Icon(
            wx.Image(PATH_GUI_IMAGES + '\\icon_error.png', wx.BITMAP_TYPE_PNG).Scale(*self.ICON_SIZE).ConvertToBitmap())
        self._tb = wx.ToolBar(self, style=wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT)
        self._vSizer = wx.BoxSizer(wx.VERTICAL)
        self.dvc = dv.DataViewCtrl(self, style=wx.BORDER_THEME
                                               | dv.DV_ROW_LINES  # nice alternating bg colors
                                               # | dv.DV_HORIZ_RULES
                                               | dv.DV_VERT_RULES
                                               | dv.DV_MULTIPLE
                                   )

        # Create an instance of our simple model...
        self.model = ConsoleDataModel()
        # ...and associate it with the dataview control.  Models can
        # be shared between multiple DataViewCtrls, so this does not
        # assign ownership like many things in wx do.  There is some
        # internal reference counting happening so you don't really
        # need to hold a reference to it either, but we do for this
        # example so we can fiddle with the model from the widget
        # inspector or whatever.
        self.dvc.AssociateModel(self.model)
        # Now we create some columns.  The second parameter is the
        # column number within the model that the DataViewColumn will
        # fetch the data from.  This means that you can have views
        # using the same model that show different columns of data, or
        # that they can be in a different order than in the model.
        # if need editable then use arg mode=dv.DATAVIEW_CELL_EDITABLE
        _c1 = self.dvc.AppendIconTextColumn("Level", 1, width=52)
        _c1.Alignment = wx.ALIGN_LEFT
        _c2 = self.dvc.AppendTextColumn("Content", self.CONTENT_COL, width=320)
        _c3 = self.dvc.AppendTextColumn("__TYPE", 3, width=0)
        _c3.SetHidden(True)
        # There are Prepend methods too, and also convenience methods
        # for other data types but we are only using strings in this
        # example.  You can also create a DataViewColumn object
        # yourself and then just use AppendColumn or PrependColumn.
        _c0 = self.dvc.PrependTextColumn("DateTime", 0, width=120)
        _c0.SetSortOrder(False)
        # The DataViewColumn object is returned from the Append and
        # Prepend methods, and we can modify some of it's properties
        # like this.
        _c0.Alignment = wx.ALIGN_LEFT
        _c0.Renderer.Alignment = wx.ALIGN_LEFT
        _c0.MinWidth = 40

        # Through the magic of Python we can also access the columns
        # as a list via the Columns property.  Here we'll mark them
        # all as sortable and reorderable.
        for c in self.dvc.GetColumns():
            c.Sortable = True
            c.Reorderable = True
        # change our minds and not let the second col be sorted.
        _c1.Sortable = False
        # initial toolbar
        self.init_toolbar()
        # bind events
        pub.subscribe(self.on_ext_sig_write_info_to_console, EnumAppSignals.sigV2VTCConsoleAddInfoContent.value)
        pub.subscribe(self.on_ext_sig_write_warning_to_console, EnumAppSignals.sigV2VTCConsoleAddWarningContent.value)
        pub.subscribe(self.on_ext_sig_write_error_to_console, EnumAppSignals.sigV2VTCConsoleAddErrorContent.value)
        # layouts
        self._vSizer.Add(self.dvc, 1, wx.EXPAND)
        self.SetSizer(self._vSizer)
        self.dvc.GetMainWindow().Bind(wx.EVT_MOTION, self.on_dvc_mouse_overed)
        wx.CallAfter(self.dvc.SendSizeEvent)
        self.Layout()
        self.Fit()

    def init_toolbar(self):
        _icon_size = (16, 16)
        _filter_label = wx.StaticText(self._tb, label='Filter:  ')
        self._chk_info = wx.CheckBox(self._tb, label='Info')
        self._chk_warning = wx.CheckBox(self._tb, label='Warning')
        self._chk_error = wx.CheckBox(self._tb, label='Error')
        self._tb.AddSeparator()
        self._tb.AddControl(_filter_label)
        self._tb.AddControl(self._chk_info)
        self._tb.AddControl(self._chk_warning)
        self._tb.AddControl(self._chk_error)
        self._tb.AddStretchableSpace()
        _refresh_bmp = wx.Image(PATH_GUI_IMAGES + '\\icon_refresh.png', wx.BITMAP_TYPE_PNG).Scale(
            *_icon_size).ConvertToBitmap()
        _del_bmp = wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_TOOLBAR, _icon_size)
        self._tb.AddTool(self.REFRESH_BTN_ID, "Refresh", _refresh_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Refresh",
                         "Refresh the console", None)
        self._tb.AddTool(self.CLEAR_BTN_ID, "Clear", _del_bmp, wx.NullBitmap, wx.ITEM_NORMAL, "Clear",
                         "Clear the console", None)
        self._chk_info.SetValue(True)
        self._chk_warning.SetValue(True)
        self._chk_error.SetValue(True)
        self._tb.Realize()
        self._vSizer.Add(self._tb, 0, wx.EXPAND)
        # bind event
        self.Bind(wx.EVT_TOOL, self.on_refresh_clicked, id=self.REFRESH_BTN_ID)
        self.Bind(wx.EVT_TOOL, self.on_clear_clicked, id=self.CLEAR_BTN_ID)
        self.Bind(wx.EVT_CHECKBOX, self.on_filter_changed, self._chk_info)
        self.Bind(wx.EVT_CHECKBOX, self.on_filter_changed, self._chk_warning)
        self.Bind(wx.EVT_CHECKBOX, self.on_filter_changed, self._chk_error)

    def on_dvc_mouse_overed(self, evt):
        _pos = wx.GetMousePosition()
        _mouse_pos = self.dvc.ScreenToClient(_pos)
        _item, _b = self.dvc.HitTest(_mouse_pos)
        _model_col_idx = _b.GetModelColumn()
        self.update_content_tip(_item, _model_col_idx)
        evt.Skip()

    def update_content_tip(self, item, col):
        if col == self.CONTENT_COL:
            _val = self.model.GetValue(item, col)
            if _val:
                self.dvc.GetMainWindow().SetToolTip(_val)

    def on_refresh_clicked(self, evt):
        print('console refresh clicked')
        pass

    def on_clear_clicked(self, evt):
        self.model.clear()

    def on_filter_changed(self, evt):

        _filter_funcs = []
        if self._chk_info.GetValue():
            _filter_funcs.append(lambda x: x[3] == ConsoleItemFlagEnum.FLAG_INFO)
        if self._chk_warning.GetValue():
            _filter_funcs.append(lambda x: x[3] == ConsoleItemFlagEnum.FLAG_WARNING)
        if self._chk_error.GetValue():
            _filter_funcs.append(lambda x: x[3] == ConsoleItemFlagEnum.FLAG_ERROR)
        if len(_filter_funcs) == 3:
            self.model.restore()
        else:
            self.model.filter_func(_filter_funcs)

    def on_ext_sig_write_info_to_console(self, content, t=None):
        self.write_info_content(content, t)

    def on_ext_sig_write_warning_to_console(self, content, t=None):
        self.write_warning_content(content, t)

    def on_ext_sig_write_error_to_console(self, content, t=None):
        self.write_error_content(content, t)

    def write_info_content(self, content: str, t: str = None):
        _data = [None] * 4
        _args = ('Info', self.ICON_INFO)
        _data[0] = util_date_now() if t is None else t
        _data[1] = wx.dataview.DataViewIconText(*_args)
        _data[2] = content
        _data[3] = ConsoleItemFlagEnum.FLAG_INFO
        self.model.append_a_row(_data)

    def write_warning_content(self, content: str, t: str = None):
        _data = [None] * 4
        _args = ('Warn', self.ICON_WARNING)
        _data[0] = util_date_now() if t is None else t
        _data[1] = wx.dataview.DataViewIconText(*_args)
        _data[2] = content
        _data[3] = ConsoleItemFlagEnum.FLAG_WARNING
        self.model.append_a_row(_data)

    def write_error_content(self, content: str, t: str = None):
        _data = [None] * 4
        _args = ('Error', self.ICON_ERROR)
        _data[0] = util_date_now() if t is None else t
        _data[1] = wx.dataview.DataViewIconText(*_args)
        _data[2] = content
        _data[3] = ConsoleItemFlagEnum.FLAG_ERROR
        self.model.append_a_row(_data)

    def write(self, std_out_strings):
        self.write_info_content(std_out_strings)
