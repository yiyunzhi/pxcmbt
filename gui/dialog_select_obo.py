# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : Test Control System
# Sourcefile(s) : dialog_select_obo.py
# ------------------------------------------------------------------------------
#
# File          : dialog_select_obo.py
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
from .panel_header import HeaderPanel
from .panel_user_feature_selector import FeatureSelectorPanel

#
# class SelectOboDialog(wx.Dialog):
#     def __init__(self, project, parent, group='USER', wx_id=wx.ID_ANY, title='SelectFeature', size=wx.DefaultSize,
#                  pos=wx.DefaultPosition,
#                  style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name='SelectFeatureDialog'):
#         wx.Dialog.__init__(self, parent, wx_id, title, pos, size, style, name)
#         self.mainSizer = wx.BoxSizer(wx.VERTICAL)
#         self.project = project
#         self.selectorPanel = FeatureSelectorPanel(self.project, self, group=group)
#         self.group = group
#         self.SetMinSize((360, 480))
#         # layout
#         self._btnSizer = wx.StdDialogButtonSizer()
#         _btn_ok = wx.Button(self, wx.ID_OK)
#         _btn_ok.SetHelpText("The OK button completes the dialog")
#         _btn_ok.SetDefault()
#         self._btnSizer.AddButton(_btn_ok)
#
#         _btn_cancel = wx.Button(self, wx.ID_CANCEL)
#         _btn_cancel.SetHelpText("The Cancel button cancels the dialog. (Cool, huh?)")
#         self._btnSizer.AddButton(_btn_cancel)
#         self._btnSizer.Realize()
#         # bind event
#
#         # layout
#         self.mainSizer.Add(HeaderPanel('Select User Feature', 'Select User Feature', parent=self), 0,
#                            wx.EXPAND | wx.ALL, 5)
#         self.mainSizer.Add(self.selectorPanel, 1, wx.EXPAND | wx.ALL, 5)
#         self.mainSizer.Add(self._btnSizer, 0, wx.ALL, 5)
#         self.SetSizer(self.mainSizer)
#         self.Layout()
#         self.Fit()
#
#     def get_selected_obo(self):
#         return self.selectorPanel.currentFeature
