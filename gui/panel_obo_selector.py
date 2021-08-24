import wx
import wx.dataview as dv
from .widgets import AutocompleteComboBox
from application.class_observable import MBTOBOManager


class OBOSelectorPanel(wx.Panel):
    def __init__(self, obo_mgr: MBTOBOManager, parent, obo_filter=None):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.oboList = dv.DataViewListCtrl(self, wx.ID_ANY, style=dv.DV_ROW_LINES | dv.DV_VERT_RULES)
        self.oboList.SetMinSize((-1, 96))
        self.oboMgr = obo_mgr
        if obo_filter is None:
            _obos = obo_mgr.get_obos_names()
        else:
            _obos = obo_mgr.get_obos_names_by_type(obo_filter)
        self._col_OBO_render = dv.DataViewChoiceRenderer(_obos)
        _col_obo = dv.DataViewColumn('OBO', self._col_OBO_render, 0, width=120)
        self.oboList.AppendColumn(_col_obo)
        self.oboList.AppendTextColumn('OBOData', mode=dv.DATAVIEW_CELL_EDITABLE)
        _col_obo_uuid =self.oboList.AppendTextColumn('UUID', mode=dv.DATAVIEW_CELL_INERT)
        _col_obo_uuid.SetHidden(True)
        # bind events
        self.oboList.Bind(dv.EVT_DATAVIEW_ITEM_ACTIVATED, self.on_item_activated)
        self.oboList.Bind(dv.EVT_DATAVIEW_ITEM_CONTEXT_MENU, self.on_item_cm)
        # layouts
        self.evtDataStructLabel = wx.StaticText(self, wx.ID_ANY)
        self.mainSizer.Add(self.evtDataStructLabel, 0, wx.EXPAND | wx.ALL, 2)
        self.mainSizer.Add(self.oboList, 1, wx.EXPAND | wx.ALL, 2)
        self.SetSizer(self.mainSizer)
        self.Layout()
        self.Fit()

    def get_selected_obos(self):
        _res = list()
        for i in range(self.oboList.GetItemCount()):
            _res.append((self.oboList.GetTextValue(i, 0), self.oboList.GetTextValue(i, 1)))
        return _res

    def set_selected_obos(self, obos):
        self.oboList.Freeze()
        for val in obos:
            self.oboList.AppendItem(val)
        self.oboList.Thaw()

    def get_obo_name_from_row(self, row):
        return self.oboList.GetTextValue(row, 0)

    def get_obo_uuid_from_row(self, row):
        return self.oboList.GetTextValue(row, 2)

    def on_item_activated(self, evt: dv.DataViewEvent):
        self.update_obo_data_label()

    def update_obo_data_label(self):
        _row = self.oboList.GetSelectedRow()
        _obo_uuid = self.get_obo_uuid_from_row(_row)
        _obo = self.oboMgr.get_obo(_obo_uuid)
        if _obo is not None:
            _typ_str = ' , '.join(['%s<%s>' % (x, y) for x, y in _obo.get_data_types(with_name=True)])
            self.evtDataStructLabel.SetLabelText('OBOData: ' + _typ_str)

    def on_item_cm(self, evt: dv.DataViewEvent):
        _selected_row = self.oboList.GetSelectedRow()
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
            if _selected_row == self.oboList.GetItemCount() - 1:
                _menu.Enable(_dwn_ref_id, False)
        else:
            _menu.Enable(_del_ref_id, False)
            _menu.Enable(_up_ref_id, False)
            _menu.Enable(_dwn_ref_id, False)
        # will be called before PopupMenu returns.
        self.PopupMenu(_menu)
        _menu.Destroy()

    def add_empty_row(self):
        self.oboList.AppendItem(('NULL', '', ''))
        self.oboList.Update()

    def on_cm_add(self, evt):
        self.add_empty_row()

    def on_cm_del(self, evt):
        pass

    def on_cm_up(self, evt):
        pass

    def on_cm_down(self, evt):
        pass
