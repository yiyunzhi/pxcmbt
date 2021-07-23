# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : menu_context_menu.py
# ------------------------------------------------------------------------------
#
# File          : menu_context_menu.py
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


class GuiContextMenu:
    def __init__(self, name, parent):
        assert hasattr(parent, 'Bind'), 'Invalid parent, attribute Bind required'
        self.name = name
        self.parent = parent

    def show(self):
        raise NotImplementedError('must be implemented')


class GuiModelContextMenu(GuiContextMenu):
    def __init__(self, parent):
        super(GuiModelContextMenu, self).__init__(name='cmModel', parent=parent)
        # self.popupNewDDISessionID = wx.NewIdRef()
        # self.popupNewPNSessionID = wx.NewIdRef()
        # self.popupNewVISASessionID = wx.NewIdRef()
        # self.popupCfgSigID = wx.NewIdRef()
        # self.popupCfgFuncID = wx.NewIdRef()
        # self.popupNewScriptID = wx.NewIdRef()
        # self.parent.Bind(wx.EVT_MENU, self.parent.on_new_ddi_session, id=self.popupNewDDISessionID)
        # self.parent.Bind(wx.EVT_MENU, self.parent.on_new_pn_session, id=self.popupNewPNSessionID)
        # self.parent.Bind(wx.EVT_MENU, self.parent.on_new_visa_session, id=self.popupNewVISASessionID)
        # self.parent.Bind(wx.EVT_MENU, self.parent.on_cfg_signal, id=self.popupCfgSigID)
        # self.parent.Bind(wx.EVT_MENU, self.parent.on_cfg_function, id=self.popupCfgFuncID)
        # self.parent.Bind(wx.EVT_MENU, self.parent.on_new_script, id=self.popupNewScriptID)

    def show(self):
        # make a menu
        _menu = wx.Menu()
        # Show how to put an icon in the menu
        # _item = wx.MenuItem(_menu, self.popupNewDDISessionID, "New DDI Session")
        # bmp = images.Smiles.GetBitmap()
        # item.SetBitmap(bmp)
        # _menu.Append(_item)
        # add some other items
        # _menu.Append(self.popupCfgSigID, "Config Signal")
        # _menu.Append(self.popupCfgFuncID, "Config Function")
        # _menu.Append(self.popupNewDDISessionID, "New DDI Session")
        # _menu.Append(self.popupNewPNSessionID, "New Profinet Session")
        # _menu.Append(self.popupNewVISASessionID, "New VISA Session")
        # _menu.Append(self.popupNewScriptID, "New Script")
        # _menu.AppendSeparator()
        # make a submenu
        # sm = wx.Menu()
        # sm.Append(self.popupID8, "sub item 1")
        # sm.Append(self.popupID9, "sub item 1")
        # _menu.Append(self.popupID7, "Test Submenu", sm)

        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.parent.PopupMenu(_menu)
        _menu.Destroy()


class GuiDeviceFeatureContextMenu(GuiContextMenu):
    def __init__(self, parent):
        super(GuiDeviceFeatureContextMenu, self).__init__(name='cmDeviceFeature', parent=parent)
        self.popupReplaceFeature = wx.NewIdRef()
        self.popupPickUpFeature = wx.NewIdRef()

        self.parent.Bind(wx.EVT_MENU, self.parent.on_replace_root_feature,
                         id=self.popupReplaceFeature)
        self.parent.Bind(wx.EVT_MENU, self.parent.on_cm_add_root_feature,
                         id=self.popupPickUpFeature)

    def show(self):
        # make a menu
        _menu = wx.Menu()
        # Show how to put an icon in the menu
        # _item = wx.MenuItem(_menu, self.popupNewSessionID, "New Session")
        # bmp = images.Smiles.GetBitmap()
        # item.SetBitmap(bmp)
        # _menu.Append(_item)
        # add some other items
        _menu.Append(self.popupPickUpFeature, "ReplaceWith")
        #_menu.Append(self.popupReplaceFeature, "Replace")
        _menu.AppendSeparator()
        # _menu.AppendSeparator()
        # _menu.Append(self.popupStartSessions, "Start All")
        # _menu.Append(self.popupStopSessions, "Stop All")
        # _menu.AppendSeparator()
        # make a submenu
        # sm = wx.Menu()
        # sm.Append(self.popupID8, "sub item 1")
        # sm.Append(self.popupID9, "sub item 1")
        # _menu.Append(self.popupID7, "Test Submenu", sm)

        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.parent.PopupMenu(_menu)
        _menu.Destroy()


class GuiDeviceFeatureStateContextMenu(GuiContextMenu):
    def __init__(self, parent):
        super(GuiDeviceFeatureStateContextMenu, self).__init__(name='cmDeviceFeature', parent=parent)
        self.popupAddUserFeature = wx.NewIdRef()
        self.popupPickUpFeature = wx.NewIdRef()

        # self.parent.Bind(wx.EVT_MENU, lambda evt, flag='': self.parent.on_add_user_feature(evt, flag),
        #                  id=self.popupAddUserFeature)
        # self.parent.Bind(wx.EVT_MENU, lambda evt, flag='': self.parent.on_pick_up_user_feature(evt, flag),
        #                  id=self.popupPickUpFeature)

    def show(self):
        # make a menu
        _menu = wx.Menu()
        # Show how to put an icon in the menu
        # _item = wx.MenuItem(_menu, self.popupNewSessionID, "New Session")
        # bmp = images.Smiles.GetBitmap()
        # item.SetBitmap(bmp)
        # _menu.Append(_item)
        # add some other items
        #_menu.Append(self.popupAddUserFeature, "Add User Feature")
        #_menu.Append(self.popupPickUpFeature, "Pick Up User Feature")
        #_menu.AppendSeparator()
        # _menu.AppendSeparator()
        # _menu.Append(self.popupStartSessions, "Start All")
        # _menu.Append(self.popupStopSessions, "Stop All")
        # _menu.AppendSeparator()
        # make a submenu
        # sm = wx.Menu()
        # sm.Append(self.popupID8, "sub item 1")
        # sm.Append(self.popupID9, "sub item 1")
        # _menu.Append(self.popupID7, "Test Submenu", sm)

        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.parent.PopupMenu(_menu)
        _menu.Destroy()


class GuiDeviceFeatureEvtContextMenu(GuiContextMenu):
    def __init__(self, parent):
        super(GuiDeviceFeatureEvtContextMenu, self).__init__(name='cmDeviceFeature', parent=parent)
        self.popupAddUserFeature = wx.NewIdRef()
        self.popupPickUpFeature = wx.NewIdRef()

        self.parent.Bind(wx.EVT_MENU, lambda evt, flag='': self.parent.on_add_user_feature(evt, flag),
                         id=self.popupAddUserFeature)
        self.parent.Bind(wx.EVT_MENU, lambda evt, flag='': self.parent.on_pick_up_user_feature(evt, flag),
                         id=self.popupPickUpFeature)

    def show(self):
        # make a menu
        _menu = wx.Menu()
        # Show how to put an icon in the menu
        # _item = wx.MenuItem(_menu, self.popupNewSessionID, "New Session")
        # bmp = images.Smiles.GetBitmap()
        # item.SetBitmap(bmp)
        # _menu.Append(_item)
        # add some other items
        # _menu.Append(self.popupAddUserFeature, "Add User Feature")
        # _menu.Append(self.popupPickUpFeature, "Pick Up User Feature")
        # _menu.AppendSeparator()
        # _menu.AppendSeparator()
        # _menu.Append(self.popupStartSessions, "Start All")
        # _menu.Append(self.popupStopSessions, "Stop All")
        # _menu.AppendSeparator()
        # make a submenu
        # sm = wx.Menu()
        # sm.Append(self.popupID8, "sub item 1")
        # sm.Append(self.popupID9, "sub item 1")
        # _menu.Append(self.popupID7, "Test Submenu", sm)

        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.parent.PopupMenu(_menu)
        _menu.Destroy()


class GuiUserFeatureContextMenu(GuiContextMenu):
    def __init__(self, parent):
        super(GuiUserFeatureContextMenu, self).__init__(name='cmUserFeature', parent=parent)
        self.popupNewID = wx.NewIdRef()
        self.popupAddID = wx.NewIdRef()
        self.popupClearID = wx.NewIdRef()
        self.popupStartSession = wx.NewIdRef()
        self.popupStopSession = wx.NewIdRef()
        self.parent.Bind(wx.EVT_MENU, self.parent.on_cm_new_user_feature, id=self.popupNewID)
        self.parent.Bind(wx.EVT_MENU, self.parent.on_cm_add_user_feature, id=self.popupAddID)
        self.parent.Bind(wx.EVT_MENU, self.parent.on_cm_clear_user_feature, id=self.popupClearID)

    def show(self):
        # make a menu
        _menu = wx.Menu()
        # Show how to put an icon in the menu
        _menu.Append(self.popupNewID, "New")
        _menu.Append(self.popupAddID, "Add")
        _menu.AppendSeparator()
        _menu.Append(self.popupClearID, "Clear")
        # make a submenu
        # will be called before PopupMenu returns.
        self.parent.PopupMenu(_menu)
        _menu.Destroy()


class GuiUserFeatureItemContextMenu(GuiContextMenu):
    def __init__(self, parent):
        super(GuiUserFeatureItemContextMenu, self).__init__(name='cmUserFeature', parent=parent)
        self.popupSaveAsLibID = wx.NewIdRef()
        self.popupRenameID = wx.NewIdRef()
        self.popupDeleteID = wx.NewIdRef()
        self.parent.Bind(wx.EVT_MENU, self.parent.on_cm_save_user_feature_as_lib, id=self.popupSaveAsLibID)
        self.parent.Bind(wx.EVT_MENU, self.parent.on_cm_rename_user_feature, id=self.popupRenameID)
        self.parent.Bind(wx.EVT_MENU, self.parent.on_cm_del_user_feature, id=self.popupDeleteID)

    def show(self):
        # make a menu
        _menu = wx.Menu()
        # Show how to put an icon in the menu
        _menu.Append(self.popupSaveAsLibID, "SaveAsLib")
        _menu.Append(self.popupRenameID, "Rename")
        _menu.Append(self.popupDeleteID, "Remove")
        _menu.AppendSeparator()
        # make a submenu
        # will be called before PopupMenu returns.
        self.parent.PopupMenu(_menu)
        _menu.Destroy()


class GuiUserFeatureStateContextMenu(GuiContextMenu):
    def __init__(self, parent):
        super(GuiUserFeatureStateContextMenu, self).__init__(name='cmUserFeatureState', parent=parent)
        self.popupRenameID = wx.NewIdRef()
        self.popupPropID = wx.NewIdRef()
        self.popupStartSession = wx.NewIdRef()
        self.popupStopSession = wx.NewIdRef()
        self.parent.Bind(wx.EVT_MENU, self.parent.on_show_feature_state_property, id=self.popupPropID)

    def show(self):
        # make a menu
        _menu = wx.Menu()
        # Show how to put an icon in the menu
        # _item = wx.MenuItem(_menu, self.popupPropID, "Property")
        # bmp = images.Smiles.GetBitmap()
        # item.SetBitmap(bmp)
        # _menu.Append(_item)
        # add some other items
        _menu.AppendSeparator()
        _menu.Append(self.popupPropID, "Properties")
        # make a submenu
        # will be called before PopupMenu returns.
        self.parent.PopupMenu(_menu)
        _menu.Destroy()


class GuiUserFeatureEvtContextMenu(GuiContextMenu):
    def __init__(self, parent):
        super(GuiUserFeatureEvtContextMenu, self).__init__(name='cmFeatureLib', parent=parent)
        # self.popupReloadID = wx.NewIdRef()
        # self.popupShowDetailID = wx.NewIdRef()
        # self.parent.Bind(wx.EVT_MENU, self.parent.on_reload_feature_lib, id=self.popupReloadID)
        # self.parent.Bind(wx.EVT_MENU, self.parent.on_show_lib_detail, id=self.popupShowDetailID)

    def show(self):
        # make a menu
        _menu = wx.Menu()
        # Show how to put an icon in the menu
        # _item = wx.MenuItem(_menu, self.popupPropID, "Property")
        # bmp = images.Smiles.GetBitmap()
        # item.SetBitmap(bmp)
        # _menu.Append(_item)
        # add some other items
        # _menu.AppendSeparator()
        # _menu.Append(self.popupReloadID, "Reload")
        # _menu.Append(self.popupShowDetailID, "Detail")
        # make a submenu
        # will be called before PopupMenu returns.
        self.parent.PopupMenu(_menu)
        _menu.Destroy()


class GuiStateItemContextMenu(GuiContextMenu):
    def __init__(self, parent):
        super(GuiStateItemContextMenu, self).__init__(name='cmFeatureLib', parent=parent)
        self.popupDeleteID = wx.NewIdRef()
        self.parent.Bind(wx.EVT_MENU, self.parent.on_cm_delete_item, id=self.popupDeleteID)

    def show(self):
        # make a menu
        _menu = wx.Menu()
        # Show how to put an icon in the menu
        # _item = wx.MenuItem(_menu, self.popupPropID, "Property")
        # bmp = images.Smiles.GetBitmap()
        # item.SetBitmap(bmp)
        # _menu.Append(_item)
        # add some other items
        _menu.Append(self.popupDeleteID, "Delete")
        _menu.AppendSeparator()
        # make a submenu
        # will be called before PopupMenu returns.
        self.parent.PopupMenu(_menu)
        _menu.Destroy()
