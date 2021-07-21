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
from pubsub import pub
from .ctrl_tree import GenericTreeCtrl
from application.define import StandardItemData, EnumItemRole, EnumAppSignals
from .define_gui import PATH_GUI_IMAGES
from application.utils_helper import util_get_uuid_string, util_wx_tree_walk_branches
from .menu_context_menu import (GuiModelContextMenu,
                                GuiDeviceFeatureContextMenu,
                                GuiUserFeatureContextMenu,
                                GuiUserFeatureItemContextMenu,
                                GuiUserFeatureStateContextMenu,
                                GuiUserFeatureEvtContextMenu,
                                GuiDeviceFeatureEvtContextMenu,
                                GuiDeviceFeatureStateContextMenu)


class ProjectPanelIconRepo:
    def __init__(self):
        self._icon_size = (16, 16)
        self._image_list = wx.ImageList(*self._icon_size)
        self.fileIcon = self._image_list.Add(
            wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, self._icon_size))
        self.invalidIcon = self._image_list.Add(
            wx.ArtProvider.GetBitmap(wx.ART_MISSING_IMAGE, wx.ART_OTHER, self._icon_size))
        self.signalsIcon = self._image_list.Add(
            wx.ArtProvider.GetBitmap(wx.ART_LIST_VIEW, wx.ART_OTHER, self._icon_size))
        self.cubeIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_cube.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.rackIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_rack.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.exclamationIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_exclamation.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.featureIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_feature.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.stateIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_state.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.eventIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_char_e.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.modelIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_model.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.keyIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_key.png', wx.BITMAP_TYPE_PNG).Scale(
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
        self.sessionsIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_session.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.scriptIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_variable.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.funcsIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_function.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.sessionDDIIconDefault = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_ddi_default.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.sessionDDIIconActive = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_ddi_active.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.sessionPNIconDefault = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_pn_default.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.sessionPNIconActive = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_pn_active.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.sessionTCPIconDefault = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_tcp_default.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.sessionTCPIconActive = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_tcp_active.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.sessionVisaIconDefault = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_visa_default.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.sessionVisaIconActive = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_visa_active.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.slotIBIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_ib_slot.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.slotIBFSIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_ib_fs_slot.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.slotAXIOIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_axio_slot.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.slotAXIOFSIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_axio_fs_slot.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.slotEPDiagIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_epdiag.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.slotEPInfoIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_epinfo.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.slotEPFComIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_epfcom.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.slotEPIOIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_epio.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.slotEPParamIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_epparam.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())

    def get_icon_size(self):
        return self._icon_size

    def get_image_list(self):
        return self._image_list


class GuiProjectManagerContainerPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.WANTS_CHARS)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.contentPanel = None
        self.SetSizer(self.mainSizer)
        self.Layout()
        self.Fit()

    def set_content(self, content_panel):
        if self.contentPanel is not None:
            self.mainSizer.Detach(self.contentPanel)
            self.contentPanel.Destroy()
        self.mainSizer.Add(content_panel, 1, wx.EXPAND)
        self.contentPanel = content_panel
        self.Layout()
        self.Fit()


class GuiProjectManagerPanel(wx.Panel):
    def __init__(self, parent):
        # Use the WANTS_CHARS style so the panel doesn't eat the Return key.
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)
        self.role = None
        self.uuid = None
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.tree = GenericTreeCtrl(self, wx.NewIdRef(), wx.DefaultPosition, wx.DefaultSize,
                                    wx.TR_HAS_BUTTONS
                                    # | wx.TR_MULTIPLE
                                    # | wx.TR_HIDE_ROOT
                                    )
        self._itemMap = dict()
        self._iconRepo = ProjectPanelIconRepo()
        self._icon_size = (16, 16)

        # style
        self.COLOR_SUCCESS = wx.Colour('#99FF99')
        self.COLOR_ERROR = wx.Colour('#FF6666')
        self.COLOR_WARNING = wx.Colour('#FFFF99')
        self.COLOR_HIGHLIGHT_TEXT = wx.Colour('#333')
        # context menu
        self._modelCtxMenu = GuiModelContextMenu(self)
        self._deviceFeatureCtxMenu = GuiDeviceFeatureContextMenu(self)
        self._deviceFeatureStateCtxMenu = GuiDeviceFeatureStateContextMenu(self)
        self._deviceFeatureEvtCtxMenu = GuiDeviceFeatureEvtContextMenu(self)
        self._userFeatureCtxMenu = GuiUserFeatureContextMenu(self)
        self._userFeatureItemCtxMenu = GuiUserFeatureItemContextMenu(self)
        self._userFeatureStateCtxMenu = GuiUserFeatureStateContextMenu(self)
        self._userFeatureEvtCtxMenu = GuiUserFeatureEvtContextMenu(self)
        # attributes
        self._current_activated_item = None
        # tree build
        self.tree.SetImageList(self._iconRepo.get_image_list())
        # NOTE:  For some reason tree items have to have a data object in
        #        order to be sorted.  Since our compare just uses the labels
        #        we don't need any real data, so we'll just use None below for
        #        the item data.

        self.root = self.tree.AddRoot("Project")
        self.rootItemData = StandardItemData()
        self.rootItemData.role = EnumItemRole.ROOT
        self.rootItemData.uuid = util_get_uuid_string()
        self.tree.SetItemData(self.root, self.rootItemData)
        self.tree.SetItemImage(self.root, self._iconRepo.cubeIcon, wx.TreeItemIcon_Normal)
        self._itemMap.update({self.rootItemData.uuid: self.root})

        self._modelItem = self.tree.AppendItem(self.root, "FeatureModel")
        self.modelItemData = StandardItemData()
        self.modelItemData.role = EnumItemRole.MODEL
        self.modelItemData.uuid = util_get_uuid_string()
        self.tree.SetItemData(self._modelItem, self.modelItemData)
        self.tree.SetItemImage(self._modelItem, self._iconRepo.modelIcon, wx.TreeItemIcon_Normal)
        self._itemMap.update({self.modelItemData.uuid: self._modelItem})

        self._rackItem = self.tree.AppendItem(self.root, "Rack")
        self.rackItemData = StandardItemData()
        self.rackItemData.role = EnumItemRole.MODEL
        self.rackItemData.uuid = util_get_uuid_string()
        self.tree.SetItemData(self._rackItem, self.rackItemData)
        self.tree.SetItemImage(self._rackItem, self._iconRepo.rackIcon, wx.TreeItemIcon_Normal)
        self._itemMap.update({self.rackItemData.uuid: self._rackItem})

        self._sessions_item = self.tree.AppendItem(self._rackItem, "Sessions")
        self.sessionsItemData = StandardItemData()
        self.sessionsItemData.role = EnumItemRole.SESSIONS
        self.sessionsItemData.uuid = util_get_uuid_string()
        self.sessionsItemData.labelReadonly = True
        self.tree.SetItemData(self._sessions_item, self.sessionsItemData)
        self.tree.SetItemImage(self._sessions_item, self._iconRepo.sessionsIcon, wx.TreeItemIcon_Normal)

        self._scripts_item = self.tree.AppendItem(self._rackItem, "Scripts")
        self.scriptsItemData = StandardItemData()
        self.scriptsItemData.role = EnumItemRole.SCRIPTS
        self.scriptsItemData.uuid = util_get_uuid_string()
        self.scriptsItemData.labelReadonly = True
        self.tree.SetItemData(self._scripts_item, self.scriptsItemData)
        self.tree.SetItemImage(self._scripts_item, self._iconRepo.scriptIcon, wx.TreeItemIcon_Normal)

        self._rootFeatureItem = self.tree.AppendItem(self._modelItem, "Root")
        self.deviceItemData = StandardItemData()
        self.deviceItemData.role = EnumItemRole.DEV_FEATURE
        self.deviceItemData.uuid = util_get_uuid_string()
        self.deviceItemData.labelReadonly = True
        self.tree.SetItemData(self._rootFeatureItem, self.deviceItemData)
        self.tree.SetItemImage(self._rootFeatureItem, self._iconRepo.featureIcon, wx.TreeItemIcon_Normal)
        self._itemMap.update({self.deviceItemData.uuid: self._rootFeatureItem})

        self._deviceStateItem = self.tree.AppendItem(self._rootFeatureItem, "State")
        self.deviceStateItemData = StandardItemData()
        self.deviceStateItemData.role = EnumItemRole.DEV_FEATURE_STATE
        self.deviceStateItemData.uuid = util_get_uuid_string()
        self.deviceStateItemData.labelReadonly = True
        self.tree.SetItemData(self._deviceStateItem, self.deviceStateItemData)
        self.tree.SetItemImage(self._deviceStateItem, self._iconRepo.stateIcon, wx.TreeItemIcon_Normal)
        self._itemMap.update({self.deviceStateItemData.uuid: self._deviceStateItem})

        self._deviceEvtItem = self.tree.AppendItem(self._rootFeatureItem, "Events")
        self._deviceEvtItemData = StandardItemData()
        self._deviceEvtItemData.role = EnumItemRole.DEV_FEATURE_EVENT
        self._deviceEvtItemData.uuid = util_get_uuid_string()
        self._deviceEvtItemData.labelReadonly = True
        self.tree.SetItemData(self._deviceEvtItem, self._deviceEvtItemData)
        self.tree.SetItemImage(self._deviceEvtItem, self._iconRepo.eventIcon, wx.TreeItemIcon_Normal)
        self._itemMap.update({self._deviceEvtItemData.uuid: self._deviceEvtItem})

        self._userFeatureItem = self.tree.AppendItem(self._modelItem, "User")
        self.userFeatureItemData = StandardItemData()
        self.userFeatureItemData.role = EnumItemRole.USER_FEATURE
        self.userFeatureItemData.uuid = util_get_uuid_string()
        self.userFeatureItemData.labelReadonly = True
        self.tree.SetItemData(self._userFeatureItem, self.userFeatureItemData)
        self.tree.SetItemImage(self._userFeatureItem, self._iconRepo.libIcon, wx.TreeItemIcon_Normal)
        self._itemMap.update({self.userFeatureItemData.uuid: self._userFeatureItem})

        # for i in range(10):
        #     self._add_user_feature('userFe%s' % i)

        self.tree.Expand(self.root)
        self.tree.Expand(self._modelItem)
        self.tree.Expand(self._rackItem)
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

    def serialize(self):
        _d = dict()
        _d.update({'uuid': self.uuid, 'role': self.role})
        _d.update({'model':
                       {'root': {'data': self.deviceItemData,
                                 'text': self.tree.GetItemText(self._rootFeatureItem),
                                 'state': self.deviceStateItemData,
                                 'event': self._deviceEvtItemData},
                        'user': {'data': self.userFeatureItemData,
                                 'text': self.tree.GetItemText(self._userFeatureItem),
                                 'children': list()}},
                   'rack':
                       {'sessions': {'text': self.tree.GetItemText(self._sessions_item),
                                     'data': self.sessionsItemData,
                                     'children': list()},
                        'scripts': {'text': self.tree.GetItemText(self._scripts_item),
                                    'data': self.scriptsItemData,
                                    'children': list()}}})
        # serialize the user features
        _item, _cookie = self.tree.GetFirstChild(self._userFeatureItem)
        while _item.IsOk():
            _state_item, _ = self.tree.GetFirstChild(_item)
            _evt_item, _ = self.tree.GetNextChild(self._userFeatureItem, _)
            _resolver_item, _ = self.tree.GetNextChild(self._userFeatureItem, _)
            _d['model']['user']['children'].append({'data': self.tree.GetItemData(_item),
                                                    'text': self.tree.GetItemText(_item),
                                                    'state': self.tree.GetItemData(_state_item),
                                                    'event': self.tree.GetItemData(_evt_item),
                                                    'resolver': self.tree.GetItemData(_resolver_item)})
            _item, _cookie = self.tree.GetNextChild(self._userFeatureItem, _cookie)
        return _d

    def deserialize(self, data):
        if hasattr(data, 'model'):
            _model = data.model
            _root = _model['root']
            _user = _model['user']
            _user_children = _model['user']['children']
            _root_item_data = _root['data']
            _root_state_data = _root['state']
            _root_evt_data = _root['event']
            self.tree.SetItemText(self._rootFeatureItem, _root['text'])
            self.tree.SetItemData(self._rootFeatureItem, _root_item_data)
            self.tree.SetItemData(self._deviceStateItem, _root_state_data)
            self.tree.SetItemData(self._deviceEvtItem, _root_evt_data)
            self.deviceItemData = _root_item_data
            self.deviceStateItemData = _root_state_data
            self._deviceEvtItemData = _root_evt_data

            self._itemMap.update({_root_item_data.uuid: self._rootFeatureItem})
            self._itemMap.update({_root_state_data.uuid: self._deviceStateItem})
            self._itemMap.update({_root_evt_data.uuid: self._deviceEvtItem})
            # handling the user feature
            self.tree.SetItemText(self._userFeatureItem, _user['text'])
            self.tree.SetItemData(self._userFeatureItem, _user['data'])
            for x in _user_children:
                _x_text, _x_data, _x_state, _x_event, _x_resolver = x['text'], x['data'], x['state'], x['event'], x[
                    'resolver']
                self.add_user_feature(_x_text, _x_data, _x_state, _x_event, _x_resolver)

        if hasattr(data, 'rack'):
            _sessions = data.rack['sessions']
            _scripts = data.rack['scripts']
            self.tree.SetItemData(self._sessions_item, _sessions['data'])
            self.tree.SetItemData(self._scripts_item, _scripts['data'])

    def get_text_by_uuid(self, uuid):
        if uuid in self._itemMap:
            _item = self._itemMap[uuid]
            return self.tree.GetItemText(_item)
        else:
            return None

    def get_feature_text_by_uuid(self, uuid):
        if uuid in self._itemMap:
            _item = self._itemMap[uuid]
            _data = self.tree.GetItemData(_item)
            if _data.role in [EnumItemRole.USER_FEATURE_STATE,
                              EnumItemRole.USER_FEATURE_EVENT,
                              EnumItemRole.DEV_FEATURE_STATE,
                              EnumItemRole.DEV_FEATURE_EVENT]:
                _parent_item = self.tree.GetItemParent(_item)
                return self.tree.GetItemText(_parent_item)
        return None

    def get_item_by_text(self, search_text, root_item):
        _item, _cookie = self.tree.GetFirstChild(root_item)
        while _item.IsOk():
            _text = self.tree.GetItemText(_item)
            if _text.lower() == search_text.lower():
                return _item
            if self.tree.ItemHasChildren(_item):
                _match = self.get_item_by_text(search_text, _item)
                if _match is None:
                    return None
                elif _match.IsOk():
                    return _match
            _item, _cookie = self.tree.GetNextChild(root_item, _cookie)
        return None

    def is_uf_name_is_exist(self, name):
        _item = self.get_item_by_text(name, self._userFeatureItem)
        return _item is not None

    def find_event_sibling_uuid_of(self, uuid):
        # fixme: next version, store association in Itemdata
        _item = self._itemMap.get(uuid)
        if _item is None:
            return None
        _item_parent = self.tree.GetItemParent(_item)
        if _item_parent is None:
            return None
        _gen_items = util_wx_tree_walk_branches(self.tree, _item_parent)
        for x in _gen_items:
            _item_data = self.tree.GetItemData(x)
            if _item_data.role in [EnumItemRole.USER_FEATURE_EVENT, EnumItemRole.DEV_FEATURE_EVENT]:
                return _item_data.uuid
        return None

    def find_state_sibling_uuid_of(self, uuid):
        # fixme: next version, store association in Itemdata
        _item = self._itemMap.get(uuid)
        if _item is None:
            return None
        _item_parent = self.tree.GetItemParent(_item)
        if _item_parent is None:
            return None
        _gen_items = util_wx_tree_walk_branches(self.tree, _item_parent)
        for x in _gen_items:
            _item_data = self.tree.GetItemData(x)
            if _item_data.role in [EnumItemRole.USER_FEATURE_STATE]:
                return _item_data.uuid
        return None

    def add_user_feature(self, name, item_data=None, state_data=None, evt_data=None, resolver_data=None):
        _userFeatureItem = self.tree.AppendItem(self._userFeatureItem, name)
        if item_data is not None:
            item_data.role = EnumItemRole.USER_FEATURE_ITEM
            _userFeatureItemData = item_data
        else:
            _userFeatureItemData = StandardItemData()
            _userFeatureItemData.role = EnumItemRole.USER_FEATURE_ITEM
            _userFeatureItemData.uuid = util_get_uuid_string()
            _userFeatureItemData.labelReadonly = False
        self.tree.SetItemData(_userFeatureItem, _userFeatureItemData)
        self.tree.SetItemImage(_userFeatureItem, self._iconRepo.fileIcon, wx.TreeItemIcon_Normal)

        _userFeatureStateItem = self.tree.AppendItem(_userFeatureItem, 'State')
        if state_data is not None:
            _userFeatureStateData = state_data
            state_data.role = EnumItemRole.USER_FEATURE_STATE
        else:
            _userFeatureStateData = StandardItemData()
            _userFeatureStateData.role = EnumItemRole.USER_FEATURE_STATE
            _userFeatureStateData.uuid = util_get_uuid_string()
            _userFeatureStateData.labelReadonly = True
        self.tree.SetItemData(_userFeatureStateItem, _userFeatureStateData)
        self.tree.SetItemImage(_userFeatureStateItem, self._iconRepo.stateIcon, wx.TreeItemIcon_Normal)

        _userFeatureEventItem = self.tree.AppendItem(_userFeatureItem, 'Event')
        if evt_data is not None:
            _userFeatureEventData = evt_data
            evt_data.role = EnumItemRole.USER_FEATURE_EVENT
        else:
            _userFeatureEventData = StandardItemData()
            _userFeatureEventData.role = EnumItemRole.USER_FEATURE_EVENT
            _userFeatureEventData.uuid = util_get_uuid_string()
            _userFeatureEventData.labelReadonly = True
        self.tree.SetItemData(_userFeatureEventItem, _userFeatureEventData)
        self.tree.SetItemImage(_userFeatureEventItem, self._iconRepo.eventIcon, wx.TreeItemIcon_Normal)

        _userFeatureResolverItem = self.tree.AppendItem(_userFeatureItem, 'Resolver')
        if resolver_data is not None:
            _userFeatureResolverData = resolver_data
            resolver_data.role = EnumItemRole.USER_FEATURE_RESOLVER
        else:
            _userFeatureResolverData = StandardItemData()
            _userFeatureResolverData.role = EnumItemRole.USER_FEATURE_RESOLVER
            _userFeatureResolverData.uuid = util_get_uuid_string()
            _userFeatureResolverData.labelReadonly = True
        self.tree.SetItemData(_userFeatureResolverItem, _userFeatureResolverData)
        self.tree.SetItemImage(_userFeatureResolverItem, self._iconRepo.keyIcon, wx.TreeItemIcon_Normal)

        self._itemMap.update({_userFeatureItemData.uuid: _userFeatureItem})
        self._itemMap.update({_userFeatureStateData.uuid: _userFeatureStateItem})
        self._itemMap.update({_userFeatureEventData.uuid: _userFeatureEventItem})
        self._itemMap.update({_userFeatureResolverData.uuid: _userFeatureResolverItem})
        return _userFeatureItemData.uuid, _userFeatureStateData.uuid, _userFeatureEventData.uuid, _userFeatureResolverData.uuid

    def get_root_state_uuid(self):
        return self.deviceStateItemData.uuid

    def get_root_event_uuid(self):
        return self._deviceEvtItemData.uuid

    def on_cm_new_user_feature(self, evt):
        pub.sendMessage(EnumAppSignals.sigV2VProjectNewUserFeature.value)

    def on_cm_add_user_feature(self, evt):
        pub.sendMessage(EnumAppSignals.sigV2VProjectAddUserFeature.value)

    def on_cm_save_user_feature_as_lib(self, evt):
        _item = self.tree.GetSelection()
        if _item is not None:
            _uuid = self.tree.GetItemData(_item).uuid
            _state_item, _evt_item = self.get_user_feature_children(_item)
            _state_uuid = self.tree.GetItemData(_state_item).uuid
            _evt_uuid = self.tree.GetItemData(_evt_item).uuid
            pub.sendMessage(EnumAppSignals.sigV2VProjectSaveUserFeatureAsLib.value, state_uuid=_state_uuid,
                            event_uuid=_evt_uuid)

    def get_user_feature_children(self, item):
        _state_item = self.tree.GetFirstChild(item)
        _evt_item = self.tree.GetLastChild(item)
        return _state_item, _evt_item

    def on_cm_clear_user_feature(self, evt):
        pass

    def on_item_get_tooltip(self, evt):
        _item = evt.GetItem()
        _item_data = self.tree.GetItemData(_item)
        if isinstance(_item_data, StandardItemData):
            if _item_data.tooltip is not None:
                evt.SetToolTip(_item_data.tooltip)

    def on_f2_pressed(self, evt):
        _selected = self.tree.GetSelection()
        if _selected:
            _data = self.tree.GetItemData(_selected)
            if _data.labelReadonly is not None:
                self.on_rename_label() if _data.labelReadonly else None
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
            elif _role == EnumItemRole.USER_FEATURE:
                self._userFeatureCtxMenu.show()
            elif _role == EnumItemRole.USER_FEATURE_ITEM:
                self._userFeatureItemCtxMenu.show()
            elif _role == EnumItemRole.USER_FEATURE_STATE:
                self._userFeatureStateCtxMenu.show()
            elif _role == EnumItemRole.USER_FEATURE_EVENT:
                self._userFeatureEvtCtxMenu.show()

    def on_size(self, event):
        self.tree.SetSize(0, 0, *self.GetClientSize())

    def init_project(self, project):
        self.tree.SetItemText(self.root, project.name)

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
        # pub.sendMessage(EnumAppSignals.sigV2MRackItemSelectChanged,sender=self,data=_data)
        event.Skip()

    def on_item_activate(self, event):
        # double click fire this event only
        _item = event.GetItem()
        _data = self.tree.GetItemData(_item)
        if hasattr(_data, 'uuid'):
            pub.sendMessage(EnumAppSignals.sigV2VModelTreeItemDoubleClicked.value, uuid=_data.uuid)

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

    def ____on_add_user_feature(self, evt, flag):
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

    def get_item_role_by_uuid(self, uuid):
        _item = self._itemMap.get(uuid)
        if _item is not None:
            _ud = self.tree.GetItemData(_item)
            if hasattr(_ud, 'role'):
                return _ud.role
            return None
        else:
            return None

    def get_item_name_by_uuid(self, uuid):
        _item = self._itemMap.get(uuid)
        if _item is not None:
            return self.tree.GetItemText(_item)
        else:
            return None

    def get_item_path_by_uuid(self, uuid):
        _item = self._itemMap.get(uuid)
        if _item is not None:
            _path = list()
            _path.append(self.tree.GetItemText(_item))
            _parent = self.tree.GetItemParent(_item)
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

    # def set_session_item_in_state_run(self, uuid):
    #     _session_item = self._itemMap.get(uuid)
    #     if _session_item is None:
    #         return
    #     _item_data = self.tree.GetItemData(_session_item)
    #     _item_data.tooltip = 'IS STARTET'
    #     _img = getattr(self._iconRepo, 'session%sIconActive' % _item_data.flag)
    #     self.tree.SetItemImage(_session_item, _img, wx.TreeItemIcon_Normal)
    #
    # def set_session_item_in_state_stop(self, uuid):
    #     _session_item = self._itemMap.get(uuid)
    #     if _session_item is None:
    #         return
    #     _item_data = self.tree.GetItemData(_session_item)
    #     _item_data.tooltip = 'IS STOPPED'
    #     _img = getattr(self._iconRepo, 'session%sIconDefault' % _item_data.flag)
    #     self.tree.SetItemImage(_session_item, _img, wx.TreeItemIcon_Normal)
    #
    # def remove_session_item_nodes(self, uuid):
    #     _session_item = self._itemMap.get(uuid)
    #     _del_slot = []
    #     _del_ep = []
    #     for x in helper.util_wx_tree_walk_branches(self.tree, _session_item):
    #         _data = self.tree.GetItemData(x)
    #         if hasattr(_data, 'role'):
    #             if _data.role == EnumItemRole.SLOT:
    #                 _del_slot.append(x)
    #                 self._itemMap.pop(_data.uuid)
    #                 for y in helper.util_wx_tree_walk_branches(self.tree, x):
    #                     _data2 = self.tree.GetItemData(y)
    #                     if _data2.role == EnumItemRole.ENDPOINT:
    #                         _del_ep.append(_data2.uuid)
    #                         self._itemMap.pop(_data2.uuid)
    #     for x in _del_slot:
    #         self.tree.Delete(x)
    #     return _del_ep
    #
    # def _update_slot_ep_node(self, parent_node, parent_uuid, slot_path, label, flag):
    #     _ep_data = StandardItemData()
    #     _ep_data.uuid = helper.util_get_uuid_string()
    #     _ep_data.role = EnumItemRole.ENDPOINT
    #     _ep_data.flag = flag
    #     _ep_data.labelReadonly = True
    #     _ep_data.parentUUID = parent_uuid
    #     _ep_data.slotPath = slot_path
    #     _ep_icon = getattr(self._iconRepo, 'slot%sIcon' % _ep_data.flag)
    #     _ep_item = self.tree.AppendItem(parent_node, label)
    #     self.tree.SetItemImage(_ep_item, _ep_icon, wx.TreeItemIcon_Normal)
    #     self.tree.SetItemData(_ep_item, _ep_data)
    #     self._itemMap.update({_ep_data.uuid: _ep_item})
    #     return _ep_data
    #
    # def update_session_item_nodes(self, uuid, nodes, endpoints):
    #     _item = self._itemMap.get(uuid)
    #     _ep_items_data = dict()
    #     if _item is None:
    #         return _ep_items_data
    #     for slot_path, slot_inst in nodes.items():
    #         _name = slot_inst.p_name
    #         _slot_path = slot_inst.p_slot_path
    #         _slot_item = self.tree.AppendItem(_item, '#%s %s' % (slot_inst.p_slot_nr, _name))
    #         _slot_item_data = StandardItemData()
    #         _slot_item_data.role = EnumItemRole.SLOT
    #         _slot_item_data.uuid = helper.util_get_uuid_string()
    #         _slot_item_data.flag = _slot_path
    #         _slot_item_data.labelReadonly = False
    #         self._itemMap.update({_slot_item_data.uuid: _slot_item})
    #         self.tree.SetItemData(_slot_item, _slot_item_data)
    #         _bus_family = slot_inst.p_bus_family
    #         _prod_family = slot_inst.p_family
    #         _is_safety = any([x in _prod_family for x in ['PS', 'SBT', 'SBTV3']])
    #         if _is_safety:
    #             _slot_icon = getattr(self._iconRepo, 'slot%sFSIcon' % _bus_family)
    #         else:
    #             _slot_icon = getattr(self._iconRepo, 'slot%sIcon' % _bus_family)
    #         self.tree.SetItemImage(_slot_item, _slot_icon, wx.TreeItemIcon_Normal)
    #         # guess endpoints
    #         _ep_io_key = '%s-%s' % (_slot_path, EPTypeEnum.EP_IO)
    #         _ep_info_key = '%s-%s' % (_slot_path, EPTypeEnum.EP_INFO)
    #         _ep_fcom_key = '%s-%s' % (_slot_path, EPTypeEnum.EP_FCOM)
    #         _ep_diag_key = '%s-%s' % (_slot_path, EPTypeEnum.EP_DIAG)
    #         _ep_param_key = '%s-%s' % (_slot_path, EPTypeEnum.EP_PARAM)
    #         _ep_io = endpoints.get(_ep_io_key)
    #         _ep_info = endpoints.get(_ep_info_key)
    #         _ep_fcom = endpoints.get(_ep_fcom_key)
    #         _ep_diag = endpoints.get(_ep_diag_key)
    #         _ep_param = endpoints.get(_ep_param_key)
    #         if _ep_io:
    #             _ep_data = self._update_slot_ep_node(_slot_item, uuid, slot_path,
    #                                                  '%s' % EPTypeEnum.EP_IO, EPTypeEnum.EP_IO)
    #             _ep_items_data.update({_ep_data.uuid: _ep_data})
    #         if _ep_info:
    #             _ep_data = self._update_slot_ep_node(_slot_item, uuid, slot_path,
    #                                                  '%s' % EPTypeEnum.EP_INFO, EPTypeEnum.EP_INFO)
    #             _ep_items_data.update({_ep_data.uuid: _ep_data})
    #         if _ep_fcom:
    #             _ep_data = self._update_slot_ep_node(_slot_item, uuid, slot_path,
    #                                                  '%s' % EPTypeEnum.EP_FCOM, EPTypeEnum.EP_FCOM)
    #             _ep_items_data.update({_ep_data.uuid: _ep_data})
    #         if _ep_diag:
    #             _ep_data = self._update_slot_ep_node(_slot_item, uuid, slot_path,
    #                                                  '%s' % EPTypeEnum.EP_DIAG, EPTypeEnum.EP_DIAG)
    #             _ep_items_data.update({_ep_data.uuid: _ep_data})
    #         if _ep_param:
    #             _ep_data = self._update_slot_ep_node(_slot_item, uuid, slot_path,
    #                                                  '%s' % EPTypeEnum.EP_PARAM, EPTypeEnum.EP_PARAM)
    #             _ep_items_data.update({_ep_data.uuid: _ep_data})
    #     return _ep_items_data
    #
    # def set_session_item_in_state_error(self, uuid, err_str):
    #     _session_item = self._itemMap.get(uuid)
    #     if _session_item is None:
    #         return
    #     _item_data = self.tree.GetItemData(_session_item)
    #     _item_data.tooltip = 'Error: %s' % err_str
    #     self.tree.SetItemImage(_session_item, self._iconRepo.exclamationIcon, wx.TreeItemIcon_Normal)
