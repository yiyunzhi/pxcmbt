import wx
import wx.dataview as dv
from .define_gui import *
from application.define import EnumMBTEventType
from application.class_mbt_event import MBTEventManager, MBTEvent
from .dialog_event_editor import EventDetailEditorDialog
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
    def __init__(self, parent, event_data=None):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.uuid = None
        self.role = 'EnumPaneRole.PANE_EVENT'
        self.shouldSave = False
        self.eventMgr = MBTEventManager()
        self.eventMgr.deserialize(event_data)
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.evtLstSizer = wx.BoxSizer(wx.VERTICAL)
        self.evtDetailSizer = wx.BoxSizer(wx.VERTICAL)
        self.evtLstToolsSizer = wx.BoxSizer(wx.HORIZONTAL)
        # evt list tools
        self.ctrlSearch = wx.SearchCtrl(self, size=(160, -1), style=wx.TE_PROCESS_ENTER)
        self.ctrlSearch.ShowCancelButton(True)
        _srch_w, _srch_h = self.ctrlSearch.GetSize()
        self.evtAddBtn = wx.Button(self, wx.ID_ANY, '+', size=(_srch_h, _srch_h))
        self.evtRemoveBtn = wx.Button(self, wx.ID_ANY, '-', size=(_srch_h, _srch_h))
        # self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch, self.search)
        # self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel, self.search)
        # self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch, self.search)
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
                self._add_event(evt)
        # bind events
        self.evtAddBtn.Bind(wx.EVT_BUTTON, self.on_add_event)
        self.evtRemoveBtn.Bind(wx.EVT_BUTTON, self.on_remove_event)
        self.dvlc.Bind(dv.EVT_DATAVIEW_ITEM_ACTIVATED, self.on_dv_item_activated)
        # layout
        self.evtLstToolsSizer.Add(self.ctrlSearch, 0)
        self.evtLstToolsSizer.AddStretchSpacer(1)
        self.evtLstToolsSizer.Add(self.evtAddBtn, 0)
        self.evtLstToolsSizer.Add(self.evtRemoveBtn, 0)
        self.evtLstSizer.Add(self.evtLstToolsSizer, 0, wx.EXPAND)
        self.evtLstSizer.AddSpacer(10)
        self.evtLstSizer.Add(self.dvlc, 1, wx.EXPAND)
        self.evtDetailSizer.Add(self.detailPanel, 1, wx.EXPAND)
        self.mainSizer.Add(self.evtLstSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.evtDetailSizer, 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)
        self.Layout()
        self.Fit()

    def _add_event(self, evt):
        _incoming_icon = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR, (10, 10))
        _outgoing_icon = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR, (10, 10))
        _icon = _incoming_icon if evt.type == EnumMBTEventType.INCOMING else _outgoing_icon
        self.dvlc.AppendItem((_icon, evt.name))

    def on_dv_item_activated(self, evt: dv.DataViewEvent):
        _selected_row = self.dvlc.GetSelectedRow()
        _selected_evt_name = self.dvlc.GetTextValue(_selected_row, 1)
        self.detailPanel.set_data(self.eventMgr.get_event(_selected_evt_name))

    def on_add_event(self, evt):
        _dlg = EventDetailEditorDialog(self)
        _ret = _dlg.ShowModal()
        if _ret == wx.ID_OK:
            _evt = MBTEvent(**_dlg.get_event())
            _evt.readonly = False
            self.eventMgr.register_event(_evt)
            self._add_event(_evt)

    def on_remove_event(self, evt):
        _selected = self.dvlc.GetSelectedRow()
        _evt_name = self.dvlc.GetTextValue(_selected, 0)
        self.eventMgr.unregister_event(_evt_name)
        self.dvlc.DeleteItem(_selected)

    def deserialize(self, data):
        if data is None:
            return

    def serialize(self):
        _d = self.eventMgr.get_all_events()
        return _d
