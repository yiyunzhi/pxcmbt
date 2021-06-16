import wx
import wx.grid as gridlib
from .define_gui import *


class EventDataTable(gridlib.GridTableBase):

    def __init__(self):
        gridlib.GridTableBase.__init__(self)
        self.colLabels = ['Name', 'Description']
        self.dataTypes = [gridlib.GRID_VALUE_STRING,
                          gridlib.GRID_VALUE_STRING
                          ]
        self.data = []

    def append_a_row(self, data=None):
        if data is not None:
            _data = data + [data[4]]
            self.data.append(_data)
        else:
            # add a new row
            self.data.append([''] * self.GetNumberCols())
        # tell the grid we've added a row
        msg = gridlib.GridTableMessage(self,  # The table
                                       gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED,  # what we did to it
                                       1  # how many
                                       )

        self.GetView().ProcessTableMessage(msg)

    def remove_a_row(self, idx):
        if idx <= len(self.data) - 1:
            self.data.pop(idx)
            # tell the grid we've delete a row
            msg = gridlib.GridTableMessage(self,  # The table
                                           gridlib.GRIDTABLE_NOTIFY_ROWS_DELETED,  # what we did to it
                                           idx,  # from
                                           1  # how many
                                           )

            self.GetView().ProcessTableMessage(msg)

    # ----------------------------------------------------------
    # required methods for the wxPyGridTableBase interface
    # ----------------------------------------------------------

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.colLabels)

    def IsEmptyCell(self, row, col):
        try:
            return not self.data[row][col]
        except IndexError:
            return True

    def GetValue(self, row, col):
        # Get/Set values in the table.  The Python version of these
        # methods can handle any data-type, (as long as the Editor and
        # Renderer understands the type too,) not just strings as in the
        # C++ version.
        try:
            _data = self.data[row][col]
            return _data
        except IndexError:
            return ''

    def SetValue(self, row, col, value):
        try:
            self.data[row][col] = value
        except IndexError:
            pass

    # --------------------------------------------------
    # Some optional methods
    # --------------------------------------------------

    def GetColLabelValue(self, col):
        """
        # Called when the grid needs to display labels
        :param col:
        :return:
        """
        return self.colLabels[col]

    def GetTypeName(self, row, col):
        """
        # Called to determine the kind of editor/renderer to use by
    # default, doesn't necessarily have to be the same type used
    # natively by the editor/renderer if they know how to convert.
        :param row:
        :param col:
        :return:
        """
        return self.dataTypes[col]

    def CanGetValueAs(self, row, col, type_name):
        """
        # Called to determine how the data can be fetched and stored by the
    # editor and renderer.  This allows you to enforce some type-safety
    # in the grid.
        :param row:
        :param col:
        :param type_name:
        :return:
        """
        # print('type name col=%s'%col,type_name)
        _col_type = self.dataTypes[col].split(':')[0]
        if type_name == _col_type:
            return True
        else:
            return False

    def CanSetValueAs(self, row, col, type_name):
        return self.CanGetValueAs(row, col, type_name)


class EventDataTableGrid(gridlib.Grid):
    def __init__(self, uuid, parent):
        gridlib.Grid.__init__(self, parent, wx.ID_ANY)
        self.SetColLabelSize(WX_GUI_GRID_COL_LABEL_HEIGHT)
        self.uuid = uuid
        self._table = EventDataTable()
        # The second parameter of SetTable means that the grid is to take ownership of the
        # table and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        self.SetTable(self._table, True)
        self.SetMargins(0, 0)
        self.AutoSizeColumns(True)
        # self.HideCol(self.ACTUAL_VAL_COL)
        # self.init_table_view(allocation_list)
        self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_CLICK, self.on_label_right_clicked)
        self.Bind(gridlib.EVT_GRID_CELL_CHANGED, self.on_cell_changed)
        self.Bind(wx.EVT_SIZE, self.on_resized)
        # EnumRackPanelSignals.sigM2VEPPDInUpdated.connect(self.on_pd_in_updated)
        # EnumRackPanelSignals.sigV2MEPPDOutUpdated.connect(self.on_pd_out_updated)
        self.Update()

    def on_resized(self, evt):
        _cnt_cols = self._table.GetNumberCols()
        _w = 0
        for i in range(_cnt_cols - 1):
            _w += self.GetColSize(i)
        _w += self.GetRowLabelSize()
        _new_size = evt.GetSize().x
        _col_size = _new_size - _w - wx.SYS_VSCROLL_X
        if _col_size > 0:
            self.SetColSize(_cnt_cols - 1, _col_size)
        evt.Skip()

    def on_label_right_clicked(self, evt):
        _selected_rows = self.GetSelectedRows()
        _menu = wx.Menu()
        _add_in_ref_id = wx.NewIdRef()
        _add_out_ref_id = wx.NewIdRef()
        _del_ref_id = wx.NewIdRef()
        # if self._inCnt > 0:
        #     _menu.Append(_add_in_ref_id, "Add new Input")
        #     self.Bind(wx.EVT_MENU, self.on_ctx_menu_add_new_in_clicked, id=_add_in_ref_id)
        # if self._outCnt > 0:
        #     _menu.Append(_add_out_ref_id, "Add new Output")
        #     self.Bind(wx.EVT_MENU, self.on_ctx_menu_add_new_out_clicked, id=_add_out_ref_id)
        _menu.Append(_del_ref_id, "Delete selected")
        self.Bind(wx.EVT_MENU, lambda evt, rows=_selected_rows: self.on_ctx_menu_del_sel_clicked(evt, rows),
                  id=_del_ref_id)
        self.PopupMenu(_menu)
        _menu.Destroy()

    def append_a_row(self, row):
        if len(row) != len(self._table.colLabels):
            return
        self._table.append_a_row(row)

    def on_ctx_menu_add_new_event_clicked(self, evt):
        _untitled = ['New Event', 'New Event Description']
        self.append_a_row(_untitled)

    def on_ctx_menu_del_sel_clicked(self, evt, rows):
        self.BeginBatch()
        for row in rows:
            self._table.remove_a_row(row)
        self.EndBatch()
        self.AdjustScrollbars()
        self.ForceRefresh()

    def on_cell_changed(self, evt):
        _row, _col = evt.GetRow(), evt.GetCol()


class EventEditorPanel(wx.Panel):
    def __init__(self, parent, events=None):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.uuid = None
        self.role = 'EnumPaneRole.PANE_EVENT'
        self.events = events
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.evtTable = EventDataTableGrid(self.uuid, self)
        self.mainSizer.Add(self.evtTable, 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)
        self.Layout()
        self.Fit()
