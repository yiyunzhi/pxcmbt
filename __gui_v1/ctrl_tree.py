# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : ctrl_tree.py
# ------------------------------------------------------------------------------
#
# File          : ctrl_tree.py
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


class GenericTreeCtrl(wx.TreeCtrl):
    def __init__(self, parent, wx_id, pos, size, style):
        wx.TreeCtrl.__init__(self, parent, wx_id, pos, size, style)

    def OnCompareItems(self, item1, item2):
        t1 = self.GetItemText(item1)
        t2 = self.GetItemText(item2)
        if t1 < t2: return -1
        if t1 == t2: return 0
        return 1
