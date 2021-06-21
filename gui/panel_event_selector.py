import wx
import wx.dataview as dv
from .widgets import AutocompleteComboBox
from application.class_mbt_event import MBTEventManager


class EventSelectorPanel(wx.Panel):
    def __init__(self, event_mgr: MBTEventManager, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.evtList = dv.DataViewListCtrl(self, wx.ID_ANY, style=dv.DV_ROW_LINES | dv.DV_VERT_RULES)
        self.evtList.SetMinSize((-1,96))
        self.eventMgr = event_mgr
        self._col_event_render = dv.DataViewChoiceRenderer(event_mgr.get_events_names())
        _col_event = dv.DataViewColumn('Event', self._col_event_render, 0, width=120)
        self.evtList.AppendColumn(_col_event)
        self.evtList.AppendTextColumn('EventData', mode=dv.DATAVIEW_CELL_EDITABLE)
        self.evtList.Bind(dv.EVT_DATAVIEW_ITEM_ACTIVATED, self.on_item_activated)
        self.evtList.Bind(dv.EVT_DATAVIEW_ITEM_CONTEXT_MENU, self.on_item_cm)
        self.evtDataStructLabel = wx.StaticText(self, wx.ID_ANY)
        self.mainSizer.Add(self.evtDataStructLabel, 0, wx.EXPAND | wx.ALL, 2)
        self.mainSizer.Add(self.evtList, 1, wx.EXPAND | wx.ALL, 2)
        self.SetSizer(self.mainSizer)
        self.Layout()
        self.Fit()

    def get_selected_events(self):
        _res = list()
        for i in range(self.evtList.GetItemCount()):
            _res.append((self.evtList.GetTextValue(i, 0), self.evtList.GetTextValue(i, 1)))
        return _res

    def set_selected_events(self, events):
        self.evtList.Freeze()
        for val in events:
            self.evtList.AppendItem(val)
        self.evtList.Thaw()

    def get_evt_name_from_row(self, row):
        return self.evtList.GetTextValue(row, 0)

    def on_item_activated(self, evt: dv.DataViewEvent):
        self.update_event_data_label()

    def update_event_data_label(self):
        _row = self.evtList.GetSelectedRow()
        _evt_name = self.get_evt_name_from_row(_row)
        _evt = self.eventMgr.get_event(_evt_name)
        if _evt is not None:
            _typ_str = ' , '.join(['%s<%s>' % (x, y) for x, y in _evt.get_data_types(with_name=True)])
            self.evtDataStructLabel.SetLabelText('EventData: ' + _typ_str)

    def on_item_cm(self, evt: dv.DataViewEvent):
        _selected_row = self.evtList.GetSelectedRow()
        _menu = wx.Menu()
        _add_ref_id = wx.NewIdRef()
        _del_ref_id = wx.NewIdRef()
        _up_ref_id = wx.NewIdRef()
        _dwn_ref_id = wx.NewIdRef()
        _menu.Append(_add_ref_id, "Add")
        _menu.Append(_del_ref_id, "Delete")
        _menu.AppendSeparator()
        _menu.Append(_up_ref_id, "Up")
        _menu.Append(_dwn_ref_id, "Down")
        self.Bind(wx.EVT_MENU, self.on_cm_add, _add_ref_id)
        self.Bind(wx.EVT_MENU, self.on_cm_del, _del_ref_id)
        self.Bind(wx.EVT_MENU, self.on_cm_up, _up_ref_id)
        self.Bind(wx.EVT_MENU, self.on_cm_down, _dwn_ref_id)
        if _selected_row != -1:
            _menu.Enable(_add_ref_id, False)
            if _selected_row == 0:
                _menu.Enable(_up_ref_id, False)
            if _selected_row == self.evtList.GetItemCount() - 1:
                _menu.Enable(_dwn_ref_id, False)
        else:
            _menu.Enable(_del_ref_id, False)
            _menu.Enable(_up_ref_id, False)
            _menu.Enable(_dwn_ref_id, False)
        # will be called before PopupMenu returns.
        self.PopupMenu(_menu)
        _menu.Destroy()

    def add_empty_row(self):
        self.evtList.AppendItem(('NULL', ''))
        self.evtList.Update()

    def on_cm_add(self, evt):
        self.add_empty_row()

    def on_cm_del(self, evt):
        pass

    def on_cm_up(self, evt):
        pass

    def on_cm_down(self, evt):
        pass
