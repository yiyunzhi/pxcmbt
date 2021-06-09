# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : pannel_rack.py
# ------------------------------------------------------------------------------
#
# File          : pannel_rack.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import wx
from .ctrl_tree import GenericTreeCtrl
from application.define import StandardItemData, EnumItemRole, EnumAppSignals
from .define_gui import PATH_GUI_IMAGES
from .utils_helper import util_get_uuid_string, util_wx_tree_walk_branches
from .menu_context_menu import (GuiModelContextMenu,
                                GuiDeviceFeatureContextMenu,
                                GuiUserFeatureContextMenu,
                                GuiUserFeatureStateContextMenu,
                                GuiFeatureLibContextMenu,
                                GuiFeatureLibItemContextMenu)


class FeaturePanelIconRepo:
    def __init__(self):
        self._icon_size = (16, 16)
        self._image_list = wx.ImageList(*self._icon_size)
        self.invalidIcon = self._image_list.Add(
            wx.ArtProvider.GetBitmap(wx.ART_MISSING_IMAGE, wx.ART_OTHER, self._icon_size))
        self.signalsIcon = self._image_list.Add(
            wx.ArtProvider.GetBitmap(wx.ART_LIST_VIEW, wx.ART_OTHER, self._icon_size))
        self.exclamationIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_exclamation.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.featureIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_feature.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.stateIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_state.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.modelIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_model.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.variableIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_variable.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.funcsIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_function.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.libIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_library.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())

    def get_icon_size(self):
        return self._icon_size

    def get_image_list(self):
        return self._image_list


class GuiFeaturePanel(wx.Panel):
    def __init__(self, parent):
        # Use the WANTS_CHARS style so the panel doesn't eat the Return key.
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)
        self.role = None
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.tree = GenericTreeCtrl(self, wx.NewIdRef(), wx.DefaultPosition, wx.DefaultSize,
                                    wx.TR_HAS_BUTTONS
                                    # | wx.TR_MULTIPLE
                                    # | wx.TR_HIDE_ROOT
                                    )
        self._itemMap = dict()
        self._iconRepo = FeaturePanelIconRepo()
        self._icon_size = (16, 16)

        # style
        self.COLOR_SUCCESS = wx.Colour('#99FF99')
        self.COLOR_ERROR = wx.Colour('#FF6666')
        self.COLOR_WARNING = wx.Colour('#FFFF99')
        self.COLOR_HIGHLIGHT_TEXT = wx.Colour('#333')
        # context menu
        self._modelCtxMenu = GuiModelContextMenu(self)
        self._deviceFeatureCtxMenu = GuiDeviceFeatureContextMenu(self)
        self._userFeatureCtxMenu = GuiUserFeatureContextMenu(self)
        self._featureStateCtxMenu = GuiUserFeatureStateContextMenu(self)
        self._featureLibCtxMenu = GuiFeatureLibContextMenu(self)
        self._featureLibItemCtxMenu = GuiFeatureLibItemContextMenu(self)
        # attributes
        self._current_activated_item = None
        # tree build
        self.tree.SetImageList(self._iconRepo.get_image_list())
        # NOTE:  For some reason tree items have to have a data object in
        #        order to be sorted.  Since our compare just uses the labels
        #        we don't need any real data, so we'll just use None below for
        #        the item data.

        self.root = self.tree.AddRoot("Model")
        self.rootItemData = StandardItemData()
        self.rootItemData.role = EnumItemRole.ROOT
        self.rootItemData.uuid = util_get_uuid_string()
        self.tree.SetItemData(self.root, self.rootItemData)
        self.tree.SetItemImage(self.root, self._iconRepo.modelIcon, wx.TreeItemIcon_Normal)
        self._itemMap.update({self.rootItemData.uuid: self.root})

        self._deviceFeatureItem = self.tree.AppendItem(self.root, "DeviceFeature")
        self.deviceItemData = StandardItemData()
        self.deviceItemData.role = EnumItemRole.DEV_FEATURE
        self.deviceItemData.uuid = util_get_uuid_string()
        self.deviceItemData.labelReadonly = True
        self.tree.SetItemData(self._deviceFeatureItem, self.deviceItemData)
        self.tree.SetItemImage(self._deviceFeatureItem, self._iconRepo.featureIcon, wx.TreeItemIcon_Normal)
        self._itemMap.update({self.deviceItemData.uuid: self._deviceFeatureItem})

        self._deviceStateItem = self.tree.AppendItem(self._deviceFeatureItem, "State")
        self.deviceStateItemData = StandardItemData()
        self.deviceStateItemData.role = EnumItemRole.DEV_FEATURE_STATE
        self.deviceStateItemData.uuid = util_get_uuid_string()
        self.deviceStateItemData.labelReadonly = True
        self.tree.SetItemData(self._deviceStateItem, self.deviceStateItemData)
        self.tree.SetItemImage(self._deviceStateItem, self._iconRepo.stateIcon, wx.TreeItemIcon_Normal)
        self._itemMap.update({self.deviceStateItemData.uuid: self._deviceStateItem})

        self._featureLibItem = self.tree.AppendItem(self.root, "Feature Libraries")
        self.featureLibItemData = StandardItemData()
        self.featureLibItemData.role = EnumItemRole.FEATURE_LIB
        self.featureLibItemData.uuid = util_get_uuid_string()
        self.featureLibItemData.labelReadonly = True
        self.tree.SetItemData(self._featureLibItem, self.featureLibItemData)
        self.tree.SetItemImage(self._featureLibItem, self._iconRepo.libIcon, wx.TreeItemIcon_Normal)
        self._itemMap.update({self.featureLibItemData.uuid: self._featureLibItem})

        self.tree.Expand(self.root)
        self.tree.Expand(self._deviceFeatureItem)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_select_changed, self.tree)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_item_activate, self.tree)
        self.tree.Bind(wx.EVT_TREE_ITEM_GETTOOLTIP, self.on_item_get_tooltip)
        self.tree.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_context_menu)
        # set the acceleratorTable
        _id_F2 = wx.NewId()

        self.Bind(wx.EVT_MENU, self.on_f2_pressed, id=_id_F2)

        accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_NORMAL, wx.WXK_F2, _id_F2)
        ])
        self.SetAcceleratorTable(accel_tbl)

    def on_item_get_tooltip(self, evt):
        _item = evt.GetItem()
        _item_data = self.tree.GetItemData(_item)
        if isinstance(_item_data, StandardItemData):
            if hasattr(_item_data, 'tooltip'):
                evt.SetToolTip(_item_data.tooltip)

    def on_f2_pressed(self, evt):
        _selected = self.tree.GetSelection()
        if _selected:
            _data = self.tree.GetItemData(_selected)
            if hasattr(_data, 'labelReadonly'):
                if not _data.labelReadonly:
                    self.on_rename_label()
        evt.Skip()

    def on_context_menu(self, event):
        _item = event.GetItem()
        if _item:
            self.tree.SelectItem(_item)
            _role = self.tree.GetItemData(_item).role
            if _role == EnumItemRole.ROOT:
                self._modelCtxMenu.show()
            elif _role == EnumItemRole.DEV_FEATURE:
                self._deviceFeatureCtxMenu.show()
            elif _role == EnumItemRole.USER_STATE_FEATURE:
                self._userFeatureCtxMenu.show()
            elif _role == EnumItemRole.FEATURE_LIB:
                self._featureLibCtxMenu.show()
            elif _role == EnumItemRole.FEATURE_LIB_ITEM:
                self._featureLibItemCtxMenu.show()

    def on_size(self, event):
        self.tree.SetSize(0, 0, *self.GetClientSize())

    def _reset_item_style(self, item):
        self.tree.SetItemTextColour(item, wx.Colour('#000'))
        self.tree.SetItemBold(item, False)
        _default_bg_color = self.tree.GetBackgroundColour()
        self.tree.SetItemBackgroundColour(item, _default_bg_color)

    def _set_item_txt_style_success(self, item):
        self.tree.SetItemTextColour(item, self.COLOR_HIGHLIGHT_TEXT)
        self.tree.SetItemBold(item, True)
        self.tree.SetItemBackgroundColour(item, self.COLOR_SUCCESS)

    def _set_item_txt_style_error(self, item):
        self.tree.SetItemTextColour(item, self.COLOR_HIGHLIGHT_TEXT)
        self.tree.SetItemBold(item, True)
        self.tree.SetItemBackgroundColour(item, self.COLOR_ERROR)

    def _set_item_txt_style_warning(self, item):
        self.tree.SetItemTextColour(item, self.COLOR_HIGHLIGHT_TEXT)
        self.tree.SetItemBold(item, True)
        self.tree.SetItemBackgroundColour(item, self.COLOR_WARNING)

    def on_select_changed(self, event):
        _item = event.GetItem()
        self._current_activated_item = _item
        _data = self.tree.GetItemData(_item)
        # EnumRackPanelSignals.sigV2MRackItemSelectChanged.send(self, item_data=_data)
        event.Skip()

    def on_item_activate(self, event):
        # double click fire this event only
        _item = event.GetItem()
        _data = self.tree.GetItemData(_item)
        if hasattr(_data, 'uuid'):
            EnumAppSignals.sigV2VModelTreeItemDoubleClicked.send(self, uuid=_data.uuid)

    def update_item_tool_tip(self, uuid, tooltip_string):
        _item = self._itemMap.get(uuid)
        if _item is None:
            return
        _item_data = self.tree.GetItemData(_item)
        _item_data.tooltip = tooltip_string

    def generate_session_unique_name(self, original_name):
        _names = [self.tree.GetItemText(node) for node in
                  util_wx_tree_walk_branches(self.tree, self._deviceFeatureItem)]
        _suffix = 0
        _name = original_name
        while _name in _names:
            _suffix += 1
            _name = '%s%s' % (original_name, '' if _suffix == 0 else str(_suffix))
        return _name

    def on_add_user_feature(self, evt, flag):
        _signals_icon_idx = self._iconRepo.signalsIcon
        _funcs_icon_idx = self._iconRepo.funcsIcon
        _session_icon_idx = getattr(self._iconRepo, 'session%sIconDefault' % flag)
        _name = self.generate_session_unique_name("%s_Untitled" % flag)
        # append session item
        _session_item = self.tree.AppendItem(self._sessions_item, _name)
        _session_item_data = StandardItemData()
        _session_item_data.role = EnumItemRole.SESSION
        _session_item_data.uuid = util_get_uuid_string()
        _session_item_data.flag = flag
        _session_item_data.labelReadonly = False
        self._itemMap.update({_session_item_data.uuid: _session_item})
        self.tree.SetItemData(_session_item, _session_item_data)
        self.tree.SetItemImage(_session_item, _session_icon_idx, wx.TreeItemIcon_Normal)
        # append signal item
        _signals_item_data = StandardItemData()
        _signals_item_data.role = EnumItemRole.SIGNALS
        _signals_item_data.uuid = util_get_uuid_string()
        _signals_item_data.flag = flag
        _signals_item_data.labelReadonly = True
        _signals_item = self.tree.AppendItem(_session_item, "Signals")
        self._itemMap.update({_signals_item_data.uuid: _signals_item_data})
        self.tree.SetItemData(_signals_item, _signals_item_data)
        self.tree.SetItemImage(_signals_item, _signals_icon_idx, wx.TreeItemIcon_Normal)
        # append func item
        _funcs_item_data = StandardItemData()
        _funcs_item_data.role = EnumItemRole.FUNCS
        _funcs_item_data.uuid = helper.util_get_uuid_string()
        _funcs_item_data.flag = flag
        _funcs_item_data.labelReadonly = True
        _funcs_item = self.tree.AppendItem(_session_item, "Functions")
        self._itemMap.update({_funcs_item_data.uuid: _funcs_item_data})
        self.tree.SetItemData(_funcs_item, _funcs_item_data)
        self.tree.SetItemImage(_funcs_item, _funcs_icon_idx, wx.TreeItemIcon_Normal)
        self.tree.ExpandAll()
        self.tree.SelectItem(_session_item, True)
        # EnumRackPanelSignals.sigV2MNewSession.send(self, uuid=_session_item_data.uuid, session_name=_name, flag=flag)

    def on_pick_up_user_feature(self, evt, flag):
        pass

    def on_rename_feature_label(self, *args):
        _selection = self.tree.GetSelection()
        if _selection is None:
            return
        _data = self.tree.GetItemData(_selection)
        if hasattr(_data, 'uuid'):
            EnumRackPanelSignals.sigV2VStartSessionReq.send(self, data=_data)

    def on_show_feature_property(self, *args):
        _selection = self.tree.GetSelection()
        if _selection is None:
            return
        _data = self.tree.GetItemData(_selection)
        if hasattr(_data, 'uuid'):
            EnumRackPanelSignals.sigV2VStopSessionReq.send(self, data=_data)

    def on_show_session_property(self, evt):
        _selected = self.tree.GetSelection()
        if _selected:
            _item_data = self.tree.GetItemData(_selected)
            EnumRackPanelSignals.sigV2VRackItemShowPropsReq.send(self, uuid=_item_data.uuid)
        evt.Skip()

    def on_rename_feature_state_label(self, *args):
        _selected = self.tree.GetSelection()
        # _focused = self.tree.GetFocusedItem()
        _dlg = wx.TextEntryDialog(self, 'New name', 'Rename', 'Rename')
        _old_name = self.tree.GetItemText(_selected)
        _uuid = self.tree.GetItemData(_selected).uuid
        _dlg.SetValue(_old_name)
        if _dlg.ShowModal() == wx.ID_OK:
            _new_name = _dlg.GetValue()
            self.tree.SetItemText(_selected, _dlg.GetValue())
            EnumRackPanelSignals.sigV2MSessionNameChanged.send(self, uuid=_uuid, new_name=_new_name)
        _dlg.Destroy()

    def on_show_feature_state_property(self, *args):
        pass

    def on_reload_feature_lib(self, evt):
        pass

    def on_show_lib_detail(self, evt):
        pass

    def on_add_feature_to_use(self, evt):
        pass

    def on_show_lib_item_detail(self, evt):
        pass

    def get_item_name_by_uuid(self, uuid):
        _item = self._itemMap.get(uuid)
        if _item is not None:
            return self.tree.GetItemText(_item)
        else:
            return None

    def get_item_path_by_uuid(self, uuid):
        _item = self._itemMap.get(uuid)
        if _item is not None:
            _path=list()
            _path.append(self.tree.GetItemText(_item))
            _parent=self.tree.GetItemParent(_item)
            while _parent:
                _path.append(self.tree.GetItemText(_parent))
                _parent = self.tree.GetItemParent(_parent)
            return '/'.join(_path[::-1])
        else:
            return None

    def highlight_item_by_uuid(self, uuid):
        _item = self._itemMap.get(uuid)
        if _item is not None:
            self.tree.SelectItem(_item, True)

    def set_session_item_in_state_run(self, uuid):
        _session_item = self._itemMap.get(uuid)
        if _session_item is None:
            return
        _item_data = self.tree.GetItemData(_session_item)
        _item_data.tooltip = 'IS STARTET'
        _img = getattr(self._iconRepo, 'session%sIconActive' % _item_data.flag)
        self.tree.SetItemImage(_session_item, _img, wx.TreeItemIcon_Normal)

    def set_session_item_in_state_stop(self, uuid):
        _session_item = self._itemMap.get(uuid)
        if _session_item is None:
            return
        _item_data = self.tree.GetItemData(_session_item)
        _item_data.tooltip = 'IS STOPPED'
        _img = getattr(self._iconRepo, 'session%sIconDefault' % _item_data.flag)
        self.tree.SetItemImage(_session_item, _img, wx.TreeItemIcon_Normal)

    def remove_session_item_nodes(self, uuid):
        _session_item = self._itemMap.get(uuid)
        _del_slot = []
        _del_ep = []
        for x in helper.util_wx_tree_walk_branches(self.tree, _session_item):
            _data = self.tree.GetItemData(x)
            if hasattr(_data, 'role'):
                if _data.role == EnumItemRole.SLOT:
                    _del_slot.append(x)
                    self._itemMap.pop(_data.uuid)
                    for y in helper.util_wx_tree_walk_branches(self.tree, x):
                        _data2 = self.tree.GetItemData(y)
                        if _data2.role == EnumItemRole.ENDPOINT:
                            _del_ep.append(_data2.uuid)
                            self._itemMap.pop(_data2.uuid)
        for x in _del_slot:
            self.tree.Delete(x)
        return _del_ep

    def _update_slot_ep_node(self, parent_node, parent_uuid, slot_path, label, flag):
        _ep_data = StandardItemData()
        _ep_data.uuid = helper.util_get_uuid_string()
        _ep_data.role = EnumItemRole.ENDPOINT
        _ep_data.flag = flag
        _ep_data.labelReadonly = True
        _ep_data.parentUUID = parent_uuid
        _ep_data.slotPath = slot_path
        _ep_icon = getattr(self._iconRepo, 'slot%sIcon' % _ep_data.flag)
        _ep_item = self.tree.AppendItem(parent_node, label)
        self.tree.SetItemImage(_ep_item, _ep_icon, wx.TreeItemIcon_Normal)
        self.tree.SetItemData(_ep_item, _ep_data)
        self._itemMap.update({_ep_data.uuid: _ep_item})
        return _ep_data

    def update_session_item_nodes(self, uuid, nodes, endpoints):
        _item = self._itemMap.get(uuid)
        _ep_items_data = dict()
        if _item is None:
            return _ep_items_data
        for slot_path, slot_inst in nodes.items():
            _name = slot_inst.p_name
            _slot_path = slot_inst.p_slot_path
            _slot_item = self.tree.AppendItem(_item, '#%s %s' % (slot_inst.p_slot_nr, _name))
            _slot_item_data = StandardItemData()
            _slot_item_data.role = EnumItemRole.SLOT
            _slot_item_data.uuid = helper.util_get_uuid_string()
            _slot_item_data.flag = _slot_path
            _slot_item_data.labelReadonly = False
            self._itemMap.update({_slot_item_data.uuid: _slot_item})
            self.tree.SetItemData(_slot_item, _slot_item_data)
            _bus_family = slot_inst.p_bus_family
            _prod_family = slot_inst.p_family
            _is_safety = any([x in _prod_family for x in ['PS', 'SBT', 'SBTV3']])
            if _is_safety:
                _slot_icon = getattr(self._iconRepo, 'slot%sFSIcon' % _bus_family)
            else:
                _slot_icon = getattr(self._iconRepo, 'slot%sIcon' % _bus_family)
            self.tree.SetItemImage(_slot_item, _slot_icon, wx.TreeItemIcon_Normal)
            # guess endpoints
            _ep_io_key = '%s-%s' % (_slot_path, EPTypeEnum.EP_IO)
            _ep_info_key = '%s-%s' % (_slot_path, EPTypeEnum.EP_INFO)
            _ep_fcom_key = '%s-%s' % (_slot_path, EPTypeEnum.EP_FCOM)
            _ep_diag_key = '%s-%s' % (_slot_path, EPTypeEnum.EP_DIAG)
            _ep_param_key = '%s-%s' % (_slot_path, EPTypeEnum.EP_PARAM)
            _ep_io = endpoints.get(_ep_io_key)
            _ep_info = endpoints.get(_ep_info_key)
            _ep_fcom = endpoints.get(_ep_fcom_key)
            _ep_diag = endpoints.get(_ep_diag_key)
            _ep_param = endpoints.get(_ep_param_key)
            if _ep_io:
                _ep_data = self._update_slot_ep_node(_slot_item, uuid, slot_path,
                                                     '%s' % EPTypeEnum.EP_IO, EPTypeEnum.EP_IO)
                _ep_items_data.update({_ep_data.uuid: _ep_data})
            if _ep_info:
                _ep_data = self._update_slot_ep_node(_slot_item, uuid, slot_path,
                                                     '%s' % EPTypeEnum.EP_INFO, EPTypeEnum.EP_INFO)
                _ep_items_data.update({_ep_data.uuid: _ep_data})
            if _ep_fcom:
                _ep_data = self._update_slot_ep_node(_slot_item, uuid, slot_path,
                                                     '%s' % EPTypeEnum.EP_FCOM, EPTypeEnum.EP_FCOM)
                _ep_items_data.update({_ep_data.uuid: _ep_data})
            if _ep_diag:
                _ep_data = self._update_slot_ep_node(_slot_item, uuid, slot_path,
                                                     '%s' % EPTypeEnum.EP_DIAG, EPTypeEnum.EP_DIAG)
                _ep_items_data.update({_ep_data.uuid: _ep_data})
            if _ep_param:
                _ep_data = self._update_slot_ep_node(_slot_item, uuid, slot_path,
                                                     '%s' % EPTypeEnum.EP_PARAM, EPTypeEnum.EP_PARAM)
                _ep_items_data.update({_ep_data.uuid: _ep_data})
        return _ep_items_data

    def set_session_item_in_state_error(self, uuid, err_str):
        _session_item = self._itemMap.get(uuid)
        if _session_item is None:
            return
        _item_data = self.tree.GetItemData(_session_item)
        _item_data.tooltip = 'Error: %s' % err_str
        self.tree.SetItemImage(_session_item, self._iconRepo.exclamationIcon, wx.TreeItemIcon_Normal)
