# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       :
# Sourcefile(s) : app_frame.py
# ------------------------------------------------------------------------------
#
# File          : app_frame.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import traceback

import wx
import wx.lib.agw.aui as aui
from wx.lib.agw import pybusyinfo as PBI
from pubsub import pub
from application.log_logger import get_logger
from application.define import EnumAppSignals, EnumPanelRole, EnumItemRole
from application.class_app_setting import APP_SETTING
from application.class_project import Project
from .assets_images import *
from .util_icon_repo import UtilIconRepo
from .panel_canvas import StateChartCanvasViewPanel
from .panel_project_mgr import GuiProjectManagerPanel, GuiProjectManagerContainerPanel
from .panel_props_container import PropContainerPanel
from .panel_console import ConsolePanel
from .panel_event_editor import EventEditorPanel
from .panel_prop_content import CanvasNodePropContentPanel, ResolverCellPropsContentPanel
from .panel_resolver import FeatureResolverPanel
from .panel_obo_editor import OBOEditorPanel
from .define_gui import _, EnumCanvasToolbarMode
from .dialog_node_editor import NodeEditorDialog, NodeNoteEditorDialog
from .dialog_transition_editor import TransitionEditorDialog
from .dialog_new_project import NewProjectDialog
from .dialog_select_feature import SelectFeatureDialog
from .dialog_user_featrue import PromptUserFeatureNameDialog, PromptUserFeatureAsLibDialog
from .dialog_tc import TCDialog
from application.utils_helper import *
from application.class_yaml_tag import *
from application.class_feature import Feature
from application.class_test_runner import MBTRunner


# fixme: default project close occure a error. No such file or directory: 'C:\\Users\\LiuZhang\\PycharmProjects\\pxcmbt\\projects\\default\\ui.pepc'


class WxLog:
    def WriteText(self, text):
        if text[-1:] == '\n':
            text = text[:-1]
        wx.LogMessage(text)

    write = WriteText


_default_wx_log = WxLog()
_log = get_logger('app')


class FrameMain(wx.Frame):
    PANE_PROPS_CONTAINER_NAME = 'PropertiesContainerPanel'
    DUMMY_PROJECT_NAME = '*#55rtzdefault'

    def __init__(self, parent, wx_id=wx.ID_ANY, title='', pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE | wx.SUNKEN_BORDER, log=_default_wx_log):
        sys.excepthook = self.except_hook
        super(FrameMain, self).__init__(parent, wx_id, title, pos, size, style)
        self._auiMgr = aui.AuiManager(agwFlags=aui.AUI_MGR_DEFAULT | aui.AUI_MGR_ALLOW_ACTIVE_PANE)
        self._icon_size = (16, 16)
        self._iconRepo = UtilIconRepo()
        self._childWinCount = 0
        # tell AuiManager to manage this frame
        self._auiMgr.SetManagedWindow(self)
        self._invisiblePanel = wx.Panel(self)
        self._invisiblePanel.Hide()
        # set frame icon
        self.SetIcon(Mondrian.GetIcon())
        # set up center pane aui info
        self._centerTargetAuiInfo = aui.AuiPaneInfo().BestSize((300, 300)). \
            DestroyOnClose(False).Center().Snappable().Dockable(). \
            MinimizeButton(True).MaximizeButton(True).Floatable(False)
        # Attributes
        # here use a dummy project
        self._currentProject = Project(self.DUMMY_PROJECT_NAME)
        self._currentPane = None
        self._panelCache = dict()
        self._toolbar = None
        self._propsPaneCaptionFmt = "%s Properties"
        self._currentPropPane = None
        self._textCount = 1
        self._transparency = 255
        self._snapped = False
        self._customPaneButtons = False
        self._customTabButtons = False
        self._paneIcons = False
        self._vetoTree = self._veto_text = False

        self.log = log

        self.CreateStatusBar()
        self.GetStatusBar().SetStatusText("Ready")
        self.create_acc_table()
        self.create_menu_bar()
        self.create_tool_bar()
        self.build_panes()
        self.bind_events()
        self.Fit()
        self.Center()
        wx.CallAfter(self.SendSizeEvent)
        self._consolePane.write_info_content('---App Initial finished---')

    def except_hook(self, etype, value, tb):
        """
        This excepthook, when bound will catch all unhadled exceptions logging
        them to file and also creating a wx MessageDialog to notify the user of
        the error.
        """
        # todo: add date time
        _message = '\nUncaught exception:\n'
        _message += ''.join(traceback.format_exception(etype, value, tb))
        _log_file = open('log\\error.log', 'a', encoding='utf-8')
        _log_file.write(_message)
        _log_file.close()

        _dlg = wx.MessageDialog(self, "{0!s}: {1!s}".format(etype.__name__, value)
                                , "Unhandled exception", wx.OK | wx.ICON_ERROR)
        _dlg.ShowModal()
        _dlg.Destroy()

    def create_acc_table(self):

        # set the acceleratorTable
        _id_ctrl_s = wx.NewId()

        self.Bind(wx.EVT_MENU, self.on_ctrl_s_pressed, id=_id_ctrl_s)

        _accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, wx.WXK_CONTROL_S, _id_ctrl_s)
        ])
        self.SetAcceleratorTable(_accel_tbl)

    def build_panes(self):
        self._panelProjectMgr = GuiProjectManagerContainerPanel(self)
        self._propContainerPane = PropContainerPanel(parent=self)
        self._auiMgr.AddPane(self._panelProjectMgr, aui.AuiPaneInfo().Name("projectMgrPanel").Caption("Project").
                             Left().Layer(1).Position(0).BestSize((240, -1)).MinSize((160, 360)).
                             CloseButton(True).MaximizeButton(True).
                             MinimizeButton(True))
        self._auiMgr.AddPane(self._propContainerPane,
                             aui.AuiPaneInfo().Name(self.PANE_PROPS_CONTAINER_NAME).Caption("Properties").
                             Left().Layer(1).Position(0).BestSize((240, 240)).
                             CloseButton(False).MaximizeButton(False).
                             MinimizeButton(True))
        self._consolePane = ConsolePanel(parent=self)
        self._auiMgr.AddPane(self._consolePane, aui.AuiPaneInfo().Name("consolePanel").Caption("Console").
                             Bottom().BestSize((-1, 150)).MinSize((-1, 120)).Floatable(False).FloatingSize((500, 160)).
                             CloseButton(False).MaximizeButton(True).
                             MinimizeButton(True))
        self._auiMgr.Update()

    def create_html_ctrl(self, parent=None):

        if not parent:
            parent = self
        text = \
            "<html><body>" \
            "<h3>Welcome to AUI</h3>" \
            "</body></html>"
        from wx import html
        ctrl = html.HtmlWindow(parent, -1, wx.DefaultPosition, wx.Size(400, 300))
        ctrl.SetPage(text)
        return ctrl

    def create_tool_bar(self):
        _img_lst = self._iconRepo.get_image_list()
        _tb_icon_size = wx.Size(16, 16)
        _tb = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                             agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        _tb.SetToolBitmapSize(_tb_icon_size)
        _new_bmp = wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR, _tb_icon_size)
        _open_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, _tb_icon_size)
        _save_bmp = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR, _tb_icon_size)
        _copy_bmp = wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_TOOLBAR, _tb_icon_size)
        _paste_bmp = wx.ArtProvider.GetBitmap(wx.ART_PASTE, wx.ART_TOOLBAR, _tb_icon_size)
        _pane_proj_new_id = wx.NewIdRef()
        _pane_proj_save_id = wx.NewIdRef()
        _pane_proj_open_id = wx.NewIdRef()
        self._pane_diag_tc_id = wx.NewIdRef()
        _tb.AddSimpleTool(_pane_proj_new_id, 'NewProject', _new_bmp, 'NewProject')
        _tb.AddSimpleTool(_pane_proj_save_id, 'Save', _save_bmp, 'Save')
        _tb.AddSimpleTool(_pane_proj_open_id, 'Open', _open_bmp, 'Open')
        _tb.AddSeparator()
        _tb.AddSimpleTool(self._pane_diag_tc_id, 'TC', _img_lst.GetBitmap(self._iconRepo.folderIcon), 'TC')
        _tb.EnableTool(self._pane_diag_tc_id, False)
        _tb.Realize()
        self.Bind(wx.EVT_TOOL, self.on_tb_pane_save, _pane_proj_save_id)
        self.Bind(wx.EVT_TOOL, self.on_menu_new_project_clicked, _pane_proj_new_id)
        self.Bind(wx.EVT_TOOL, self.on_menu_open_clicked, _pane_proj_open_id)
        self.Bind(wx.EVT_TOOL, self.on_menu_open_tc_diag, self._pane_diag_tc_id)
        self._toolbar = _tb
        self._auiMgr.AddPane(_tb, aui.AuiPaneInfo().Name("CanvasTool").Caption("General Tools").
                             ToolbarPane().Top().Layer(1).Position(0).BestSize((-1, 24)))

    def create_menu_bar(self):
        # create menu
        _mb = wx.MenuBar()
        _file_new_project_id = wx.NewIdRef()
        _file_new_file_id = wx.NewIdRef()
        _file_menu = wx.Menu()
        _file_new_sub_menu = wx.Menu()
        _new_project_id = _file_new_sub_menu.Append(_file_new_project_id, _('NewProject'))
        _new_file_id = _file_new_sub_menu.Append(_file_new_file_id, _('NewFile'))
        _file_menu.Append(wx.ID_ANY, 'New', _file_new_sub_menu)
        _file_menu.Append(wx.ID_OPEN, _('Open'))
        _file_menu.Append(wx.ID_SAVE, _('Save'))
        _file_menu.Append(wx.ID_SAVEAS, _('Save As'))
        _file_menu.AppendSeparator()
        _file_menu.Append(wx.ID_EXIT, _('Exit'))
        self.Bind(wx.EVT_MENU, self.on_menu_new_project_clicked, _new_project_id)
        self.Bind(wx.EVT_MENU, self.on_menu_new_file_clicked, _new_file_id)
        _view_menu = wx.Menu()
        # view_menu.Append(ID_CreateText, "Create Text Control")
        _view_menu.AppendSeparator()

        _tools_menu = wx.Menu()

        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, _('About...'))

        _mb.Append(_file_menu, "&File")
        _mb.Append(_view_menu, "&View")
        _mb.Append(_tools_menu, "&Tool")
        _mb.Append(help_menu, "&Help")

        self.SetMenuBar(_mb)

    def bind_events(self):
        # bind general event
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.on_erase_background)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_CLOSE, self.on_window_closed)
        self.Bind(wx.EVT_CHILD_FOCUS, self.on_child_focused)
        self.Bind(aui.EVT_AUI_PANE_ACTIVATED, self.on_aui_pane_activated)
        self.Bind(aui.EVT_AUI_PANE_CLOSE, self.on_aui_pane_close)
        # bind menu event

        self.Bind(wx.EVT_MENU, self.on_menu_save_clicked, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.on_menu_open_clicked, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.on_menu_save_as_clicked, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.on_about, id=wx.ID_ABOUT)
        # bind event update UI, multi allowed
        pub.subscribe(self.on_ext_sig_project_item_dclicked, EnumAppSignals.sigV2VModelTreeItemDoubleClicked.value)
        pub.subscribe(self.on_ext_sig_project_item_select_change, EnumAppSignals.sigV2VProjectItemSelectChanged.value)
        pub.subscribe(self.on_ext_sig_canvas_node_dclicked, EnumAppSignals.sigV2VCanvasNodeDClicked.value)
        pub.subscribe(self.on_ext_sig_canvas_node_note_dclicked, EnumAppSignals.sigV2VCanvasNodeNoteDClicked.value)
        pub.subscribe(self.on_ext_sig_canvas_transition_dclicked, EnumAppSignals.sigV2VCanvasTransitionDClicked.value)
        pub.subscribe(self.on_ext_sig_canvas_node_show_props, EnumAppSignals.sigV2VCanvasNodeShowProps.value)
        pub.subscribe(self.on_ext_sig_project_add_user_feature, EnumAppSignals.sigV2VProjectAddUserFeature.value)
        pub.subscribe(self.on_ext_sig_project_new_user_feature, EnumAppSignals.sigV2VProjectNewUserFeature.value)
        pub.subscribe(self.on_ext_sig_project_save_user_feature_as_lib,
                      EnumAppSignals.sigV2VProjectSaveUserFeatureAsLib.value)
        pub.subscribe(self.on_ext_sig_project_save_root_feature_as_lib,
                      EnumAppSignals.sigV2VProjectSaveRootFeatureAsLib.value)
        pub.subscribe(self.on_ext_sig_project_del_user_feature, EnumAppSignals.sigV2VProjectDelUserFeature.value)
        pub.subscribe(self.on_ext_sig_project_add_root_feature, EnumAppSignals.sigV2VProjectAddRootFeature.value)
        pub.subscribe(self.on_ext_sig_project_empty_root_feature, EnumAppSignals.sigV2VProjectEmptyRootFeature.value)
        pub.subscribe(self.on_ext_sig_resolver_cell_select_changed,
                      EnumAppSignals.sigV2VResolverCellSelectChanged.value)

    def _show_success_msgbox(self, msg=None):
        _ret = wx.MessageBox('Operation successful executed' if msg is None else msg, 'Success')

    def _show_failed_msgbox(self, msg=None):
        _ret = wx.MessageBox('Operation failed executed' if msg is None else msg, 'Failed')

    def on_ext_sig_resolver_cell_select_changed(self, row_trans_uid, col_trans_uid, row_stc_file_io, col_stc_file_io):
        _row_wire, _col_wire = None, None
        _row_src_node, _col_src_node = None, None
        _row_dst_node, _col_dst_node = None, None
        _res = filter(lambda x: x['uuid'] == row_trans_uid, row_stc_file_io.body.wires)
        if _res: _row_wire = list(_res)[0]
        _res = filter(lambda x: x['uuid'] == col_trans_uid, col_stc_file_io.body.wires)
        if _res: _col_wire = list(_res)[0]
        if _row_wire:
            _res = filter(lambda x: x['uuid'] == _row_wire['srcNodeUUID'], row_stc_file_io.body.nodes)
            if _res: _row_src_node = list(_res)[0]
            _res = filter(lambda x: x['uuid'] == _row_wire['dstNodeUUID'], row_stc_file_io.body.nodes)
            if _res: _row_dst_node = list(_res)[0]
        if _col_wire:
            _res = filter(lambda x: x['uuid'] == _col_wire['srcNodeUUID'], col_stc_file_io.body.nodes)
            if _res: _col_src_node = list(_res)[0]
            _res = filter(lambda x: x['uuid'] == _col_wire['dstNodeUUID'], col_stc_file_io.body.nodes)
            if _res: _col_dst_node = list(_res)[0]
        _prop_content = ResolverCellPropsContentPanel((_row_wire, _row_src_node, _row_dst_node),
                                                      (_col_wire, _col_src_node, _col_dst_node),
                                                      self._propContainerPane)
        self._propContainerPane.set_content(_prop_content)

    def on_ext_sig_project_save_root_feature_as_lib(self, state_uuid, event_uuid, obo_uuid):
        try:
            _dlg = PromptUserFeatureAsLibDialog(self._currentProject.is_root_feature_lib_exist, self)
            _ret = _dlg.ShowModal()
            if _ret == wx.ID_OK:
                _name = _dlg.ufNameTextEdit.GetValue()
                _desc = _dlg.ufDescTextEdit.GetValue()
                self._currentProject.create_root_feature_lib(_name, _desc, state_uuid, event_uuid, obo_uuid)
                self._show_success_msgbox()
        except Exception as e:
            self._show_failed_msgbox('%s' % e)

    def on_ext_sig_project_save_user_feature_as_lib(self, state_uuid, event_uuid):
        try:
            _dlg = PromptUserFeatureAsLibDialog(self._currentProject.is_user_feature_lib_exist, self)
            _ret = _dlg.ShowModal()
            if _ret == wx.ID_OK:
                _name = _dlg.ufNameTextEdit.GetValue()
                _desc = _dlg.ufDescTextEdit.GetValue()
                self._currentProject.create_feature_lib(_name, _desc, state_uuid, event_uuid)
                self._show_success_msgbox()
        except Exception as e:
            self._show_failed_msgbox('%s' % e)

    def on_ext_sig_project_del_user_feature(self, state_uuid, event_uuid, resolver_uuid):
        if state_uuid:
            self._currentProject.remove_stc_file(state_uuid)
        if event_uuid:
            self._currentProject.remove_evt_file(event_uuid)
        if resolver_uuid:
            self._currentProject.remove_rsv_file(resolver_uuid)

    def on_ext_sig_project_new_user_feature(self):
        _dlg = PromptUserFeatureNameDialog(self._panelProjectMgr.contentPanel.is_uf_name_is_exist, self)
        _ret = _dlg.ShowModal()
        if _ret == wx.ID_OK:
            _name = _dlg.ufNameTextEdit.GetValue()
            _, _state_name, _evt_name, _resolver_name = self._panelProjectMgr.contentPanel.add_user_feature(_name)
            self._currentProject.save_project(self._panelProjectMgr.contentPanel)
            self._currentProject.create_new_stc_file(_state_name)
            self._currentProject.create_new_evt_file(_evt_name)
            self._currentProject.create_new_rsv_file(_resolver_name)

    def on_ext_sig_project_add_user_feature(self):
        _dlg = SelectFeatureDialog(self._currentProject, self)
        _ret = _dlg.ShowModal()
        if _ret == wx.ID_OK:
            _selected_feature_name = _dlg.get_selected_feature()
            if _selected_feature_name:
                _, _stc_uuid, _evt_uuid, _resolver_uuid = self._panelProjectMgr.contentPanel.add_user_feature(
                    _selected_feature_name)
                self._currentProject.add_user_feature_event(_selected_feature_name, _evt_uuid)
                self._currentProject.add_user_feature_state(_selected_feature_name, _stc_uuid)
            else:
                wx.MessageBox('No Feature selected', 'Info')

    def on_ext_sig_project_add_root_feature(self):
        _ret = wx.MessageBox('Current data of root item will be deleted!', 'Info', style=wx.YES_NO)
        if _ret == wx.YES:
            _dlg = SelectFeatureDialog(self._currentProject, self, group='ROOT')
            _ret = _dlg.ShowModal()
            if _ret == wx.ID_OK:
                _selected_feature_name = _dlg.get_selected_feature()
                if _selected_feature_name:
                    _evt_uuid = self._panelProjectMgr.contentPanel.get_root_event_uuid()
                    _stc_uuid = self._panelProjectMgr.contentPanel.get_root_state_uuid()
                    self._currentProject.add_root_feature_event(_selected_feature_name, _evt_uuid)
                    self._currentProject.add_root_feature_state(_selected_feature_name, _stc_uuid)
                    if _stc_uuid in self._panelCache:
                        _pane_info = self._panelCache[_stc_uuid]
                        _pane = self._auiMgr.GetPaneByName(_stc_uuid)
                        self._auiMgr.ClosePane(_pane)
                        self._auiMgr.DetachPane(_pane_info)
                        self._panelCache.pop(_stc_uuid)
                    if _evt_uuid in self._panelCache:
                        _pane_info = self._panelCache[_evt_uuid]
                        _pane = self._auiMgr.GetPaneByName(_evt_uuid)
                        self._auiMgr.ClosePane(_pane)
                        self._auiMgr.DetachPane(_pane_info)
                        self._panelCache.pop(_evt_uuid)
                    self._auiMgr.Update()
                else:
                    wx.MessageBox('No Feature selected', 'Info')

    def on_ext_sig_project_empty_root_feature(self):
        _ret = wx.MessageBox('Current data of root item will be deleted!', 'Info', style=wx.YES_NO)
        if _ret == wx.YES:
            _evt_uuid = self._panelProjectMgr.contentPanel.get_root_event_uuid()
            _stc_uuid = self._panelProjectMgr.contentPanel.get_root_state_uuid()
            self._currentProject.empty_root_feature_event(_evt_uuid)
            self._currentProject.empty_root_feature_state(_stc_uuid)
            if _stc_uuid in self._panelCache:
                _pane_info = self._panelCache[_stc_uuid]
                _pane = self._auiMgr.GetPaneByName(_stc_uuid)
                self._auiMgr.ClosePane(_pane)
                self._auiMgr.DetachPane(_pane_info)
                self._panelCache.pop(_stc_uuid)
            if _evt_uuid in self._panelCache:
                _pane_info = self._panelCache[_evt_uuid]
                _pane = self._auiMgr.GetPaneByName(_evt_uuid)
                self._auiMgr.ClosePane(_pane)
                self._auiMgr.DetachPane(_pane_info)
                self._panelCache.pop(_evt_uuid)
            self._auiMgr.Update()

    def on_ext_sig_canvas_node_show_props(self, item):
        if hasattr(item, 'get_properties'):
            _uuid = item.uuid
            _prop_panel = self._propContainerPane.get_panel_by_uuid(_uuid)
            if _prop_panel:
                self._propContainerPane.toggle_panel_by_uuid(_uuid)
            else:
                _node_prop_inst = CanvasNodePropContentPanel(item, parent=self._propContainerPane, id=wx.ID_ANY)
                self._propContainerPane.set_content(_node_prop_inst)

    def on_ext_sig_canvas_node_note_dclicked(self, uuid, role, item):
        _dlg = NodeNoteEditorDialog(item, self)
        _ret = _dlg.ShowModal()

    def on_ext_sig_canvas_node_dclicked(self, uuid, role, item):
        _evt_uuid = self.get_associated_event_uuid(uuid)
        _evt_data = self._currentProject.get_event_data(_evt_uuid, True)
        _dlg = NodeEditorDialog(_evt_data, item, self)
        _ret = _dlg.ShowModal()

    def on_ext_sig_canvas_transition_dclicked(self, uuid, role, item):
        _evt_uuid = self.get_associated_event_uuid(uuid)
        _evt_data = self._currentProject.get_event_data(_evt_uuid, True)
        _dlg = TransitionEditorDialog(_evt_data, item, self)
        _ret = _dlg.ShowModal()

    def get_associated_event_uuid(self, uuid):
        _evt_uuid = self._panelProjectMgr.contentPanel.find_event_sibling_uuid_of(uuid)
        if _evt_uuid is None:
            raise IOError('no associated uuid found')
        return _evt_uuid

    def get_associated_state_uuid(self, uuid):
        _stc_uuid = self._panelProjectMgr.contentPanel.find_state_sibling_uuid_of(uuid)
        if _stc_uuid is None:
            raise IOError('no associated uuid found')
        return _stc_uuid

    def on_child_focused(self, evt):
        _win = evt.GetWindow()
        evt.Skip()

    def on_ctrl_s_pressed(self, evt):
        self._save_project()

    def on_menu_open_tc_diag(self, evt):
        if self._currentProject.name != self.DUMMY_PROJECT_NAME:
            _busy = PBI.PyBusyInfo('Processing...', parent=None, title="ProcessInfo")
            wx.Yield()
            _root_feature = Feature('Root',
                                    util_get_uuid_string(),
                                    self._currentProject,
                                    None,
                                    self._panelProjectMgr.contentPanel.get_root_state_uuid(),
                                    self._panelProjectMgr.contentPanel.get_root_event_uuid(),
                                    )
            _user_features = self._get_all_user_feature(_root_feature)
            _mbt_runner=MBTRunner(_user_features)
            del _busy
            _dlg = TCDialog(_mbt_runner, self)
            _ret = _dlg.ShowModal()
            _dlg.Destroy()
        else:
            wx.MessageBox('properly you need to open a project firstly', 'Info', wx.OK_DEFAULT)

    def _get_all_user_feature(self,root_feature):
        _res = list()
        _rsv_uids = self._panelProjectMgr.contentPanel.get_all_user_features()
        for name,uuid, stc_uid, evt_uid, rsv_uid in _rsv_uids:
            _res.append(Feature(name, uuid,self._currentProject,root_feature, stc_uid, evt_uid, rsv_uid))
        return _res

    def on_tb_pane_save(self, evt):
        self._save_project()

    def on_aui_pane_close(self, evt):
        _pane = evt.GetPane()
        _window = _pane.window
        if hasattr(_window, 'changeFlag'):
            if _window.changeFlag:
                _ret = wx.MessageBox('Do you wanna save it?', 'Notice', wx.YES_NO)
                _save = _ret == wx.YES
            else:
                _save = False
            _window.on_close(_save)

    def on_aui_pane_activated(self, evt):
        _pane = evt.GetPane()
        if hasattr(_pane, 'uuid'):
            # print('pane activated', _pane.uuid)
            if _pane.uuid in self._panelCache:
                self._panelProjectMgr.contentPanel.highlight_item_by_uuid(_pane.uuid)
            if _pane.role == EnumPanelRole.STATE_CHART_CANVAS:
                self._currentPane = _pane
                self._auiMgr.ShowPane(self._toolbar, True)
            # elif _pane.role == EnumPanelRole.USER_FEATURE_RESOLVER:
            #     _exist_in_proj = self._currentProject.get_file_io(_pane.uuid, _pane.role)
            #     if _exist_in_proj is not None:
            #         _pane.deserialize(_exist_in_proj.body)

    def on_window_closed(self, evt):
        if self._currentProject is not None and util_is_dir_exist(self._currentProject.path):
            _perspective = self._auiMgr.SavePerspective()
            self._currentProject.save_ui_perspective(_perspective)
        evt.Skip()

    def on_menu_save_clicked(self, evt):
        self._save_project()

    def _enable_tb_tc(self, state=True):
        self._toolbar.EnableTool(self._pane_diag_tc_id, state)
        self._toolbar.Refresh()

    def _save_project(self):
        self.GetStatusBar().SetStatusText("Project Saving...")
        if self._currentProject:
            # save all cached pane
            # fixme: next version, frame_app send the data to project only, not the instance
            for n_uuid, panel in self._panelCache.items():
                if isinstance(panel, StateChartCanvasViewPanel):
                    self._currentProject.save_canvas(panel)
                elif isinstance(panel, EventEditorPanel):
                    self._currentProject.save_event(panel)
                elif isinstance(panel, FeatureResolverPanel):
                    self._currentProject.save_resolver(panel)
                elif isinstance(panel, OBOEditorPanel):
                    self._currentProject.save_obo(panel)
            if self._panelProjectMgr.contentPanel is not None:
                self._currentProject.save_project(self._panelProjectMgr.contentPanel)
            pass
        else:
            pass
        _panes = self._auiMgr.GetAllPanes()
        for pane in _panes:
            if hasattr(pane, 'changeFlag'):
                pane.changeFlag = False
        self.GetStatusBar().SetStatusText("Project Saved")

    def on_menu_save_as_clicked(self, evt):
        if self._currentProject:
            pass
        else:
            pass

    def on_menu_open_clicked(self, evt):
        if self._currentProject:
            # fixme: first check if current project saved
            pass
        else:
            pass
        _dlg = wx.FileDialog(self, defaultDir=APP_SETTING.projectPath,
                             wildcard='Project file (*.proj)|*.proj')
        _ret = _dlg.ShowModal()
        if _ret == wx.ID_OK:
            _path = _dlg.GetPath()
            _project = Project('_tmp')
            _proj_file_io = _project.open_project(_path)
            _proj_mgr_panel = GuiProjectManagerPanel(self._panelProjectMgr)
            _proj_mgr_panel.init_project(_project)
            _proj_mgr_panel.deserialize(_proj_file_io.body)
            _proj_mgr_panel.uuid = util_get_uuid_string()
            self._panelProjectMgr.set_content(_proj_mgr_panel)
            self._currentProject = _project
            self.remove_cached_pane()
            _ui_pesp = self._currentProject.load_ui_perspective()
            if _ui_pesp is not None:
                self._auiMgr.LoadPerspective(self._currentProject.load_ui_perspective())
            self._enable_tb_tc()

    def remove_cached_pane(self):
        for k, v in self._panelCache.items():
            self._auiMgr.DetachPane(v)
            v.Destroy()
        self._panelCache.clear()
        self._auiMgr.Update()

    def on_menu_new_project_clicked(self, evt):
        if self._currentProject:
            if not self._currentProject.savedState:
                # todo: prompt msgbox to save the project
                pass
        self._create_new_project()
        if self._currentProject is not None:
            _proj_mgr_content_panel = GuiProjectManagerPanel(self._panelProjectMgr)
            _proj_mgr_content_panel.init_project(self._currentProject)
            _proj_mgr_content_panel.uuid = util_get_uuid_string()
            self._panelProjectMgr.set_content(_proj_mgr_content_panel)
            self._currentProject.save_project(_proj_mgr_content_panel)
            _root_evt_uuid = self._panelProjectMgr.contentPanel.get_root_event_uuid()
            _root_stc_uuid = self._panelProjectMgr.contentPanel.get_root_state_uuid()
            self._currentProject.create_new_stc_file(_root_stc_uuid)
            self._currentProject.create_new_evt_file(_root_evt_uuid)
            self.remove_cached_pane()
            self._enable_tb_tc()

    def _create_new_project(self):
        self._currentProject = None
        _dlg = NewProjectDialog(APP_SETTING.projectPath, self)
        _ret = _dlg.ShowModal()
        if _ret == wx.ID_OK:
            if _dlg.projNameTextEdit.IsEmpty():
                _msg = wx.MessageBox(' fail to create project, since project name is empty', 'Fail')
                return
            _project_name = _dlg.projNameTextEdit.GetValue()
            _project_path = _dlg.projectPath
            _project_full_path = os.path.join(_project_path, _project_name)
            _exist = util_is_dir_exist(_project_full_path)
            if _exist:
                _msg = wx.MessageBox(' fail to create project, since project already exist', 'Fail')
                return
            self._currentProject = Project(_project_name)
            self._currentProject.set_project_workspace_path(_project_path)
            self._currentProject.create_new_project()

    def on_menu_new_file_clicked(self, evt):
        wx.MessageBox(' fail to create file, see you next version', 'Fail')

    def on_ext_sig_project_item_select_change(self, item_data: StandardItemData):
        # todo: next version show the props of project items
        if hasattr(item_data, 'role'):
            _role = item_data.role
            if _role == EnumItemRole.DEV_FEATURE:
                pass
            elif _role == EnumItemRole.USER_FEATURE:
                pass
            elif _role == EnumItemRole.DEV_FEATURE_OBO:
                pass
            else:
                pass

    def on_ext_sig_project_item_dclicked(self, uuid):
        _removed_cache = None
        if uuid in self._panelCache:
            _panel = self._panelCache.get(uuid)
            if _panel.role == EnumPanelRole.USER_FEATURE_RESOLVER:
                _removed_cache = uuid
        if _removed_cache is not None:
            _panel = self._panelCache.get(uuid)
            self._auiMgr.DetachPane(_panel)
            self._panelCache.pop(_removed_cache)
            self._auiMgr.Update()
            del _removed_cache
        _path = self._panelProjectMgr.contentPanel.get_item_path_by_uuid(uuid)
        _role = self._panelProjectMgr.contentPanel.get_item_role_by_uuid(uuid)
        _exist = self._auiMgr.GetPaneByName(uuid)
        _exist_in_proj = self._currentProject.get_file_io(uuid, _role)
        _caption = '%s' % _path

        if not _exist.IsOk():
            if _role == EnumItemRole.DEV_FEATURE_STATE or _role == EnumItemRole.USER_FEATURE_STATE:
                _panel = StateChartCanvasViewPanel(self, wx.ID_ANY)
                if _exist_in_proj is not None:
                    _panel.deserialize(_exist_in_proj.body)
            elif _role == EnumItemRole.DEV_FEATURE_EVENT or _role == EnumItemRole.USER_FEATURE_EVENT:
                _evt_data = self._currentProject.get_event_data(uuid)
                _panel = EventEditorPanel(self, _evt_data, self._currentProject.builtInEvents)
                if _exist_in_proj is not None:
                    _panel.deserialize(_evt_data)
            elif _role == EnumItemRole.DEV_FEATURE_OBO:
                _obo_data = self._currentProject.get_obo_data(uuid)
                _panel = OBOEditorPanel(self, _obo_data, self._currentProject.builtInObos)
                if _exist_in_proj is not None:
                    _panel.deserialize(_obo_data)
            elif _role == EnumItemRole.USER_FEATURE_RESOLVER:
                _root_state_uuid = self._panelProjectMgr.contentPanel.get_root_state_uuid()
                _root_obo_uuid = self._panelProjectMgr.contentPanel.get_root_obo_uuid()
                _obo_data = self._currentProject.get_obo_data(_root_obo_uuid, True)
                _root_stc_file_io = self._currentProject.get_file_io(_root_state_uuid, EnumItemRole.DEV_FEATURE_STATE)
                _state_uuid = self.get_associated_state_uuid(uuid)
                _uf_stc_file_io = self._currentProject.get_file_io(_state_uuid, EnumItemRole.USER_FEATURE_STATE)
                _uf_name = self._panelProjectMgr.contentPanel.get_feature_text_by_uuid(_state_uuid)
                _root_name = self._panelProjectMgr.contentPanel.get_feature_text_by_uuid(_root_state_uuid)
                _panel = FeatureResolverPanel(_obo_data, self, _uf_stc_file_io, _root_stc_file_io)
                _panel.set_uuid(uuid)
                _panel.set_graph_cluster_name(_uf_name, _root_name)
                if _exist_in_proj is not None:
                    _exist_in_proj.read()
                    _panel.deserialize(_exist_in_proj.body)
            else:
                return
            if uuid in self._panelCache:
                raise ValueError('panel already exist in cache')
            _panel.uuid = uuid
            _panel.Fit()
            _bestSize = _panel.GetBestSize()
            _centerDefaultAuiInfo = aui.AuiPaneInfo().BestSize(*_bestSize).Caption(_caption).Name(uuid). \
                DestroyOnClose(False).Center().Snappable().Dockable(). \
                MinimizeButton(True).MaximizeButton(True)
            self._centerTargetAuiInfo.BestSize(_bestSize)
            self._auiMgr.AddPane(_panel, _centerDefaultAuiInfo, target=self._centerTargetAuiInfo)
            self._auiMgr.Update()
            self._panelCache.update({uuid: _panel})
        else:
            # if exist
            _panel = self._panelCache.get(uuid)
            if _panel.IsShown():
                self._auiMgr.RequestUserAttention(_panel)
            else:
                self._auiMgr.ShowPane(_panel, True)

        _w, _h = self.GetClientSize()
        _pw, _ph = _panel.GetBestSize()
        _w = max(_w, _pw + 240)
        _h = max(_h, _ph)
        self.SetClientSize(_w, _h)
        _panel.SetFocus()

    def on_ext_sig_prop_show_required(self, sender, uuid):
        self._propContainerPane.toggle_panel_by_uuid(uuid)

    def on_ext_sig_session_name_changed(self, sender, uuid, new_name):
        self._rename_props_container_pane_caption(self._propsPaneCaptionFmt % new_name)
        # todo: rename opened tab label

    def _rename_props_container_pane_caption(self, caption):
        _pane = self._auiMgr.GetPaneByName(self.PANE_PROPS_CONTAINER_NAME)
        if _pane:
            _pane.Caption(caption)
            self._auiMgr.Update()

    def on_ext_sig_rack_item_select_changed(self, sender, item_data):
        _uuid = item_data.uuid
        self._propContainerPane.toggle_panel_by_uuid(_uuid)
        _current_prop_panel = self._propContainerPane.get_panel_by_uuid(_uuid)
        if _current_prop_panel:
            _new_cap = self._propsPaneCaptionFmt % _current_prop_panel.p_name
            self._rename_props_container_pane_caption(_new_cap)
        else:
            self._rename_props_container_pane_caption(self._propsPaneCaptionFmt % 'No')

    def on_ext_sig_new_session_created(self, sender, uuid, session_name, flag):
        if flag == 'DDI':
            _pane_caption = self._propsPaneCaptionFmt % session_name
            _ddi_session_prop_pane = DDISessionPropsContentPanel(uuid, parent=self._invisiblePanel)
            _ddi_session_prop_pane.p_name = session_name
            self._propContainerPane.set_content(_ddi_session_prop_pane)
            self._rename_props_container_pane_caption(_pane_caption)
        self._auiMgr.Update()

    def on_update_ui(self, event):
        _agw_flags = self._auiMgr.GetAGWFlags()
        _evt_src_id = event.GetId()
        event.Skip()

    def on_size(self, event: wx.Event):
        event.Skip()

    def on_erase_background(self, event: wx.Event):
        event.Skip()

    def on_exit(self, event: wx.Event):
        self.Close(force=True)
        event.Skip()

    def on_about(self, event: wx.Event):
        _msg = "This Is The About Dialog Of MBT.\n\n" + \
               "Author: Gaofeng Zhang @ 19 Sep 2020\n\n" + \
               "Welcome To wxPython " + wx.VERSION_STRING + "!!"

        _dlg = wx.MessageDialog(self, _msg, "About MBT",
                                wx.OK | wx.ICON_INFORMATION)

        if wx.Platform != '__WXMAC__':
            _dlg.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,
                                 False, '', wx.FONTENCODING_DEFAULT))

        _dlg.ShowModal()
        _dlg.Destroy()
