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
import sys, os, traceback, threading
import wx
import wx.lib.agw.aui as aui
from pubsub import pub
from .assets_images import *
from .panel_canvas import StateChartCanvasViewPanel
from .panel_feature import GuiFeaturePanel
from .panel_props_container import PropContainerPanel
from .panel_console import ConsolePanel
from .panel_event_editor import EventEditorPanel
from .define_gui import _, PATH_GUI_IMAGES, EnumCanvasToolbarMode
from application.log_logger import get_logger
from application.define import EnumAppSignals, EnumPanelRole, EnumItemRole


# todo: integration with tcs.

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

    def __init__(self, parent, wx_id=wx.ID_ANY, title='', pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE | wx.SUNKEN_BORDER, log=_default_wx_log):
        sys.excepthook = self.except_hook
        super(FrameMain, self).__init__(parent, wx_id, title, pos, size, style)
        self._auiMgr = aui.AuiManager(agwFlags=aui.AUI_MGR_DEFAULT | aui.AUI_MGR_ALLOW_ACTIVE_PANE)
        self._icon_size = (16, 16)
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
            MinimizeButton(True).MaximizeButton(True)
        # Attributes
        self._currentCanvasPane = None
        self._canvasPanelCache = dict()
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
        # set the acceleratorTable
        # _id_F1 = wx.NewId()
        # _id_F2 = wx.NewId()

        # self.Bind(wx.EVT_MENU, self.on_f1_pressed, id=_id_F1)
        # self.Bind(wx.EVT_MENU, self.on_f2_pressed, id=_id_F2)

        # accel_tbl = wx.AcceleratorTable([
        #    (wx.ACCEL_NORMAL, wx.WXK_F1, _id_F1),
        #    (wx.ACCEL_NORMAL, wx.WXK_F2, _id_F2)
        # ])
        # self.SetAcceleratorTable(accel_tbl)

        self.CreateStatusBar()
        self.GetStatusBar().SetStatusText("Ready")
        self.create_menu_bar()
        # self.create_tool_bar()
        self._show_toolbar(False)
        self.build_panes()
        self.bind_events()
        self.Fit()
        self.Center()
        wx.CallAfter(self.SendSizeEvent)
        self._consolePane.write_info_content('---App Initial finished---')

    def _show_toolbar(self, state=True):
        pass

    def _set_canvas_toolbar_mode(self, mode: EnumCanvasToolbarMode):
        _tool = self._toolbar.FindToolByIndex(mode)
        if _tool is not None:
            self._toolbar.ToggleTool(_tool.GetId(), True)

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

    def build_panes(self):
        self._panelFeature = GuiFeaturePanel(self)
        self._propContainerPane = PropContainerPanel(parent=self)
        self._auiMgr.AddPane(self._panelFeature, aui.AuiPaneInfo().Name("featurePanel").Caption("Model").
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
        _tb_icon_size = wx.Size(16, 16)
        _tb = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                             agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        _tb.SetToolBitmapSize(_tb_icon_size)
        # _pointer_shape_icon = wx.Image(PATH_GUI_IMAGES + '\\icon_shape_pointer_bk.png', wx.BITMAP_TYPE_PNG).Scale(
        #     *_tb_icon_size).ConvertToBitmap()
        # _tb_pointer = wx.NewIdRef()
        # _tb.AddRadioTool(_tb_pointer, "Pointer", _pointer_shape_icon,
        #                   disabled_bitmap=wx.NullBitmap, short_help_string='Pointer',
        #                   client_data=EnumCanvasToolbarMode.POINTER)
        _tb.AddSeparator()
        _tb.Realize()
        # self.Bind(wx.EVT_TOOL, lambda evt: self.on_canvas_tool_changed(evt, EnumCanvasToolbarMode.POINTER),
        #          _tb_pointer)
        self._toolbar = _tb
        self._auiMgr.AddPane(_tb, aui.AuiPaneInfo().Name("CanvasTool").Caption("General Tools").
                             ToolbarPane().Left().Layer(1).Position(0).BestSize((-1, 24)))

    def create_menu_bar(self):
        # create menu
        _mb = wx.MenuBar()

        _file_menu = wx.Menu()
        _file_menu.Append(wx.ID_NEW, _('New'))
        _file_menu.Append(wx.ID_OPEN, _('Open'))
        _file_menu.Append(wx.ID_SAVE, _('Save'))
        _file_menu.Append(wx.ID_SAVEAS, _('Save As'))
        _file_menu.AppendSeparator()
        _file_menu.Append(wx.ID_EXIT, _('Exit'))

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
        # bind menu event
        self.Bind(wx.EVT_MENU, self.on_menu_new_clicked, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.on_about, id=wx.ID_ABOUT)
        # bind event update UI, multi allowed
        pub.subscribe(self.on_ext_sig_model_item_double_clicked, EnumAppSignals.sigV2VModelTreeItemDoubleClicked)

    def on_child_focused(self, evt):
        _win = evt.GetWindow()
        evt.Skip()

    def on_aui_pane_activated(self, evt):
        _pane = evt.GetPane()
        if hasattr(_pane, 'uuid'):
            if _pane.uuid in self._canvasPanelCache:
                self._panelFeature.highlight_item_by_uuid(_pane.uuid)
            if _pane.role == EnumPanelRole.STATE_CHART_CANVAS:
                self._currentCanvasPane = _pane
                self._auiMgr.ShowPane(self._toolbar, True)
        evt.Skip()

    def on_window_closed(self, evt):
        evt.Skip()

    def on_menu_new_clicked(self, evt):
        _win = wx.MDIChildFrame(self, -1, "Child Window: %d" % self._childWinCount, style=wx.DEFAULT_FRAME_STYLE)
        _win.Show(True)
        # self._auiMgr.AddPane(_win, aui.AuiPaneInfo().Name("Child%s" % self._childWinCount).CenterPane())
        self._childWinCount += 1
        # self._auiMgr.Update()

    def on_ext_sig_model_item_double_clicked(self, uuid):
        _exist = self._auiMgr.GetPaneByName(uuid)
        if not _exist.IsOk():
            _path = self._panelFeature.get_item_path_by_uuid(uuid)
            _role = self._panelFeature.get_item_role_by_uuid(uuid)
            _caption = '%s' % _path
            if _role == EnumItemRole.DEV_FEATURE_STATE:
                _panel = StateChartCanvasViewPanel(self, wx.ID_ANY)
            elif _role == EnumItemRole.DEV_FEATURE_EVENT:
                _panel = EventEditorPanel(self)
            else:
                return
            _panel.uuid = uuid
            _centerDefaultAuiInfo = aui.AuiPaneInfo().BestSize((300, 300)).Caption(_caption).Name(uuid). \
                DestroyOnClose(False).Center().Snappable().Dockable(). \
                MinimizeButton(True).MaximizeButton(True)
            self._auiMgr.AddPane(_panel, _centerDefaultAuiInfo, target=self._centerTargetAuiInfo)
            self._auiMgr.Update()
            self._canvasPanelCache.update({uuid: _panel})
        else:
            _panel = self._canvasPanelCache.get(uuid)
            if _panel.IsShown():
                self._auiMgr.RequestUserAttention(_panel)
            else:
                self._auiMgr.ShowPane(_panel, True)
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
        _msg = "This Is The About Dialog Of The Pure Python Version Of AUI.\n\n" + \
               "Author: Andrea Gavana @ 23 Dec 2005\n\n" + \
               "Please Report Any Bug/Requests Of Improvements\n" + \
               "To Me At The Following Addresses:\n\n" + \
               "andrea.gavana@maerskoil.com\n" + "andrea.gavana@gmail.com\n\n" + \
               "Welcome To wxPython " + wx.VERSION_STRING + "!!"

        _dlg = wx.MessageDialog(self, _msg, "About",
                                wx.OK | wx.ICON_INFORMATION)

        if wx.Platform != '__WXMAC__':
            _dlg.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL,
                                 False, '', wx.FONTENCODING_DEFAULT))

        _dlg.ShowModal()
        _dlg.Destroy()
