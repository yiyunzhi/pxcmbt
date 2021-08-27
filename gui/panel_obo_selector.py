import wx
import wx.dataview as dv
from .panel_props_container import PropContainerPanel
from .panel_prop_content import OBOPropsContentPanel
from application.class_observable import MBTOBOManager


class ResolverOboPropContainer(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.oboPropPanel = PropContainerPanel(parent=self)
        self.oboPropPanel.SetMinSize((360, 96))
        self.mainSizer.Add(self.oboPropPanel, 1, wx.EXPAND | wx.ALL, 0)
        self.SetSizerAndFit(self.mainSizer)


class OBOSelectorPanel(wx.Panel):
    # todo: next version oboPropPanelContainer and oboList in sashWindow
    def __init__(self, obo_mgr: MBTOBOManager, parent, obo_filter=None):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.tableHSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.oboPropPanelContainer = ResolverOboPropContainer(self)
        self.oboPropPanelContainer.SetMinSize((380, -1))
        self.oboList = dv.DataViewListCtrl(self, wx.ID_ANY, style=dv.DV_ROW_LINES | dv.DV_VERT_RULES)
        self.oboList.SetMinSize((-1, 96))
        self.oboMgr = obo_mgr
        self._oboUids = list()
        self._oboNameChoices = list()
        if obo_filter is None:
            _obos = obo_mgr.get_all_obos()
        else:
            _obos = obo_mgr.get_obos_by_type(obo_filter)
        for k, v in _obos.items():
            self._oboUids.append(k)
            self._oboNameChoices.append(v.name)
        self._col_OBO_render = dv.DataViewChoiceRenderer(self._oboNameChoices)
        _col_obo = dv.DataViewColumn('OBO', self._col_OBO_render, 0, width=120)
        self.oboList.AppendColumn(_col_obo)
        self.oboList.AppendTextColumn('OBOData (leave blank use default)', mode=dv.DATAVIEW_CELL_EDITABLE)
        _col_obo_uuid = self.oboList.AppendTextColumn('UUID', mode=dv.DATAVIEW_CELL_INERT)
        _col_obo_uuid.SetHidden(True)
        # bind events
        self.oboList.Bind(dv.EVT_DATAVIEW_ITEM_ACTIVATED, self.on_item_activated)
        self.oboList.Bind(dv.EVT_DATAVIEW_ITEM_CONTEXT_MENU, self.on_item_cm)
        self.oboList.Bind(dv.EVT_DATAVIEW_SELECTION_CHANGED, self.on_item_selected)
        # layouts
        self.evtDataStructLabel = wx.StaticText(self, wx.ID_ANY)
        self.tableHSizer.Add(self.oboList, 1, wx.EXPAND | wx.ALL, 2)
        self.tableHSizer.Add(self.oboPropPanelContainer, 0, wx.EXPAND | wx.ALL, 2)
        self.mainSizer.Add(self.evtDataStructLabel, 0, wx.EXPAND | wx.ALL, 2)
        self.mainSizer.Add(self.tableHSizer, 1, wx.EXPAND | wx.ALL, 2)
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
        _obo_name = self.get_obo_name_from_row(_row)
        _obo = self.oboMgr.get_obo_by_name(_obo_name)
        if _obo is not None:
            _typ_str = ' , '.join(['%s<%s>' % (x, y) for x, y in _obo.get_data_types(with_name=True)])
            self.evtDataStructLabel.SetLabelText('OBOData: ' + _typ_str)

    def on_item_selected(self, evt):
        _selected_row = self.oboList.GetSelectedRow()
        if _selected_row != -1:
            _name = self.oboList.GetTextValue(_selected_row, 0)
            _obo = self.oboMgr.get_obo_by_name(_name)
            if _obo is not None:
                self.show_obo_props(_obo)

    def show_obo_props(self, obo):
        _content = OBOPropsContentPanel(obo, parent=self.oboPropPanelContainer.oboPropPanel)
        self.oboPropPanelContainer.oboPropPanel.set_content(_content)

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
        self.oboList.AppendItem(('SelectHere', '', ''))
        self.oboList.Update()

    def on_cm_add(self, evt):
        self.add_empty_row()

    def on_cm_del(self, evt):
        _selected_row = self.oboList.GetSelectedRow()
        if _selected_row != -1:
            self.oboList.DeleteItem(_selected_row)

    def on_cm_up(self, evt):
        pass

    def on_cm_down(self, evt):
        pass
