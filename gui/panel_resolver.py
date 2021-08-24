import wx
import wx.grid as gridlib
import wx.propgrid as wxpg
from application.define import *
from application.class_observable import MBTOBOManager
from .panel_resolver_obo_editor import ResolverOBOEditPanel
from .panel_header import HeaderPanel
from .dialog_canvas_dotgraph_viewer import CanvasDotGraphViewerDialog


class TransMatrixGrid(gridlib.Grid):
    IGNORED_BG_COLOR = '#aaa'
    IGNORED_FONT_COLOR = '#ffffff'
    OBSERVABLE_BG_COLOR = '#99CCFF'
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

    def set_cell_observable_style(self, row, col):
        self.SetCellBackgroundColour(row, col, self.OBSERVABLE_BG_COLOR)
        self.SetCellTextColour(row, col, self.OBSERVABLE_FONT_COLOR)

    def reset_cell_style(self, row, col):
        _bg_color = self.GetDefaultCellBackgroundColour()
        _font_color = self.GetDefaultCellTextColour()
        self.SetCellBackgroundColour(row, col, _bg_color)
        self.SetCellTextColour(row, col, _font_color)


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


class ResolverOBOPropPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        _pg_main = wxpg.PropertyGridManager(self, wx.ID_ANY,
                                            style=wxpg.PG_SPLITTER_AUTO_CENTER | wxpg.PG_BOLD_MODIFIED)
        _pg_uuid = wxpg.StringProperty("uuid", 'uuid', value=self.uuid)
        _pg_main.SetPropertyReadOnly(_pg_uuid)
        _pg_main.Append(_pg_uuid)

        _pg_role = wxpg.StringProperty("role", 'role', value=EnumItemRole(self.role).name)
        _pg_main.SetPropertyReadOnly(_pg_role)
        _pg_main.Append(_pg_role)

        _pg_position = wxpg.StringProperty("position", 'position',
                                           value='(%s,%s)' % (self.position[0], self.position[1]))
        _pg_main.SetPropertyReadOnly(_pg_position)
        _pg_main.Append(_pg_position)

        _pg_name = wxpg.StringProperty("name", 'name',
                                       value=self.nameText)
        _pg_main.SetPropertyReadOnly(_pg_name)
        _pg_main.Append(_pg_name)

        # self.mainSizer.Add(self.btnStcPreview, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizerAndFit(self.mainSizer)

    def set_obo(self, obo):
        pass


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
        self.matrixTab.Bind(wx.EVT_KILL_FOCUS, self.on_matrixtab_kill_focus)
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
        _d = dict()
        return _d

    def deserialize(self, data):
        pass

    def on_bl_apply_clicked(self, evt):
        # todo: first get the associated obo mgr, then update the obomgr
        pass

    def on_stc_preview_clicked(self, evt):
        if self._canvasOVDlg.IsShown():
            return
        if self.aSTCFileIO is not None and self.bSTCFileIO is not None:
            self._canvasOVDlg.headerPanel.set_description('State chart of %s and %s' % (self.aName, self.bName))
            self._canvasOVDlg.viewerPanel.show_graph(self.aSTCFileIO, self.bSTCFileIO, self.aName, self.bName)
            self._canvasOVDlg.SetSize(self._canvasOVDlg.viewerPanel.GetSize())
            self._canvasOVDlg.Show()

    def on_matrixtab_kill_focus(self, evt):
        pass
        # self.oboEditorPanel.oboSelectorPanel.Disable()
        # self.oboEditorPanel.clear()

    def on_cell_selected(self, evt):
        _row = evt.GetRow()
        _col = evt.GetCol()
        _cell_val = self.matrixTab.GetCellValue(_row, _col)
        if _cell_val == self.matrixTab.editorChoices[1]:
            _row_uid = self.rowUids[_row]
            _col_uid = self.colUids[_col]
            _obo_lst = self.resolverModel.get_pair_obo_mgr(_row_uid, _col_uid)
            if _obo_lst is not None:
                self.oboEditorPanel.set_data(_obo_lst)
            else:
                self.oboEditorPanel.clear()

    def on_cell_changed(self, evt):
        # self.oboEditorPanel.oboSelectorPanel.Enable()
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
        # print('...---> cell changed', evt.GetCol(), evt.GetRow())

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

    def on_ok_clicked(self, evt):
        evt.Skip()

    def on_update_clicked(self, evt):
        self.update()
