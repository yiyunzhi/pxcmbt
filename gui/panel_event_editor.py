import wx
import wx.dataview as dv
from .define_gui import *
from application.define import EnumMBTEventType
from application.class_mbt_event import MBTEventManager, MBTEvent


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
        self.ctrlEvtTypEdit = wx.ComboBox(self, wx.ID_ANY, value=EnumMBTEventType.INCOMING,
                                          choices=EnumMBTEventType.ALL_VALUES)
        self.ctrlEvtPermissionLabel = wx.StaticText(self, wx.ID_ANY, 'Permission:')
        self.ctrlEvtPermissionEdit = wx.StaticText(self, wx.ID_ANY, 'R')
        self.ctrlEvtDescLabel = wx.StaticText(self, wx.ID_ANY, 'Description:')
        self.ctrlEvtDescEdit = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_MULTILINE)
        self._formSizer.Add(self.ctrlEvtNameLabel, (0, 0), flag=wx.TOP, border=4)
        self._formSizer.Add(self.ctrlEvtNameEdit, (0, 1), span=(1, 10), flag=wx.EXPAND)
        self._formSizer.Add(self.ctrlEvtTypLabel, (1, 0), flag=wx.TOP, border=4)
        self._formSizer.Add(self.ctrlEvtTypEdit, (1, 1), span=(1, 5))
        self._formSizer.Add(self.ctrlEvtPermissionLabel, (2, 0), flag=wx.TOP, border=4)
        self._formSizer.Add(self.ctrlEvtPermissionEdit, (2, 1), span=(1, 5),flag=wx.TOP, border=4)
        self._formSizer.Add(self.ctrlEvtDescLabel, (3, 0), flag=wx.TOP, border=4)
        self._formSizer.Add(self.ctrlEvtDescEdit, (3, 1), span=(5, 10), flag=wx.EXPAND|wx.TOP, border=4)

        # init data table
        self.dvlc = dv.DataViewListCtrl(self, style=dv.DV_ROW_LINES)
        self.dvlc.AppendTextColumn('Name', width=96, mode=dv.DATAVIEW_CELL_EDITABLE)
        _col_type_render = dv.DataViewChoiceRenderer(['integer', 'string', 'float'])
        _col_type = dv.DataViewColumn('Type', _col_type_render, 1, width=80)
        self.dvlc.AppendColumn(_col_type)
        self.dvlc.AppendTextColumn('Min', width=96, mode=dv.DATAVIEW_CELL_EDITABLE)
        self.dvlc.AppendTextColumn('Max', width=96, mode=dv.DATAVIEW_CELL_EDITABLE)
        self.dvlc.AppendTextColumn('Default', width=96, mode=dv.DATAVIEW_CELL_EDITABLE)
        # self.dvlc.Bind(dv.EVT_DATAVIEW_ITEM_CONTEXT_MENU, self.on_dvlc_cm)
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
        _row = self.dvlc.GetSelectedRow()
        # self.dvlc.EditItem(_item, self.dvlc.GetColumn(evt.GetColumn()))
        print('cm on dvlc', evt.GetColumn(), _item, _row)
        evt.Skip()

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
            self.dvlc.AppendItem((v.name, v.dataType, str(v.minVal), str(v.maxVal), str(v.defaultVal)))


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
                _icon = _incoming_icon if evt.type == EnumMBTEventType.INCOMING else _outgoing_icon
                self.dvlc.AppendItem((_icon, name))
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

    def on_dv_item_activated(self, evt: dv.DataViewEvent):
        _selected_row = self.dvlc.GetSelectedRow()
        _selected_evt_name = self.dvlc.GetTextValue(_selected_row, 1)
        self.detailPanel.set_data(self.eventMgr.get_event(_selected_evt_name))
