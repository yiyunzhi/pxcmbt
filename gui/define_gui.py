# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : define_gui.py
# ------------------------------------------------------------------------------
#
# File          : define_gui.py
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

"""
wx.ART_ERROR
wx.ART_GOTO_LAST (since 2.9.2)
wx.ART_FILE_SAVE_AS
wx.ART_QUESTION
wx.ART_PRINT
wx.ART_DELETE
wx.ART_WARNING
wx.ART_HELP
wx.ART_COPY
wx.ART_INFORMATION
wx.ART_TIP
wx.ART_CUT
wx.ART_ADD_BOOKMARK
wx.ART_REPORT_VIEW
wx.ART_PASTE
wx.ART_DEL_BOOKMARK
wx.ART_LIST_VIEW
wx.ART_UNDO
wx.ART_HELP_SIDE_PANEL
wx.ART_NEW_DIR
wx.ART_REDO
wx.ART_HELP_SETTINGS
wx.ART_FOLDER
wx.ART_PLUS (since 2.9.2)
wx.ART_HELP_BOOK
wx.ART_FOLDER_OPEN
wx.ART_MINUS (since 2.9.2)
wx.ART_HELP_FOLDER
wx.ART_GO_DIR_UP
wx.ART_CLOSE
wx.ART_HELP_PAGE
wx.ART_EXECUTABLE_FILE
wx.ART_QUIT
wx.ART_GO_BACK
wx.ART_NORMAL_FILE
wx.ART_FIND
wx.ART_GO_FORWARD
wx.ART_TICK_MARK
wx.ART_FIND_AND_REPLACE
wx.ART_GO_UP
wx.ART_CROSS_MARK
wx.ART_HARDDISK
wx.ART_GO_DOWN
wx.ART_MISSING_IMAGE
wx.ART_FLOPPY
wx.ART_GO_TO_PARENT
wx.ART_NEW
wx.ART_CDROM
wx.ART_GO_HOME
wx.ART_FILE_OPEN
wx.ART_GOTO_FIRST (since 2.9.2)
wx.ART_FILE_SAVE
"""
import os

ROOT_PATH = os.getcwd()

_ = wx.GetTranslation
PATH_GUI_IMAGES = ROOT_PATH + '\\gui\\images'


class EnumCanvasToolbarMode:
    POINTER = 0
    STATE = 1
    SUB_STATE = 2
    INIT_STATE = 3
    FINAL_STATE = 4
    CONNECTION = 5
    NOTE = 6


class EnumMenuID:
    ID_CreateTree = wx.ID_HIGHEST + 1
    ID_CreateGrid = ID_CreateTree + 1
    ID_CreateText = ID_CreateTree + 2
    ID_CreateHTML = ID_CreateTree + 3


CANVAS_MAX_W = 2000
CANVAS_MAX_H = 2000
CANVAS_HIT_RADIUS = 5

WIRE_COLOUR = 'black'
WIRE_THICKNESS = 2

PORT_MARGIN = 6
PORT_RADIUS = 4
PORT_HIT_RADIUS = 10
PORT_SPACING = 20
PORT_TYPE_IN = 0
PORT_TYPE_OUT = 1
PORT_TITLE_MARGIN = 20

NODE_TITLE_INSET_X = 5
NODE_TITLE_INSET_Y = 1
NODE_ROUND_CORNER_RADIUS = 8
