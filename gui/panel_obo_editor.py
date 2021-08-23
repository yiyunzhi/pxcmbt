import wx
import wx.dataview as dv
from application.class_observable import *
from application.define import *
from .define_gui import *
from .panel_obo_detail import OBODetailPanel
from .util_icon_repo import UtilIconRepo
from application.utils_helper import util_get_uuid_string


class OBOLstMixin:
    def __init__(self, obo_data):
        self.oboMgr = MBTOBOManager()
        self.oboMgr.register_obos(obo_data)
        self._iconRepo = UtilIconRepo()
        self.processedObo = None
        # Create a dataview control
        self.dvlc = dv.DataViewListCtrl(self, style=wx.LC_REPORT | dv.DV_NO_HEADER | dv.DV_ROW_LINES)
        self.dvlc.SetRowHeight(16)
        self.dvlc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.dvlc.AppendBitmapColumn('Icon', 0, width=22)
        self.dvlc.AppendTextColumn('Name', width=120)
        _col2 = self.dvlc.AppendTextColumn('uuid', width=-1)
        _col2.SetHidden(True)
        for name, obo in self.oboMgr.get_all_obos().items():
            if obo.visible:
                self.add_obo(obo)
        # self.dvlc.Bind(dv.EVT_DATAVIEW_ITEM_ACTIVATED, self.on_dv_item_activated)
        self.dvlc.Bind(dv.EVT_DATAVIEW_SELECTION_CHANGED, self.on_dv_item_select_changed)

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

    def _save_processed_obo(self):
        if self.processedObo is not None:
            _exist = self.oboMgr.has_obo(self.processedObo.name)
            if _exist:
                if self.oboMgr.is_obo_changed(self.processedObo):
                    self.oboMgr.update(self.processedObo)
            else:
                self.oboMgr.register_obo(self.processedObo)

    def _update_select_row(self, event):
        _row = self.dvlc.GetSelectedRow()
        _icon = self.get_obo_icon(event)
        self.dvlc.SetValue(_icon, _row, 0)
        self.dvlc.SetValue(event.name, _row, 1)

    def on_dv_item_select_changed(self, evt: dv.DataViewEvent):
        _selected_row = self.dvlc.GetSelectedRow()
        if _selected_row == -1:
            self.clear_details()
            return
        _item = self.dvlc.RowToItem(_selected_row)
        _item_data = self.dvlc.GetItemData(_item)
        _selected_obo_name = self.dvlc.GetTextValue(_selected_row, 1)
        _selected_obo_uuid = self.dvlc.GetTextValue(_selected_row, 2)
        if self.processedObo is not None:
            if _selected_obo_uuid != self.processedObo.uuid and not self.processedObo.readonly:
                self._handle_unsaved_obo()
        if self.processedObo is None:
            _obo = self.oboMgr.get_obo(_selected_obo_uuid)
            if _obo is not None:
                self.set_detail(_obo)
                if _obo.readonly:
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

    def add_obo(self, obo, select=True):
        _icon = self.get_obo_icon(obo)
        self.dvlc.AppendItem((_icon, obo.name, obo.uuid))
        if select:
            self.dvlc.Select(self.dvlc.RowToItem(self.dvlc.GetItemCount() - 1))

    def get_obo_icon(self, obo):
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


class CustomOBOListPanel(wx.Panel, OBOLstMixin):
    def __init__(self, obo_data, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        OBOLstMixin.__init__(self, obo_data)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.oboLstToolsSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ctrlSearch = wx.SearchCtrl(self, size=(160, -1), style=wx.TE_PROCESS_ENTER)
        self.ctrlSearch.ShowCancelButton(True)
        _srch_w, _srch_h = self.ctrlSearch.GetSize()
        self.oboAddBtn = wx.Button(self, wx.ID_ANY, '+', size=(_srch_h, _srch_h))
        self.oboAddBtn.SetToolTip('Add a new OBO')
        self.oboRemoveBtn = wx.Button(self, wx.ID_ANY, '-', size=(_srch_h, _srch_h))
        self.oboRemoveBtn.SetToolTip('Remove a OBO')
        # bind events
        self.oboAddBtn.Bind(wx.EVT_BUTTON, self.on_add_obo)
        self.oboRemoveBtn.Bind(wx.EVT_BUTTON, self.on_remove_event)

        # layout
        self.oboLstToolsSizer.Add(self.ctrlSearch, 0)
        self.oboLstToolsSizer.AddStretchSpacer(1)
        self.oboLstToolsSizer.Add(self.oboAddBtn, 0)
        self.oboLstToolsSizer.Add(self.oboRemoveBtn, 0)
        self.mainSizer.Add(self.oboLstToolsSizer, 0, wx.EXPAND)
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
            self.oboRemoveBtn.Enable()
        else:
            _parent.detailPanel.Disable()
            self.oboRemoveBtn.Disable()

    def on_add_obo(self, evt):
        _parent = self.get_top_level_parent()
        if _parent is None:
            return
        self._handle_unsaved_obo()
        if self.processedObo is None:
            _dlg = wx.SingleChoiceDialog(self, 'Select the type', 'OBO Type', EnumOBOType.ALL_VALUES.value)
            _ret = _dlg.ShowModal()
            if _ret == wx.ID_OK:
                _select_type = _dlg.GetStringSelection()
                _parent.detailPanel.ctrlEvtTypEdit.SetValue(_select_type)
                self.processedObo = Observable(name='*%s' % _select_type, description='Observable Description')
                self.processedObo.uuid = util_get_uuid_string()
                self.processedObo.readonly = False
                self.processedObo.type = _select_type
                self.processedObo.attach_default_data()
                self.add_obo(self.processedObo)
                _parent.detailPanel.set_data(self.processedObo)

    def on_remove_event(self, evt):
        _selected = self.dvlc.GetSelectedRow()
        _item = self.dvlc.RowToItem(_selected)
        _item_data = self.dvlc.GetItemData(_item)
        if _selected != -1:
            _obo_name = self.dvlc.GetTextValue(_selected, 0)
            self.oboMgr.unregister_obo(_obo_name)
            self.dvlc.DeleteItem(_selected)
        self.processedObo = None

    def apply_change(self):
        if self.dvlc.GetItemCount() < 1:
            return
        if self.processedObo is not None:
            _detail = self.get_detail()
            if _detail is None:
                return
            self.processedObo.update(**_detail)
            self._save_processed_obo()
            self._update_select_row(self.processedObo)
            self.processedObo = None


class BuiltinOBOListPanel(wx.Panel, OBOLstMixin):
    def __init__(self, obo_data, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        OBOLstMixin.__init__(self, obo_data)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.oboLstToolsSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ctrlSearch = wx.SearchCtrl(self, size=(160, -1), style=wx.TE_PROCESS_ENTER)
        self.ctrlSearch.ShowCancelButton(True)
        # bind events
        # layout
        self.oboLstToolsSizer.Add(self.ctrlSearch, 0)
        self.mainSizer.Add(self.oboLstToolsSizer, 0, wx.EXPAND)
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


class OBOLstBook(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, wx.ID_ANY, size=(21, 21), style=wx.BK_LEFT)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.on_page_changing)

    def on_page_changing(self, evt):
        _old_id = evt.GetOldSelection()
        if _old_id == 0:
            _page = self.GetPage(0)
            _page._handle_unsaved_obo()


class OBOEditorPanel(wx.Panel):
    def __init__(self, parent, obo_data=None, built_in_obo_data=None):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.uuid = None
        self.role = 'EnumPaneRole.PANE_OBO'
        self.shouldSave = False
        self.builtInOboData = built_in_obo_data
        self._iconRepo = UtilIconRepo()
        self.oboBook = OBOLstBook(self)
        self.oboBook.SetMinSize((240, -1))
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.oboLstSizer = wx.BoxSizer(wx.VERTICAL)
        self.oboDetailSizer = wx.BoxSizer(wx.VERTICAL)
        self.oboLstToolsSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.oboActionSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btnApplyChange = wx.Button(self, wx.ID_ANY, 'ApplyChange')
        self.btnApplyChange.Bind(wx.EVT_BUTTON, self.on_apply_change_clicked)
        # create panels
        self.detailPanel = OBODetailPanel(self)
        self.customOboLstPanel = CustomOBOListPanel(obo_data, self.oboBook)
        self.builtinOboLstPanel = BuiltinOBOListPanel(built_in_obo_data, self.oboBook)
        self.oboBook.AddPage(self.customOboLstPanel, 'Custom')
        self.oboBook.AddPage(self.builtinOboLstPanel, 'Builtin')
        # add data view
        self.oboBook.SetSelection(0)
        # bind events
        # layout
        self.oboDetailSizer.Add(self.detailPanel, 1, wx.EXPAND)
        self.oboDetailSizer.Add(self.oboActionSizer, 0, wx.EXPAND, 5)
        self.oboActionSizer.AddStretchSpacer(1)
        self.oboActionSizer.Add(self.btnApplyChange, 0, wx.ALL, 5)
        self.mainSizer.Add(self.oboBook, 0, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.oboDetailSizer, 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)
        self.Layout()
        self.Fit()

    def on_apply_change_clicked(self, evt):
        _page = self.oboBook.GetSelection()
        if _page == 0:
            _page = self.oboBook.GetPage(_page)
            _page.apply_change()

    def deserialize(self, data):
        if data is None:
            return

    def serialize(self):
        _d = self.customOboLstPanel.oboMgr.get_all_obos()
        _dc = dict()
        [_dc.update({v.name: v}) for k, v in _d.items()]
        return _dc
