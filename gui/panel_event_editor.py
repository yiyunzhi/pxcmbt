import wx
import wx.dataview as dv
from application.class_mbt_event import *
from application.define import *
from .define_gui import *
from .panel_event_detail import EventDetailPanel
from .util_icon_repo import UtilIconRepo
from application.utils_helper import util_get_uuid_string


class EVTLstMixin:
    def __init__(self, evt_data):
        self.evtMgr = MBTEventManager()
        self.evtMgr.register_events(evt_data)
        self._iconRepo = UtilIconRepo()
        self.processedEvt = None
        # Create a dataview control
        self.dvlc = dv.DataViewListCtrl(self, style=wx.LC_REPORT | dv.DV_NO_HEADER | dv.DV_ROW_LINES)
        self.dvlc.SetRowHeight(16)
        self.dvlc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.dvlc.AppendBitmapColumn('Icon', 0, width=22)
        self.dvlc.AppendTextColumn('Name', width=120)
        _col2 = self.dvlc.AppendTextColumn('uuid', width=-1)
        _col2.SetHidden(True)
        for name, evt in self.evtMgr.get_all_events().items():
            if evt.visible:
                self.add_evt(evt)
        # self.dvlc.Bind(dv.EVT_DATAVIEW_ITEM_ACTIVATED, self.on_dv_item_activated)
        self.dvlc.Bind(dv.EVT_DATAVIEW_SELECTION_CHANGED, self.on_dv_item_select_changed)

    def _handle_unsaved_evt(self):
        if self.dvlc.GetItemCount() < 1:
            return
        _selected_row = self.dvlc.GetSelectedRow()
        if _selected_row != -1:
            _selected_evt_name = self.dvlc.GetTextValue(_selected_row, 1)
        else:
            return
        if self.processedEvt is not None:
            _ret = wx.MessageBox('Edit of the event not finish, do you want save it?', 'Save Event Change',
                                 style=wx.YES_NO)
            if _ret == wx.YES:
                self._save_processed_evt()
            elif _ret == wx.NO:
                _exist = self.evtMgr.has_event(self.processedEvt.uuid)
                if not _exist:
                    self.dvlc.DeleteItem(_selected_row)
            self.processedEvt = None

    def _save_processed_evt(self):
        if self.processedEvt is not None:
            _exist = self.evtMgr.has_event(self.processedEvt.name)
            if _exist:
                if self.evtMgr.is_event_changed(self.processedEvt):
                    self.evtMgr.update(self.processedEvt)
            else:
                self.evtMgr.register_event(self.processedEvt)

    def _update_select_row(self, event):
        _row = self.dvlc.GetSelectedRow()
        _icon = self.get_evt_icon(event)
        self.dvlc.SetValue(_icon, _row, 0)
        self.dvlc.SetValue(event.name, _row, 1)

    def on_dv_item_select_changed(self, evt: dv.DataViewEvent):
        _selected_row = self.dvlc.GetSelectedRow()
        if _selected_row == -1:
            self.clear_details()
            return
        _item = self.dvlc.RowToItem(_selected_row)
        _item_data = self.dvlc.GetItemData(_item)
        _selected_evt_name = self.dvlc.GetTextValue(_selected_row, 1)
        _selected_evt_uuid = self.dvlc.GetTextValue(_selected_row, 2)
        if self.processedEvt is not None:
            if _selected_evt_uuid != self.processedEvt.uuid and not self.processedEvt.readonly:
                self._handle_unsaved_evt()
        if self.processedEvt is None:
            _evt = self.evtMgr.get_event(_selected_evt_uuid)
            if _evt is not None:
                self.set_detail(_evt)
                if _evt.readonly:
                    self.enable_ctrls(False)
                else:
                    self.enable_ctrls(True)

    def get_top_level_parent(self):
        raise NotImplemented()

    def set_detail(self, data):
        raise NotImplemented()

    def get_detail(self):
        raise NotImplemented()

    def clear_details(self):
        raise NotImplemented()

    def enable_ctrls(self, state=True):
        raise NotImplemented()

    def add_evt(self, evt, select=True):
        _icon = self.get_evt_icon(evt)
        self.dvlc.AppendItem((_icon, evt.name, evt.uuid))
        if select:
            self.dvlc.Select(self.dvlc.RowToItem(self.dvlc.GetItemCount() - 1))

    def get_evt_icon(self, evt):
        _img_lst = self._iconRepo.get_image_list()
        if evt.type == EnumMBTEventType.INCOMING.value:
            return wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR, (10, 10))
        elif evt.type == EnumMBTEventType.OUTGOING.value:
            return wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR, (10, 10))
        else:
            return _img_lst.GetBitmap(self._iconRepo.binaryIcon)


class CustomEvtListPanel(wx.Panel, EVTLstMixin):
    def __init__(self, evt_data, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        EVTLstMixin.__init__(self, evt_data)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.evtLstToolsSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ctrlSearch = wx.SearchCtrl(self, size=(160, -1), style=wx.TE_PROCESS_ENTER)
        self.ctrlSearch.ShowCancelButton(True)
        _srch_w, _srch_h = self.ctrlSearch.GetSize()
        self.evtAddBtn = wx.Button(self, wx.ID_ANY, '+', size=(_srch_h, _srch_h))
        self.evtAddBtn.SetToolTip('Add a new evt')
        self.evtRemoveBtn = wx.Button(self, wx.ID_ANY, '-', size=(_srch_h, _srch_h))
        self.evtRemoveBtn.SetToolTip('Remove a evt')
        # bind events
        self.evtAddBtn.Bind(wx.EVT_BUTTON, self.on_add_evt)
        self.evtRemoveBtn.Bind(wx.EVT_BUTTON, self.on_remove_event)

        # layout
        self.evtLstToolsSizer.Add(self.ctrlSearch, 0)
        self.evtLstToolsSizer.AddStretchSpacer(1)
        self.evtLstToolsSizer.Add(self.evtAddBtn, 0)
        self.evtLstToolsSizer.Add(self.evtRemoveBtn, 0)
        self.mainSizer.Add(self.evtLstToolsSizer, 0, wx.EXPAND)
        self.mainSizer.AddSpacer(10)
        self.mainSizer.Add(self.dvlc, 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)
        self.Layout()

    def get_top_level_parent(self):
        _parent = self.GetParent()
        if _parent is None:
            return
        _parent = _parent.GetParent()
        if _parent is None:
            return
        return _parent

    def get_detail(self):
        _parent = self.get_top_level_parent()
        if _parent is None:
            return
        return _parent.detailPanel.get_data()

    def set_detail(self, data):
        _parent = self.get_top_level_parent()
        if _parent is None:
            return
        _parent.detailPanel.set_data(data)

    def clear_details(self):
        _parent = self.get_top_level_parent()
        if _parent is None:
            return
        _parent.detailPanel.clear()

    def enable_ctrls(self, state=True):
        _parent = self.get_top_level_parent()
        if _parent is None:
            return
        if state:
            _parent.detailPanel.Enable()
            self.evtRemoveBtn.Enable()
        else:
            _parent.detailPanel.Disable()
            self.evtRemoveBtn.Disable()

    def on_add_evt(self, evt):
        _parent = self.get_top_level_parent()
        if _parent is None:
            return
        self._handle_unsaved_evt()
        if self.processedEvt is None:
            _dlg = wx.SingleChoiceDialog(self, 'Select the type', 'evt Type', EnumMBTEventType.ALL_VALUES.value)
            _ret = _dlg.ShowModal()
            if _ret == wx.ID_OK:
                _select_type = _dlg.GetStringSelection()
                _parent.detailPanel.ctrlEvtTypEdit.SetValue(_select_type)
                self.processedEvt = MBTEvent(name='*%s' % _select_type, description='Event Description')
                self.processedEvt.uuid = util_get_uuid_string()
                self.processedEvt.readonly = False
                self.processedEvt.type = _select_type
                self.add_evt(self.processedEvt)
                _parent.detailPanel.set_data(self.processedEvt)

    def on_remove_event(self, evt):
        _selected = self.dvlc.GetSelectedRow()
        _item = self.dvlc.RowToItem(_selected)
        _item_data = self.dvlc.GetItemData(_item)
        if _selected != -1:
            _evt_name = self.dvlc.GetTextValue(_selected, 0)
            self.evtMgr.unregister_event(_evt_name)
            self.dvlc.DeleteItem(_selected)
        self.processedEvt = None

    def apply_change(self):
        if self.dvlc.GetItemCount() < 1:
            return
        if self.processedEvt is not None:
            _detail = self.get_detail()
            if _detail is None:
                return
            self.processedEvt.update(**_detail)
            self._save_processed_evt()
            self._update_select_row(self.processedEvt)
            self.processedEvt = None


class BuiltinEvtListPanel(wx.Panel, EVTLstMixin):
    def __init__(self, evt_data, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        EVTLstMixin.__init__(self, evt_data)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.evtLstToolsSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ctrlSearch = wx.SearchCtrl(self, size=(160, -1), style=wx.TE_PROCESS_ENTER)
        self.ctrlSearch.ShowCancelButton(True)
        # bind events
        # layout
        self.evtLstToolsSizer.Add(self.ctrlSearch, 0)
        self.mainSizer.Add(self.evtLstToolsSizer, 0, wx.EXPAND)
        self.mainSizer.AddSpacer(10)
        self.mainSizer.Add(self.dvlc, 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)
        self.Layout()

    def get_top_level_parent(self):
        _parent = self.GetParent()
        if _parent is None:
            return
        _parent = _parent.GetParent()
        if _parent is None:
            return
        return _parent

    def set_detail(self, data):
        _parent = self.get_top_level_parent()
        if _parent is None:
            return
        _parent.detailPanel.set_data(data)

    def clear_details(self):
        _parent = self.get_top_level_parent()
        if _parent is None:
            return
        _parent.detailPanel.clear()

    def enable_ctrls(self, state=True):
        _parent = self.get_top_level_parent()
        if _parent is None:
            return
        if state:
            _parent.detailPanel.Enable()
        else:
            _parent.detailPanel.Disable()


class EVTLstBook(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, wx.ID_ANY, size=(21, 21), style=wx.BK_LEFT)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.on_page_changing)

    def on_page_changing(self, evt):
        _old_id = evt.GetOldSelection()
        if _old_id == 0:
            _page = self.GetPage(0)
            _page._handle_unsaved_evt()


class EventEditorPanel(wx.Panel):
    def __init__(self, parent, evt_data=None, built_in_evt_data=None):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.uuid = None
        self.role = 'EnumPaneRole.PANE_evt'
        self.shouldSave = False
        self.builtInevtData = built_in_evt_data
        self._iconRepo = UtilIconRepo()
        self.evtBook = EVTLstBook(self)
        self.evtBook.SetMinSize((240, -1))
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.evtLstSizer = wx.BoxSizer(wx.VERTICAL)
        self.evtDetailSizer = wx.BoxSizer(wx.VERTICAL)
        self.evtLstToolsSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.evtActionSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btnApplyChange = wx.Button(self, wx.ID_ANY, 'ApplyChange')
        self.btnApplyChange.Bind(wx.EVT_BUTTON, self.on_apply_change_clicked)
        # create panels
        self.detailPanel = EventDetailPanel(self)
        self.customevtLstPanel = CustomEvtListPanel(evt_data, self.evtBook)
        self.builtinevtLstPanel = BuiltinEvtListPanel(built_in_evt_data, self.evtBook)
        self.evtBook.AddPage(self.customevtLstPanel, 'Custom')
        self.evtBook.AddPage(self.builtinevtLstPanel, 'Builtin')
        # add data view
        self.evtBook.SetSelection(0)
        # bind events
        # layout
        self.evtDetailSizer.Add(self.detailPanel, 1, wx.EXPAND)
        self.evtDetailSizer.Add(self.evtActionSizer, 0, wx.EXPAND, 5)
        self.evtActionSizer.AddStretchSpacer(1)
        self.evtActionSizer.Add(self.btnApplyChange, 0, wx.ALL, 5)
        self.mainSizer.Add(self.evtBook, 0, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.evtDetailSizer, 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)
        self.Layout()
        self.Fit()

    def on_apply_change_clicked(self, evt):
        _page = self.evtBook.GetSelection()
        if _page == 0:
            _page = self.evtBook.GetPage(_page)
            _page.apply_change()

    def deserialize(self, data):
        if data is None:
            return

    def serialize(self):
        _d = self.customevtLstPanel.evtMgr.get_all_events()
        _dc = dict()
        [_dc.update({v.name: v}) for k, v in _d.items()]
        return _dc
