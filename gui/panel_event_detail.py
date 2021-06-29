import wx
import wx.dataview as dv
from application.define import EnumMBTEventType, EnumMBTEventDataType
from application.class_mbt_event import MBTEvent


class EventDetailPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self._formSizer = wx.GridBagSizer(5, 5)
        self._detailTitle = wx.StaticText(self, wx.ID_ANY, 'EventDetail')
        self._detailTitle.SetFont(wx.Font(10, wx.FONTFAMILY_SCRIPT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self._dataLvLabel = wx.StaticText(self, wx.ID_ANY, 'EventData:')
        self.ctrlEvtNameLabel = wx.StaticText(self, wx.ID_ANY, 'Name:')
        self.ctrlEvtNameEdit = wx.TextCtrl(self, wx.ID_ANY)
        self.ctrlEvtTypLabel = wx.StaticText(self, wx.ID_ANY, 'Type:')
        self.ctrlEvtTypEdit = wx.ComboBox(self, wx.ID_ANY, value=EnumMBTEventType.INCOMING.value,
                                          choices=EnumMBTEventType.ALL_VALUES.value)
        self.ctrlEvtPermissionLabel = wx.StaticText(self, wx.ID_ANY, 'Permission:')
        self.ctrlEvtPermissionEdit = wx.StaticText(self, wx.ID_ANY, 'R')
        self.ctrlEvtDescLabel = wx.StaticText(self, wx.ID_ANY, 'Description:')
        self.ctrlEvtDescEdit = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_MULTILINE)
        self._formSizer.Add(self.ctrlEvtNameLabel, (0, 0), flag=wx.TOP, border=4)
        self._formSizer.Add(self.ctrlEvtNameEdit, (0, 1), span=(1, 10), flag=wx.EXPAND)
        self._formSizer.Add(self.ctrlEvtTypLabel, (1, 0), flag=wx.TOP, border=4)
        self._formSizer.Add(self.ctrlEvtTypEdit, (1, 1), span=(1, 5))
        self._formSizer.Add(self.ctrlEvtPermissionLabel, (2, 0), flag=wx.TOP, border=4)
        self._formSizer.Add(self.ctrlEvtPermissionEdit, (2, 1), span=(1, 5), flag=wx.TOP, border=4)
        self._formSizer.Add(self.ctrlEvtDescLabel, (3, 0), flag=wx.TOP, border=4)
        self._formSizer.Add(self.ctrlEvtDescEdit, (3, 1), span=(5, 10), flag=wx.EXPAND | wx.TOP, border=4)

        # init data table
        self.dvlc = dv.DataViewListCtrl(self, style=dv.DV_ROW_LINES)
        self.dvlc.AppendTextColumn('Name', width=96, mode=dv.DATAVIEW_CELL_EDITABLE)
        _col_type_render = dv.DataViewChoiceRenderer(EnumMBTEventDataType.ALL.value)
        _col_type = dv.DataViewColumn('Type', _col_type_render, 1, width=80)
        self.dvlc.AppendColumn(_col_type)
        self.dvlc.AppendTextColumn('Default', width=96, mode=dv.DATAVIEW_CELL_EDITABLE)
        # bind event
        self.dvlc.Bind(dv.EVT_DATAVIEW_ITEM_CONTEXT_MENU, self.on_dvlc_cm)
        # layout
        self.mainSizer.Add(self._detailTitle, 0, wx.ALL, 5)
        self.mainSizer.AddSpacer(15)
        self._formSizer.AddGrowableCol(1)
        # self._formSizer.AddGrowableRow(2)
        self.mainSizer.Add(self._formSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self._dataLvLabel, 0, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.dvlc, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(self.mainSizer)
        self.Layout()
        self.Fit()

    def on_dvlc_cm(self, evt: dv.DataViewEvent):
        _item = evt.GetItem()
        _selected_row = self.dvlc.GetSelectedRow()
        _menu = wx.Menu()
        _add_ref_id = wx.NewIdRef()
        _del_ref_id = wx.NewIdRef()
        _up_ref_id = wx.NewIdRef()
        _dwn_ref_id = wx.NewIdRef()
        _menu.Append(_add_ref_id, "Add")
        _menu.Append(_del_ref_id, "Delete")
        self.Bind(wx.EVT_MENU, self.on_cm_add, _add_ref_id)
        self.Bind(wx.EVT_MENU, self.on_cm_del, _del_ref_id)
        # will be called before PopupMenu returns.
        self.PopupMenu(_menu)
        _menu.Destroy()
        evt.Skip()

    def on_cm_add(self, evt):
        self.dvlc.AppendItem(('NewData', EnumMBTEventDataType.STRING.value, ''))

    def on_cm_del(self, evt):
        _row = self.dvlc.GetSelectedRow()
        self.dvlc.DeleteItem(_row)

    def set_data(self, data: MBTEvent):
        self.dvlc.DeleteAllItems()
        if data.readonly:
            self.Enable(False)
        else:
            self.Enable(True)
        self.ctrlEvtNameEdit.SetValue(data.name)
        self.ctrlEvtDescEdit.SetValue(data.description)
        self.ctrlEvtTypEdit.SetValue(data.type)
        self.ctrlEvtPermissionEdit.SetLabelText('R' if data.readonly else 'RW')
        _data = data.data
        for k, v in _data.items():
            self.dvlc.AppendItem((v.name, v.dataType, str(v.defaultVal)))

    def get_data(self):
        _evt_data = list()
        for i in range(self.dvlc.GetItemCount()):
            _evt_data.append({'name': self.dvlc.GetTextValue(i, 0),
                              'dataType': self.dvlc.GetTextValue(i, 1),
                              'default': self.dvlc.GetTextValue(i, 2)})
        _d = {
            'name': self.ctrlEvtNameEdit.GetValue(),
            'description': self.ctrlEvtDescEdit.GetValue(),
            'type': self.ctrlEvtTypEdit.GetValue(),
            'data': _evt_data
        }
        return _d

    def clear(self):
        self.dvlc.DeleteAllItems()
        self.ctrlEvtNameEdit.Clear()
        self.ctrlEvtDescEdit.Clear()
        self.ctrlEvtPermissionEdit.SetLabelText('')
