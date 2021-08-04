import wx
import wx.dataview as dv
from .define_gui import *
from application.define import EnumMBTEventType
from application.class_mbt_event import MBTEventManager, MBTEvent
from .panel_event_detail import EventDetailPanel


class ComboboxRenderer(dv.DataViewCustomRenderer):
    def __init__(self, *args, **kw):
        dv.DataViewCustomRenderer.__init__(self, *args, **kw)
        self.value = None
        self.EnableEllipsize(wx.ELLIPSIZE_END)

    def SetValue(self, value):
        # self.log.write('SetValue: %s' % value)
        self.value = value
        return True

    def GetValue(self):
        return self.value

    def GetSize(self):
        # Return the size needed to display the value.  The renderer
        # has a helper function we can use for measuring text that is
        # aware of any custom attributes that may have been set for
        # this item.
        value = self.value if self.value else ""
        size = self.GetTextExtent(value)
        size += (2, 2)
        # self.log.write('GetSize("{}"): {}'.format(value, size))
        return size

    # def GetEditorCtrl(self):
    #    return wx.ComboBox(self, wx.ID_ANY, value='A', values=['A', 'B', 'C'])

    def Render(self, rect, dc, state):
        # if state != 0:
        #    self.log.write('Render: %s, %d' % (rect, state))

        if not state & dv.DATAVIEW_CELL_SELECTED:
            # we'll draw a shaded background to see if the rect correctly
            # fills the cell
            dc.SetBrush(wx.Brush('#ffd0d0'))
            dc.SetPen(wx.TRANSPARENT_PEN)
            rect.Deflate(1, 1)
            dc.DrawRoundedRectangle(rect, 2)

        # And then finish up with this helper function that draws the
        # text for us, dealing with alignment, font and color
        # attributes, etc.
        value = self.value if self.value else ""
        self.RenderText(value,
                        0,  # x-offset
                        rect,
                        dc,
                        state  # wxDataViewCellRenderState flags
                        )
        return True

    def ActivateCell(self, rect, model, item, col, mouse_event):
        return True

    # The HasEditorCtrl, CreateEditorCtrl and GetValueFromEditorCtrl
    # methods need to be implemented if this renderer is going to
    # support in-place editing of the cell value, otherwise they can
    # be omitted.

    def HasEditorCtrl(self):
        return True

    def CreateEditorCtrl(self, parent, label_rect, value):
        _ctrl = wx.ComboBox(self, wx.ID_ANY, value='A', values=['A', 'B', 'C'])
        return _ctrl
        # _ctrl = wx.TextCtrl(parent,
        #                     value=value,
        #                     pos=label_rect.Position,
        #                     size=label_rect.Size)
        #
        # # select the text and put the caret at the end
        # _ctrl.SetInsertionPointEnd()
        # _ctrl.SelectAll()
        # return _ctrl

    def GetValueFromEditorCtrl(self, editor):
        value = editor.GetValue()
        return value

    # The LeftClick and Activate methods serve as notifications
    # letting you know that the user has either clicked or
    # double-clicked on an item.  Implementing them in your renderer
    # is optional.

    def LeftClick(self, pos, cell_rect, model, item, col):
        return True

    def Activate(self, cell_rect, model, item, col):
        return True


class EventEditorPanel(wx.Panel):
    SRC_EVT_MGR = 0
    SRC_EVT_BUILTIN = 1

    def __init__(self, parent, event_data=None, built_in_event_data=None):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.uuid = None
        self.role = 'EnumPaneRole.PANE_EVENT'
        self.shouldSave = False
        self.newEventName = '*NewEvent'
        self.processedEvt = None
        self.builtInEvtData = built_in_event_data
        self.eventMgr = MBTEventManager()
        self.eventMgr.deserialize(event_data)
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.evtLstSizer = wx.BoxSizer(wx.VERTICAL)
        self.evtDetailSizer = wx.BoxSizer(wx.VERTICAL)
        self.evtLstToolsSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.evtActionSizer = wx.BoxSizer(wx.HORIZONTAL)
        # evt list tools
        self.ctrlSearch = wx.SearchCtrl(self, size=(160, -1), style=wx.TE_PROCESS_ENTER)
        self.ctrlSearch.ShowCancelButton(True)
        _srch_w, _srch_h = self.ctrlSearch.GetSize()
        self.evtAddBtn = wx.Button(self, wx.ID_ANY, '+', size=(_srch_h, _srch_h))
        self.evtAddBtn.SetToolTip('Add a new event')
        self.evtRemoveBtn = wx.Button(self, wx.ID_ANY, '-', size=(_srch_h, _srch_h))
        self.evtRemoveBtn.SetToolTip('Remove a new event')
        self.btnApplyChange = wx.Button(self, wx.ID_ANY, 'ApplyChange')
        # self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch, self.search)
        # self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel, self.search)
        # self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch, self.search)
        self.btnApplyChange.Bind(wx.EVT_BUTTON, self.on_apply_change_clicked)
        # create detail panel
        self.detailPanel = EventDetailPanel(self)
        # Create a dataview control
        self.dvlc = dv.DataViewListCtrl(self, style=wx.LC_REPORT | dv.DV_NO_HEADER | dv.DV_ROW_LINES)
        self.dvlc.SetRowHeight(16)

        self.dvlc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.dvlc.AppendBitmapColumn('Direction', 0, width=18)
        self.dvlc.AppendTextColumn('Name', width=120)
        _incoming_icon = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR, (10, 10))
        _outgoing_icon = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR, (10, 10))
        for name, evt in self.eventMgr.get_all_events().items():
            if evt.visible:
                self._add_event(evt, self.SRC_EVT_MGR)
        if self.builtInEvtData is not None:
            [self._add_event(evt, self.SRC_EVT_BUILTIN) for name, evt in self.builtInEvtData.items() if evt.visible]
        # bind events
        self.evtAddBtn.Bind(wx.EVT_BUTTON, self.on_add_event)
        self.evtRemoveBtn.Bind(wx.EVT_BUTTON, self.on_remove_event)
        # self.dvlc.Bind(dv.EVT_DATAVIEW_ITEM_ACTIVATED, self.on_dv_item_activated)
        self.dvlc.Bind(dv.EVT_DATAVIEW_SELECTION_CHANGED, self.on_dv_item_select_changed)

        # layout
        self.evtLstToolsSizer.Add(self.ctrlSearch, 0)
        self.evtLstToolsSizer.AddStretchSpacer(1)
        self.evtLstToolsSizer.Add(self.evtAddBtn, 0)
        self.evtLstToolsSizer.Add(self.evtRemoveBtn, 0)
        self.evtLstSizer.Add(self.evtLstToolsSizer, 0, wx.EXPAND)
        self.evtLstSizer.AddSpacer(10)
        self.evtLstSizer.Add(self.dvlc, 1, wx.EXPAND)
        self.evtDetailSizer.Add(self.detailPanel, 1, wx.EXPAND)
        self.evtDetailSizer.Add(self.evtActionSizer, 0, wx.EXPAND, 5)
        self.evtActionSizer.AddStretchSpacer(1)
        self.evtActionSizer.Add(self.btnApplyChange, 0, wx.ALL, 5)
        self.mainSizer.Add(self.evtLstSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.evtDetailSizer, 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)
        self.Layout()
        self.Fit()

    def _add_event(self, evt, data=SRC_EVT_MGR, select=True):
        _icon = self._get_event_icon(evt)
        self.dvlc.AppendItem((_icon, evt.name), data)
        if select:
            self.dvlc.Select(self.dvlc.RowToItem(self.dvlc.GetItemCount() - 1))

    def _get_event_icon(self, event):
        _incoming_icon = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR, (10, 10))
        _outgoing_icon = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR, (10, 10))
        return _incoming_icon if event.type == EnumMBTEventType.INCOMING.value else _outgoing_icon

    def _handle_unsaved_event(self):
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
                self._save_processed_event()
            elif _ret == wx.NO:
                _exist = self.eventMgr.has_event(self.processedEvt.name)
                if not _exist:
                    self.dvlc.DeleteItem(_selected_row)
            self.processedEvt = None

    def on_dv_item_select_changed(self, evt: dv.DataViewEvent):
        _selected_row = self.dvlc.GetSelectedRow()
        _item = self.dvlc.RowToItem(_selected_row)
        _item_data = self.dvlc.GetItemData(_item)
        if _selected_row == -1:
            self.detailPanel.clear()
            return
        _selected_evt_name = self.dvlc.GetTextValue(_selected_row, 1)
        if self.processedEvt is not None:
            if _selected_evt_name != self.processedEvt.name:
                self._handle_unsaved_event()
        if self.processedEvt is None:
            if _item_data == self.SRC_EVT_MGR:
                _evt = self.eventMgr.get_event(_selected_evt_name)
            elif _item_data == self.SRC_EVT_BUILTIN:
                _evt = self.builtInEvtData.get(_selected_evt_name)
            else:
                _evt = None
            if _evt is not None:
                self.detailPanel.set_data(_evt)
                if _item_data == self.SRC_EVT_MGR:
                    self.processedEvt = _evt
                if _evt.readonly:
                    self.detailPanel.Disable()
                    self.evtRemoveBtn.Disable()
                else:
                    self.detailPanel.Enable()
                    self.evtRemoveBtn.Enable()

    def _save_processed_event(self):
        if self.processedEvt is not None:
            _exist = self.eventMgr.has_event(self.processedEvt.name)
            if _exist:
                if self.eventMgr.is_event_changed(self.processedEvt):
                    self.eventMgr.update(self.processedEvt)
            else:
                self.eventMgr.register_event(self.processedEvt)

    def on_apply_change_clicked(self, evt):
        if self.dvlc.GetItemCount() < 1:
            return
        if self.processedEvt is not None:
            self.processedEvt.update(**self.detailPanel.get_data())
            self._save_processed_event()
            self._update_select_row(self.processedEvt)
            self.processedEvt = None

    def _update_select_row(self, event):
        _row = self.dvlc.GetSelectedRow()
        _icon = self._get_event_icon(event)
        self.dvlc.SetValue(_icon, _row, 0)
        self.dvlc.SetValue(event.name, _row, 1)

    def on_add_event(self, evt):
        self._handle_unsaved_event()
        if self.processedEvt is None:
            self.processedEvt = MBTEvent(name=self.newEventName, description='Event Description')
            self.processedEvt.readonly = False
            self._add_event(self.processedEvt, self.SRC_EVT_MGR)
            self.detailPanel.set_data(self.processedEvt)

    def on_remove_event(self, evt):
        _selected = self.dvlc.GetSelectedRow()
        _item = self.dvlc.RowToItem(_selected)
        _item_data = self.dvlc.GetItemData(_item)
        if _selected != -1:
            _evt_name = self.dvlc.GetTextValue(_selected, 0)
            if _item_data == self.SRC_EVT_MGR:
                self.eventMgr.unregister_event(_evt_name)
                self.dvlc.DeleteItem(_selected)
        self.processedEvt = None

    def deserialize(self, data):
        if data is None:
            return

    def serialize(self):
        _d = self.eventMgr.get_all_events()
        return _d
