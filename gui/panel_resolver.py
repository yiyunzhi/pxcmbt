import wx
import wx.grid as gridlib
from application.define import *
from .panel_canvas_dot_graph import CompoundCanvasDotGraphViewPanel
from .panel_header import HeaderPanel


class TransMatrixGrid(gridlib.Grid):
    def __init__(self, parent, col_labels: list, row_labels: list, transitions: list = None):
        gridlib.Grid.__init__(self, parent, -1)
        self.CreateGrid(len(row_labels), len(col_labels))
        self.editorChoices = ['observed', 'ignored']
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
        self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_BOTTOM)
        self.SetRowLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_BOTTOM)
        self.SetRowLabelSize(gridlib.GRID_AUTOSIZE)
        self.AutoSize()


class FeatureResolverPanel(wx.Panel):
    def __init__(self, parent, a_stc_file_io, b_stc_file_io):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.uuid = None
        self.role = EnumPanelRole.USER_FEATURE_RESOLVER
        self.aSTCFileIO = a_stc_file_io
        self.bSTCFileIO = b_stc_file_io
        self.aName = 'A'
        self.bName = 'B'
        self.compoundCanvasDotGraphView = CompoundCanvasDotGraphViewPanel(self, self.uuid)
        self.matrixTab = self.init_matrix_table(None)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        # layout
        # todo: next version->use sash windows
        # self._btnSizer = wx.StdDialogButtonSizer()
        # _btn_ok = wx.Button(self, wx.ID_OK)
        # _btn_ok.SetHelpText("The OK button completes the dialog")
        # _btn_ok.SetDefault()
        # self._btnSizer.AddButton(_btn_ok)
        #
        # _btn_cancel = wx.Button(self, wx.ID_CANCEL)
        # _btn_cancel.SetHelpText("The Cancel button cancels the dialog. (Cool, huh?)")
        # _btn_update = wx.Button(self, wx.ID_ANY)
        # self._btnSizer.AddButton(_btn_cancel)
        # self._btnSizer.AddButton(_btn_update)
        # self._btnSizer.Realize()
        # # bind event
        # _btn_ok.Bind(wx.EVT_BUTTON, self.on_ok_clicked)
        # _btn_update.Bind(wx.EVT_BUTTON, self.on_update_clicked)
        # layout
        self.mainSizer.Add(HeaderPanel('TransitionMatrix', 'TransitionMatrix', parent=self), 0,
                           wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.matrixTab, 1, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.compoundCanvasDotGraphView, 1, wx.EXPAND | wx.ALL, 5)
        # self.mainSizer.Add(self._btnSizer, 0, wx.ALL, 5)
        self.SetSizerAndFit(self.mainSizer)

    def serialize(self):
        _d = dict()
        return _d

    def deserialize(self, data):
        pass

    def set_graph_cluster_name(self, a_name, b_name):
        a_name = a_name if a_name is not None else 'A'
        b_name = b_name if b_name is not None else 'B'
        self.aName, self.bName = a_name, b_name
        self.matrixTab.SetCornerLabelValue('%s\%s' % (self.aName, self.bName))

    def show_graph(self):
        if self.aSTCFileIO is not None and self.bSTCFileIO is not None:
            self.compoundCanvasDotGraphView.show_graph(self.aSTCFileIO, self.bSTCFileIO, self.aName, self.bName)

    def init_matrix_table(self, transitions=None):
        _col_labels, _row_labels = list(), list()
        if self.aSTCFileIO is not None and self.bSTCFileIO is not None:
            # first add column, root feature
            for x in self.bSTCFileIO.body.get_transitions_list():
                _col_labels.append(x)
            # then append rows
            for x in self.aSTCFileIO.body.get_transitions_list():
                _row_labels.append(x)
        _tab = TransMatrixGrid(self, _col_labels, _row_labels, transitions)
        return _tab

    def update(self):
        pass

    def on_ok_clicked(self, evt):
        evt.Skip()

    def on_update_clicked(self, evt):
        self.update()
