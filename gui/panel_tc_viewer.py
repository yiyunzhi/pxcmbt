import wx
import wx.dataview as dv
from pubsub import pub
from application.define import EnumAppSignals, EnumTCStatus
from .panel_header import HeaderPanel
from .util_icon_repo import UtilIconRepo


class TCDetailTooltipFormatter:
    def __init__(self):
        pass


class TestPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self._status_choice = {'INITED': 0, 'EXECUTING': 1, 'PASSED': 2, 'FAILED': 3, 'ERROR': 4, 'UNKNOWN': 255}
        self.choiceStatus = wx.Choice(self, wx.ID_ANY, choices=list(self._status_choice.keys()))
        self.indexSpin = wx.SpinCtrl(self, wx.ID_ANY)
        self.btnChgStatus = wx.Button(self, wx.ID_ANY, 'CHANGE STATUS')
        self.btnChgIdx = wx.Button(self, wx.ID_ANY, 'CHANGE Index')
        # bind event
        self.btnChgIdx.Bind(wx.EVT_BUTTON, self.on_index_changed)
        self.btnChgStatus.Bind(wx.EVT_BUTTON, self.on_status_changed)
        # layout
        self.mainSizer.Add(self.choiceStatus, 0)
        self.mainSizer.Add(self.btnChgStatus, 0)
        self.mainSizer.Add(self.indexSpin, 0)
        self.mainSizer.Add(self.btnChgIdx, 0)
        self.SetSizer(self.mainSizer)
        self.Layout()
        self.Fit()

    def on_index_changed(self, evt):
        pub.sendMessage(EnumAppSignals.sigV2VCurrentTCChanged.value, index=self.indexSpin.GetValue())

    def on_status_changed(self, evt):
        _status = list(self._status_choice.values())[self.choiceStatus.GetSelection()]
        pub.sendMessage(EnumAppSignals.sigV2VCurrentTCStatusChanged.value, status=_status)


class TCViewerPanel(wx.Panel):
    def __init__(self, parent, tcs_runner):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.uuid = None
        self.role = 'EnumPaneRole.PANE_TCV'
        self._iconRepo = UtilIconRepo()
        self._tcsRunner = tcs_runner
        self._currentTcsIdx = 0
        #self._testPanel = TestPanel(self)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.tlSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.statisticTextTemplate = 'PASSED:%s, FAILED:%s, ERROR:%s'
        # create a progressbar
        self.gauge = wx.Gauge(self, wx.ID_ANY, range=100, size=wx.DefaultSize, style=wx.GA_HORIZONTAL)
        self.gauge.SetToolTip('%s%%' % (0.0 * 100))
        self.percentText = wx.StaticText(self, wx.ID_ANY)
        self.percentText.SetLabelText('0.0%')
        self.statisticText = wx.StaticText(self, wx.ID_ANY)
        self.statisticText.SetLabelText(self.statisticTextTemplate % (0, 0, 0))
        self.exportOpt = wx.Choice(self, wx.ID_ANY, size=(-1, 23), choices=['ALL', 'PASSED', 'FAILED', 'ERROR'])
        self.exportOpt.SetSelection(0)
        self.exportBtn = wx.Button(self, wx.ID_ANY, 'EXPORT')
        # Create a dataview control
        self.dvlc = dv.DataViewListCtrl(self, style=wx.LC_REPORT | dv.DV_ROW_LINES)
        self.dvlc.SetRowHeight(16)
        self.dvlc.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.dvlc.AppendTextColumn('CaseContext', 0, width=640)
        self.dvlc.AppendBitmapColumn('Status', 1, width=18)
        self.dvlcMainWin = self.dvlc.FindWindow('wxdataviewctrlmainwindow')
        for step in self._tcsRunner.cases:
            _icon = self._get_status_icon(EnumTCStatus.INITED)
            self.dvlc.AppendItem((str(step), _icon), EnumTCStatus.INITED)
        if self.dvlc.GetItemCount() > 0:
            self.dvlc.SelectRow(0)
        # bind event
        # self.dvlcMainWin.Bind(wx.EVT_MOTION, self._on_mouse_motion)
        pub.subscribe(self.on_ext_sig_current_tc_changed, EnumAppSignals.sigV2VCurrentTCChanged.value)
        pub.subscribe(self.on_ext_sig_current_tc_status_changed, EnumAppSignals.sigV2VCurrentTCStatusChanged.value)
        self.tlSizer.Add(self.gauge, 0)
        self.tlSizer.Add(self.percentText, 0, wx.LEFT, 5)
        self.tlSizer.Add(self.statisticText, 0, wx.LEFT, 20)
        self.tlSizer.AddStretchSpacer(1)
        self.tlSizer.Add(self.exportOpt, 0, wx.TOP, 1)
        self.tlSizer.Add(self.exportBtn, 0)
        # self.mainSizer.Add(HeaderPanel('Overview of Testcases', 'Overview of Testcases', parent=self), 0,
        #                    wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.dvlc, 1, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.tlSizer, 0, wx.EXPAND | wx.ALL, 5)
        #self.mainSizer.Add(self._testPanel)
        self.SetSizer(self.mainSizer)
        self.Layout()
        self.Fit()

    def _get_status_icon(self, status):
        _img_lst = self._iconRepo.get_image_list()
        if status == EnumTCStatus.INITED:
            return _img_lst.GetBitmap(self._iconRepo.pinIcon)
        elif status == EnumTCStatus.EXECUTING:
            return _img_lst.GetBitmap(self._iconRepo.sandglassIcon)
        elif status == EnumTCStatus.PASSED:
            return _img_lst.GetBitmap(self._iconRepo.successIcon)
        elif status == EnumTCStatus.FAILED:
            return _img_lst.GetBitmap(self._iconRepo.warningIcon)
        elif status == EnumTCStatus.ERROR:
            return _img_lst.GetBitmap(self._iconRepo.errorIcon)
        elif status == EnumTCStatus.UNKNOWN:
            return _img_lst.GetBitmap(self._iconRepo.invalidIcon)
        else:
            return wx.ArtProvider.GetBitmap(wx.ART_CDROM, wx.ART_TOOLBAR, (14, 14))

    def _get_statistic_status(self):
        _passed = 0
        _failed = 0
        _error = 0
        for i in range(self.dvlc.GetItemCount()):
            _item = self.dvlc.RowToItem(i)
            if _item is not None:
                _status = self.dvlc.GetItemData(_item)
                if _status == EnumTCStatus.PASSED:
                    _passed += 1
                elif _status == EnumTCStatus.FAILED:
                    _failed += 1
                elif _status == EnumTCStatus.ERROR:
                    _error += 1
        return _passed, _failed, _error

    def _update_statistic_text(self):
        self.statisticText.SetLabelText(self.statisticTextTemplate % self._get_statistic_status())

    def set_percent(self, val):
        _pos = val * 100
        _text = '%s%%' % _pos
        self.gauge.SetValue(_pos)
        self.gauge.SetToolTip(_text)
        self.percentText.SetLabelText(_text)

    def on_ext_sig_current_tc_changed(self, index):
        self._currentTcsIdx = index
        _cnt = self.dvlc.GetItemCount()
        _percent = round((index + 1) / _cnt, 2) if _cnt != 0 else 0
        self.dvlc.SelectRow(index)
        self.set_percent(_percent)
        self._update_statistic_text()

    def on_ext_sig_current_tc_status_changed(self, status):
        if self._currentTcsIdx < self.dvlc.GetItemCount():
            self.dvlc.SelectRow(self._currentTcsIdx)
            _item = self.dvlc.GetCurrentItem()
            if _item:
                self.dvlc.SetValue(self._get_status_icon(status), self._currentTcsIdx, 1)
                self.dvlc.SetItemData(_item, status)
        self._update_statistic_text()
