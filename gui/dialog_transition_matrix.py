import wx
import wx.grid as gridlib
from .panel_header import HeaderPanel
from .panel_compound_canvas_dot_graph import CompoundCanvasDotGraphViewPanel


class TransMatrixGrid(gridlib.Grid):
    def __init__(self, parent, col_labels: list, row_labels: list, states: list = None):
        gridlib.Grid.__init__(self, parent, -1)
        self.CreateGrid(len(row_labels), len(col_labels))
        self.editorChoices = ['observed', 'ignored']
        _editor = gridlib.GridCellChoiceEditor(self.editorChoices)
        self.SetDefaultEditor(_editor)
        for idx, x in enumerate(col_labels):
            self.SetColLabelValue(idx, x)
        for idx, x in enumerate(row_labels):
            self.SetRowLabelValue(idx, x)
        if states is not None:
            pass
        else:
            for x in range(len(row_labels)):
                for y in range(len(col_labels)):
                    self.SetCellValue(x, y, self.editorChoices[0])
        self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_BOTTOM)
        self.SetRowLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_BOTTOM)
        self.SetRowLabelSize(gridlib.GRID_AUTOSIZE)
        self.AutoSize()


class TransitionMatrixDialog(wx.Dialog):
    def __init__(self, parent, a_stc_file_io, b_stc_file_io, wx_id=wx.ID_ANY, title='TransitionMatrix',
                 size=wx.DefaultSize,
                 pos=wx.DefaultPosition,
                 style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name='TransitionMatrixDialog'):
        wx.Dialog.__init__(self, parent, wx_id, title, pos, size, style, name)
        self.aSTCFileIO = a_stc_file_io
        self.bSTCFileIO = b_stc_file_io
        self.aName = 'A'
        self.bName = 'B'
        self.compoundCanvasDotGraphView = CompoundCanvasDotGraphViewPanel(self)
        self.matrixTab = self.init_matrix_table(None)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        # layout
        self._btnSizer = wx.StdDialogButtonSizer()
        _btn_ok = wx.Button(self, wx.ID_OK)
        _btn_ok.SetHelpText("The OK button completes the dialog")
        _btn_ok.SetDefault()
        self._btnSizer.AddButton(_btn_ok)

        _btn_cancel = wx.Button(self, wx.ID_CANCEL)
        _btn_cancel.SetHelpText("The Cancel button cancels the dialog. (Cool, huh?)")
        self._btnSizer.AddButton(_btn_cancel)
        self._btnSizer.Realize()
        # bind event
        _btn_ok.Bind(wx.EVT_BUTTON, self.on_ok_clicked)
        self.Bind(wx.EVT_SHOW, self.on_this_show)
        # layout
        self.mainSizer.Add(HeaderPanel('TransitionMatrix', 'TransitionMatrix', parent=self), 0,
                           wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.matrixTab, 1, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self.compoundCanvasDotGraphView, 1, wx.EXPAND | wx.ALL, 5)
        self.mainSizer.Add(self._btnSizer, 0, wx.ALL, 5)
        self.SetSizerAndFit(self.mainSizer)

    def set_graph_cluster_name(self, a_name, b_name):
        a_name = a_name if a_name is not None else 'A'
        b_name = b_name if b_name is not None else 'B'
        self.aName, self.bName = a_name, b_name
        self.matrixTab.SetCornerLabelValue('%s\%s' % (self.aName, self.bName))

    def init_matrix_table(self, states=None):
        if self.aSTCFileIO is not None and self.bSTCFileIO is not None:
            _col_labels, _row_labels = list(), list()
            # first add column, root feature
            for x in self.bSTCFileIO.body.get_transitions_list():
                _col_labels.append(x)
            # then append rows
            for x in self.aSTCFileIO.body.get_transitions_list():
                _row_labels.append(x)
            _tab = TransMatrixGrid(self, _col_labels, _row_labels, states)
            return _tab
        return None

    def on_this_show(self, evt):
        self.compoundCanvasDotGraphView.show_graph(self.aSTCFileIO, self.bSTCFileIO, self.aName, self.bName)

    def on_name_entered(self, evt):
        # self.ufNameExistMsgLabel.SetLabel('')
        evt.Skip()

    def on_ok_clicked(self, evt):
        # _name = self.ufNameTextEdit.GetValue()
        # if not _name or not _name.strip():
        #     self.ufNameExistMsgLabel.SetLabel('name can not empty')
        #     return
        # if self.refFuncNameChecker(self.ufNameTextEdit.GetValue()):
        #     self.ufNameExistMsgLabel.SetLabel('name %s is already exist' % _name)
        #     return
        evt.Skip()
