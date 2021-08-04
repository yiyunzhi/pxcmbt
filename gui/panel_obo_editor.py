import wx
import wx.dataview as dv
from application.class_observable import *
from application.define import *
from .define_gui import *
from .panel_obo_detail import OBODetailPanel
from .util_icon_repo import UtilIconRepo


class OBOEditorPanel(wx.Panel):
    SRC_OBO_MGR = 0
    SRC_OBO_BUILTIN = 1

    def __init__(self, parent, event_data=None, built_in_obo_data=None):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.uuid = None
        self.role = 'EnumPaneRole.PANE_OBO'
        self.shouldSave = False
        self.processedObo = None
        self.builtInOboData = built_in_obo_data
        self._iconRepo = UtilIconRepo()
        self.oboMgr = MBTOBOManager()
        self.oboMgr.deserialize(event_data)
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.oboLstSizer = wx.BoxSizer(wx.VERTICAL)
        self.oboDetailSizer = wx.BoxSizer(wx.VERTICAL)
        self.oboLstToolsSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.oboActionSizer = wx.BoxSizer(wx.HORIZONTAL)
        # obo list tools
        self.ctrlSearch = wx.SearchCtrl(self, size=(160, -1), style=wx.TE_PROCESS_ENTER)
        self.ctrlSearch.ShowCancelButton(True)
        _srch_w, _srch_h = self.ctrlSearch.GetSize()
        # _choices = EnumOBOType.ALL_VALUES.value
        # self.ctrlOboDropList = wx.ComboBox(self, size=(160, -1), value=_choices[0], choices=_choices, style=wx.CB_DROPDOWN)
        # _w, _h = self.ctrlOboDropList.GetSize()
        self.oboAddBtn = wx.Button(self, wx.ID_ANY, '+', size=(_srch_h, _srch_h))
        self.oboAddBtn.SetToolTip('Add a new event')
        self.oboRemoveBtn = wx.Button(self, wx.ID_ANY, '-', size=(_srch_h, _srch_h))
        self.oboRemoveBtn.SetToolTip('Remove a new event')
        self.btnApplyChange = wx.Button(self, wx.ID_ANY, 'ApplyChange')
        self.btnApplyChange.Bind(wx.EVT_BUTTON, self.on_apply_change_clicked)
        # create detail panel
        self.detailPanel = OBODetailPanel(self)
        # Create a dataview control
        self.dvlc = dv.DataViewListCtrl(self, style=wx.LC_REPORT | dv.DV_NO_HEADER | dv.DV_ROW_LINES)
        self.dvlc.SetRowHeight(16)
        self.dvlc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.dvlc.AppendBitmapColumn('Direction', 0, width=18)
        self.dvlc.AppendTextColumn('Name', width=120)
        _incoming_icon = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR, (10, 10))
        _outgoing_icon = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR, (10, 10))
        for name, obo in self.oboMgr.get_all_obos().items():
            if obo.visible:
                self._add_obo(obo, self.SRC_OBO_MGR)
        if self.builtInOboData is not None:
            [self._add_obo(obo, self.SRC_OBO_BUILTIN) for name, obo in self.builtInOboData.items() if obo.visible]
        # bind events
        self.oboAddBtn.Bind(wx.EVT_BUTTON, self.on_add_obo)
        self.oboRemoveBtn.Bind(wx.EVT_BUTTON, self.on_remove_event)
        # self.dvlc.Bind(dv.EVT_DATAVIEW_ITEM_ACTIVATED, self.on_dv_item_activated)
        self.dvlc.Bind(dv.EVT_DATAVIEW_SELECTION_CHANGED, self.on_dv_item_select_changed)

        # layout
        self.oboLstToolsSizer.Add(self.ctrlSearch, 0)
        self.oboLstToolsSizer.AddStretchSpacer(1)
        self.oboLstToolsSizer.Add(self.oboAddBtn, 0)
        self.oboLstToolsSizer.Add(self.oboRemoveBtn, 0)
        self.oboLstSizer.Add(self.oboLstToolsSizer, 0, wx.EXPAND)
        self.oboLstSizer.AddSpacer(10)
        self.oboLstSizer.Add(self.dvlc, 1, wx.EXPAND)
        self.oboDetailSizer.Add(self.detailPanel, 1, wx.EXPAND)
        self.oboDetailSizer.Add(self.oboActionSizer, 0, wx.EXPAND, 5)
        self.oboActionSizer.AddStretchSpacer(1)
        self.oboActionSizer.Add(self.btnApplyChange, 0, wx.ALL, 5)
        self.mainSizer.Add(self.oboLstSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.oboDetailSizer, 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)
        self.Layout()
        self.Fit()

    def _add_obo(self, obo, data=SRC_OBO_MGR, select=True):
        _icon = self._get_obo_icon(obo)
        self.dvlc.AppendItem((_icon, obo.name), data)
        if select:
            self.dvlc.Select(self.dvlc.RowToItem(self.dvlc.GetItemCount() - 1))

    def _get_obo_icon(self, obo):
        _img_lst = self._iconRepo.get_image_list()
        if obo.type == EnumOBOType.PD.value:
            return _img_lst.GetBitmap(self._iconRepo.binaryIcon)
        elif obo.type == EnumOBOType.FHOST_SB.value:
            return wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR, (10, 10))
        elif obo.type == EnumOBOType.FDEVICE_SB.value:
            return wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR, (10, 10))
        elif obo.type == EnumOBOType.DIAGNOSIS.value:
            return _img_lst.GetBitmap(self._iconRepo.alarmTaIcon)
        elif obo.type == EnumOBOType.LED.value:
            return _img_lst.GetBitmap(self._iconRepo.ledIcon)
        else:
            return _img_lst.GetBitmap(self._iconRepo.binaryIcon)

    def _handle_unsaved_obo(self):
        if self.dvlc.GetItemCount() < 1:
            return
        _selected_row = self.dvlc.GetSelectedRow()
        if _selected_row != -1:
            _selected_evt_name = self.dvlc.GetTextValue(_selected_row, 1)
        else:
            return
        if self.processedObo is not None:
            _ret = wx.MessageBox('Edit of the event not finish, do you want save it?', 'Save Event Change',
                                 style=wx.YES_NO)
            if _ret == wx.YES:
                self._save_processed_obo()
            elif _ret == wx.NO:
                _exist = self.oboMgr.has_obo(self.processedObo.name)
                if not _exist:
                    self.dvlc.DeleteItem(_selected_row)
            self.processedObo = None

    def on_dv_item_select_changed(self, evt: dv.DataViewEvent):
        _selected_row = self.dvlc.GetSelectedRow()
        _item = self.dvlc.RowToItem(_selected_row)
        _item_data = self.dvlc.GetItemData(_item)
        if _selected_row == -1:
            self.detailPanel.clear()
            return
        _selected_obo_name = self.dvlc.GetTextValue(_selected_row, 1)
        if self.processedObo is not None:
            if _selected_obo_name != self.processedObo.name:
                self._handle_unsaved_obo()
        if self.processedObo is None:
            if _item_data == self.SRC_OBO_MGR:
                _obo = self.oboMgr.get_obo(_selected_obo_name)
            elif _item_data == self.SRC_OBO_BUILTIN:
                _obo = self.builtInOboData.get(_selected_obo_name)
            else:
                _obo = None
            if _obo is not None:
                self.detailPanel.set_data(_obo)
                if _item_data == self.SRC_OBO_MGR:
                    self.processedObo = _obo
                if _obo.readonly:
                    self.detailPanel.Disable()
                    self.oboRemoveBtn.Disable()
                else:
                    self.detailPanel.Enable()
                    self.oboRemoveBtn.Enable()

    def _save_processed_obo(self):
        if self.processedObo is not None:
            _exist = self.oboMgr.has_obo(self.processedObo.name)
            if _exist:
                if self.oboMgr.is_obo_changed(self.processedObo):
                    self.oboMgr.update(self.processedObo)
            else:
                self.oboMgr.register_obo(self.processedObo)

    def on_apply_change_clicked(self, evt):
        if self.dvlc.GetItemCount() < 1:
            return
        if self.processedObo is not None:
            self.processedObo.update(**self.detailPanel.get_data())
            self._save_processed_obo()
            self._update_select_row(self.processedObo)
            self.processedObo = None

    def _update_select_row(self, event):
        _row = self.dvlc.GetSelectedRow()
        _icon = self._get_obo_icon(event)
        self.dvlc.SetValue(_icon, _row, 0)
        self.dvlc.SetValue(event.name, _row, 1)

    def on_add_obo(self, evt):
        self._handle_unsaved_obo()
        if self.processedObo is None:
            _type = self.detailPanel.ctrlEvtTypEdit.GetValue()
            self.processedObo = Observable(name='*%s' % _type, description='Observable Description')
            self.processedObo.readonly = False
            self.processedObo.type = _type
            self.processedObo.attach_default_data()
            self._add_obo(self.processedObo, self.SRC_OBO_MGR)
            self.detailPanel.set_data(self.processedObo)

    def on_remove_event(self, evt):
        _selected = self.dvlc.GetSelectedRow()
        _item = self.dvlc.RowToItem(_selected)
        _item_data = self.dvlc.GetItemData(_item)
        if _selected != -1:
            _obo_name = self.dvlc.GetTextValue(_selected, 0)
            if _item_data == self.SRC_OBO_MGR:
                self.oboMgr.unregister_obo(_obo_name)
                self.dvlc.DeleteItem(_selected)
        self.processedObo = None

    def deserialize(self, data):
        if data is None:
            return

    def serialize(self):
        _d = self.oboMgr.get_all_obos()
        return _d
