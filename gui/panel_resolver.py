import wx
import wx.grid as gridlib
from pubsub import pub
from application.define import *
from application.class_observable import MBTOBOManager
from .panel_resolver_obo_editor import ResolverOBOEditPanel
from .panel_header import HeaderPanel
from .dialog_canvas_dotgraph_viewer import CanvasDotGraphViewerDialog


class TransMatrixGrid(gridlib.Grid):
    IGNORED_BG_COLOR = '#aaa'
    IGNORED_FONT_COLOR = '#ffffff'
    OBSERVABLE_BG_COLOR = '#99CCFF'
    OBSERVABLE_DATA_BG_COLOR = '#80FF00'
    OBSERVABLE_FONT_COLOR = '#333'

    def __init__(self, parent, col_labels: list, row_labels: list, transitions: list = None):
        gridlib.Grid.__init__(self, parent, -1)
        self.CreateGrid(len(row_labels), len(col_labels))
        self.editorChoices = ['ignored', 'observable']
        _editor = gridlib.GridCellChoiceEditor(self.editorChoices)
        self.SetDefaultEditor(_editor)
        for idx, x in enumerate(col_labels):
            self.SetColLabelValue(idx, x)
        for idx, x in enumerate(row_labels):
            self.SetRowLabelValue(idx, x)
        if transitions is not None:
            pass
        else:
            for x in range(len(row_labels)):
                for y in range(len(col_labels)):
                    self.SetCellValue(x, y, self.editorChoices[0])
                    self.set_cell_ignored_style(x, y)
        self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_BOTTOM)
        self.SetRowLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_BOTTOM)
        self.SetRowLabelSize(gridlib.GRID_AUTOSIZE)
        self.AutoSize()

    def set_cell_ignored_style(self, row, col):
        self.SetCellBackgroundColour(row, col, self.IGNORED_BG_COLOR)
        self.SetCellTextColour(row, col, self.IGNORED_FONT_COLOR)
        self.Refresh()

    def set_cell_observable_style(self, row, col):
        self.SetCellBackgroundColour(row, col, self.OBSERVABLE_BG_COLOR)
        self.SetCellTextColour(row, col, self.OBSERVABLE_FONT_COLOR)
        self.Refresh()

    def set_cell_observable_data_style(self, row, col):
        self.SetCellBackgroundColour(row, col, self.OBSERVABLE_DATA_BG_COLOR)
        self.SetCellTextColour(row, col, self.OBSERVABLE_FONT_COLOR)
        self.Refresh()

    def reset_cell_style(self, row, col):
        _bg_color = self.GetDefaultCellBackgroundColour()
        _font_color = self.GetDefaultCellTextColour()
        self.SetCellBackgroundColour(row, col, _bg_color)
        self.SetCellTextColour(row, col, _font_color)
        self.Refresh()


class FeatureResolverTLPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetBackgroundColour('#ddd')
        self.btnStcPreview = wx.Button(self, wx.ID_ANY, 'StateChartPreview')
        self.mainSizer.Add(self.btnStcPreview, 0, wx.EXPAND | wx.ALL, 15)
        # self.mainSizer.Add(self.btnStcPreview, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizerAndFit(self.mainSizer)


class FeatureResolverBLPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetBackgroundColour('#ddd')
        self.btnApply = wx.Button(self, wx.ID_ANY, 'Apply')
        self.mainSizer.AddStretchSpacer(1)
        self.mainSizer.Add(self.btnApply, 0, wx.EXPAND | wx.ALL, 15)
        # self.mainSizer.Add(self.btnStcPreview, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizerAndFit(self.mainSizer)


class ResolverModel:
    def __init__(self):
        self._items = dict()

    def format_query_string(self, a, b):
        return '%s_%s' % (a, b)

    def register_pair_obo_mgr(self, a, b, obo_mgr=None):
        _fmt_str = self.format_query_string(a, b)
        if obo_mgr is None:
            obo_mgr = MBTOBOManager()
        self._items.update({_fmt_str: obo_mgr})
        return obo_mgr

    def unregister_pair_obo_mgr(self, a, b):
        _fmt_str = self.format_query_string(a, b)
        if _fmt_str in self._items:
            self._items.pop(_fmt_str)

    def get_pair_obo_mgr(self, a, b):
        _fmt_str = self.format_query_string(a, b)
        return self._items.get(_fmt_str)

    def get_all_pairs(self):
        return self._items


class FeatureResolverPanel(wx.Panel):
    def __init__(self, obo_data, parent, a_stc_file_io, b_stc_file_io):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.uuid = None
        self.role = EnumPanelRole.USER_FEATURE_RESOLVER
        self.aSTCFileIO = a_stc_file_io
        self.bSTCFileIO = b_stc_file_io
        self.aName = 'A'
        self.bName = 'B'
        self.oboMgr = MBTOBOManager()
        self.oboMgr.register_obos(obo_data)
        self.resolverModel = ResolverModel()
        self.rowUids = list()
        self.colUids = list()
        self.processedPair = None
        self.changeFlag = False
        self.oboEditorPanel = ResolverOBOEditPanel(self.oboMgr, self)
        self._canvasOVDlg = CanvasDotGraphViewerDialog(self.uuid, self)
        self._canvasOVDlg.headerPanel.set_title('StateChart Overview')
        self.matrixTab = self.init_matrix_table(None)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.tlPanel = FeatureResolverTLPanel(self)
        self.blPanel = FeatureResolverBLPanel(self)
        # bind event
        self.matrixTab.Bind(gridlib.EVT_GRID_CELL_CHANGED, self.on_cell_changed)
        self.matrixTab.Bind(gridlib.EVT_GRID_SELECT_CELL, self.on_cell_selected)
        self.tlPanel.btnStcPreview.Bind(wx.EVT_BUTTON, self.on_stc_preview_clicked)
        self.blPanel.btnApply.Bind(wx.EVT_BUTTON, self.on_bl_apply_clicked)
        # layout
        self.mainSizer.Add(HeaderPanel('Resolver', 'Resolver with TransitionMatrix', parent=self), 0,
                           wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.tlPanel, 0, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.matrixTab, 1, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.oboEditorPanel, 1, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.blPanel, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizerAndFit(self.mainSizer)

    def set_uuid(self, uuid):
        self._canvasOVDlg.viewerPanel.name = uuid
        self.uuid = uuid

    def serialize(self):
        _pairs = self.resolverModel.get_all_pairs()
        _d = dict()
        for k, v in _pairs.items():
            _d.update({k: v.get_all_obos()})
        return _d

    def deserialize(self, data):
        # first compare the given data and current model
        # the data read from disk, check if any new transition or modeled transition not in data found.
        if data:
            _restored_row_cols = list()
            for k, v in data.rsv.items():
                _row_trans_uid, _col_trans_uid = k.split('_')
                # early saved trans relation not exist
                if self._stc_has_wire(_row_trans_uid, 'a') and self._stc_has_wire(_col_trans_uid, 'b'):
                    _obo_mgr = MBTOBOManager()
                    _obos = list(v.values())
                    _obo_mgr.register_obos(_obos)
                    self.resolverModel.register_pair_obo_mgr(_row_trans_uid, _col_trans_uid, _obo_mgr)
                    _restored_row_cols.append(
                        (self.rowUids.index(_row_trans_uid), self.colUids.index(_col_trans_uid), len(_obos) > 0))
            for row, col, has_data in _restored_row_cols:
                self.matrixTab.SetCellValue(row, col, self.matrixTab.editorChoices[1])
                if has_data:
                    self.matrixTab.set_cell_observable_data_style(row, col)
                else:
                    self.matrixTab.set_cell_observable_style(row, col)

        # second if has diff, show the Dialog to commit the changes
        # depends on the use selection determine if the data updated or not.

    def _stc_has_wire(self, wire_uid, a_or_b='a'):
        _wires = self.aSTCFileIO.body.wires if a_or_b == 'a' else self.bSTCFileIO.body.wires
        _wire_uids = [x['uuid'] for x in _wires]
        return wire_uid in _wire_uids

    def on_close(self, save=False):
        if save:
            self.changeFlag = False

    def on_bl_apply_clicked(self, evt):
        if self.processedPair is not None:
            _selected_obos = self.oboEditorPanel.oboSelectorPanel.get_selected_obos()
            _associated_obo_mgr = self.resolverModel.get_pair_obo_mgr(*self.processedPair)
            _row = self.rowUids.index(self.processedPair[0])
            _col = self.colUids.index(self.processedPair[1])
            if _selected_obos:
                self.matrixTab.set_cell_observable_data_style(_row, _col)
                for name, value in _selected_obos:
                    _obo = self.oboMgr.get_obo_by_name(name)
                    if _obo is not None:
                        _obo.set_data_from_string(value.rstrip())
                        _associated_obo_mgr.register_obo(_obo)
            else:
                self.matrixTab.set_cell_observable_style(_row, _col)
                _associated_obo_mgr.clear()

    def on_stc_preview_clicked(self, evt):
        if self._canvasOVDlg.IsShown():
            return
        if self.aSTCFileIO is not None and self.bSTCFileIO is not None:
            self._canvasOVDlg.headerPanel.set_description('State chart of %s and %s' % (self.aName, self.bName))
            self._canvasOVDlg.viewerPanel.show_graph(self.aSTCFileIO, self.bSTCFileIO, self.aName, self.bName)
            self._canvasOVDlg.SetSize(self._canvasOVDlg.viewerPanel.GetSize())
            self._canvasOVDlg.Show()

    def on_cell_selected(self, evt):
        _row = evt.GetRow()
        _col = evt.GetCol()
        _cell_val = self.matrixTab.GetCellValue(_row, _col)
        _row_uid = self.rowUids[_row]
        _col_uid = self.colUids[_col]
        self.oboEditorPanel.clear()
        if _cell_val == self.matrixTab.editorChoices[1]:
            _obo_lst = self.resolverModel.get_pair_obo_mgr(_row_uid, _col_uid)
            self.processedPair = (_row_uid, _col_uid)
            self.oboEditorPanel.Enable()
            if _obo_lst is not None:
                self.oboEditorPanel.set_data(_obo_lst)
        else:
            self.processedPair = None
            self.oboEditorPanel.Disable()
        pub.sendMessage(EnumAppSignals.sigV2VResolverCellSelectChanged.value,
                        row_trans_uid=_row_uid,
                        col_trans_uid=_col_uid,
                        row_stc_file_io=self.aSTCFileIO,
                        col_stc_file_io=self.bSTCFileIO)

    def on_cell_changed(self, evt):
        _row = evt.GetRow()
        _col = evt.GetCol()
        _row_uid = self.rowUids[_row]
        _col_uid = self.colUids[_col]
        _cell_val = self.matrixTab.GetCellValue(_row, _col)
        if _cell_val == self.matrixTab.editorChoices[0]:
            self.matrixTab.set_cell_ignored_style(_row, _col)
            self.resolverModel.unregister_pair_obo_mgr(_row_uid, _col_uid)
        elif _cell_val == self.matrixTab.editorChoices[1]:
            self.matrixTab.set_cell_observable_style(_row, _col)
            _obo_mgr = self.resolverModel.register_pair_obo_mgr(_row_uid, _col_uid)
            self.oboEditorPanel.set_data(_obo_mgr)
        else:
            self.matrixTab.reset_cell_style(_row, _col)
        self.changeFlag = True

    def set_graph_cluster_name(self, a_name, b_name):
        a_name = a_name if a_name is not None else 'A'
        b_name = b_name if b_name is not None else 'B'
        self.aName, self.bName = a_name, b_name
        self.matrixTab.SetCornerLabelValue('%s\%s' % (self.aName, self.bName))

    def init_matrix_table(self, transitions=None):
        _col_labels, _row_labels = list(), list()
        if self.aSTCFileIO is not None and self.bSTCFileIO is not None:
            # first add column, root feature
            for uid, x in self.bSTCFileIO.body.get_transition_text_list():
                _col_labels.append(x)
                self.colUids.append(uid)
            # then append rows
            for uid, x in self.aSTCFileIO.body.get_transition_text_list():
                _row_labels.append(x)
                self.rowUids.append(uid)
        _tab = TransMatrixGrid(self, _col_labels, _row_labels, transitions)
        return _tab

    def update(self):
        pass
