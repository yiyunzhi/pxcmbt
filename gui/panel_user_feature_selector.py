import wx
import wx.dataview as dv
import wx.propgrid as wxpg
from .widgets import AutocompleteComboBox


class FeatureDetailPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.pgMgr = wxpg.PropertyGridManager(self, wx.ID_ANY,
                                              style=wxpg.PG_SPLITTER_AUTO_CENTER | wxpg.PG_BOLD_MODIFIED)
        self.pgCat = wxpg.PropertyCategory('LibInfo', 'LibInfo')
        self.pgMgr.Append(self.pgCat)
        self.pgVersion = wxpg.StringProperty("Version", 'version', value='')
        self.pgDate = wxpg.StringProperty("Date", 'date', value='')
        self.pgAuthor = wxpg.StringProperty("Author", 'author', value='')
        self.pgTyp = wxpg.StringProperty("Type", 'type', value='')
        self.pgDesc = wxpg.LongStringProperty("Description", 'description', value='')
        self.pgMgr.SetPropertyReadOnly(self.pgVersion)
        self.pgMgr.SetPropertyReadOnly(self.pgDate)
        self.pgMgr.SetPropertyReadOnly(self.pgAuthor)
        self.pgMgr.SetPropertyReadOnly(self.pgTyp)
        self.pgMgr.SetPropertyReadOnly(self.pgDesc)
        self.pgMgr.Append(self.pgVersion)
        self.pgMgr.Append(self.pgDate)
        self.pgMgr.Append(self.pgAuthor)
        self.pgMgr.Append(self.pgTyp)
        self.pgMgr.Append(self.pgDesc)
        self.mainSizer.Add(self.pgMgr, 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)
        self.Layout()
        self.Fit()

    def set_data(self, name, data):
        self.pgCat.SetValue(name)
        self.pgVersion.SetValue(data.version)
        self.pgDate.SetValue(data.date)
        self.pgAuthor.SetValue(data.author)
        self.pgTyp.SetValue(data.type)
        self.pgDesc.SetValue(data.description)


class FeatureSelectorPanel(wx.Panel):
    def __init__(self, project, parent, group='USER'):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.uuid = None
        self.role = 'EnumPaneRole.PANE_EVENT'
        self.currentFeature = None
        self.project = project
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.featureLstSizer = wx.BoxSizer(wx.VERTICAL)
        self.featureDetailSizer = wx.BoxSizer(wx.VERTICAL)
        self.featureLstToolsSizer = wx.BoxSizer(wx.HORIZONTAL)
        # image show stc
        self.image = wx.Image(1, 1)
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(self.image))
        # evt list tools
        self.ctrlSearch = wx.SearchCtrl(self, size=(160, -1), style=wx.TE_PROCESS_ENTER)
        self.ctrlSearch.ShowCancelButton(True)
        # self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch, self.search)
        # self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel, self.search)
        # self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch, self.search)
        # create detail panel
        self.detailPanel = FeatureDetailPanel(self)
        # Create a dataview control
        self.dvlc = dv.DataViewListCtrl(self, style=wx.LC_REPORT | dv.DV_NO_HEADER | dv.DV_ROW_LINES)
        self.dvlc.SetRowHeight(16)
        self.dvlc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.dvlc.AppendTextColumn('Name', width=140)
        self.dvlc.SetMaxSize((160, -1))
        if group == 'ROOT':
            self._builtIn = self.project.builtInRootFeaturesMap
        else:
            self._builtIn = self.project.builtInUserFeaturesMap
        for name, evt in self._builtIn.items():
            self.dvlc.AppendItem((name,))

        self.dvlc.Bind(dv.EVT_DATAVIEW_ITEM_ACTIVATED, self.on_dv_item_activated)
        # layout
        self.featureLstToolsSizer.Add(self.ctrlSearch, 0)
        self.featureLstSizer.Add(self.featureLstToolsSizer, 0)
        self.featureLstSizer.AddSpacer(10)
        self.featureLstSizer.Add(self.dvlc, 1, wx.EXPAND)
        self.mainSizer.AddSpacer(5)
        self.featureDetailSizer.Add(self.detailPanel, 1, wx.EXPAND)
        self.featureDetailSizer.Add(self.imageCtrl, 1, wx.EXPAND)
        self.mainSizer.Add(self.featureLstSizer, 0, wx.EXPAND)
        self.mainSizer.Add(self.featureDetailSizer, 1, wx.EXPAND)
        self.SetSizer(self.mainSizer)
        self.Layout()
        self.Fit()

    def on_dv_item_activated(self, evt: dv.DataViewEvent):
        _selected_row = self.dvlc.GetSelectedRow()
        _selected_fe_name = self.dvlc.GetTextValue(_selected_row, 0)
        self.currentFeature = _selected_fe_name
        _feature=self._builtIn[_selected_fe_name]
        _data = _feature.get_inf_file_content()
        self.detailPanel.set_data(_selected_fe_name, _data.header)
        _img = wx.Image(_feature.overviewImage, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        _w = _img.GetWidth()
        _h = _img.GetHeight()
        self.imageCtrl.SetBitmap(wx.Bitmap(_img))
        self.Refresh()
