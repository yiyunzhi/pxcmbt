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


class EnumCanvasStyle:
    # brief Allow multiselection box
    STYLE_MULTI_SELECTION = 1
    # Allow shapes size change done via the multiselection box
    STYLE_MULTI_SIZE_CHANGE = 2
    # Show grid
    STYLE_SHOW_GRID = 4
    # Use grid
    STYLE_USE_GRID = 8
    # Enable Drag & Drop operations
    STYLE_DND = 16
    # Enable Undo/Redo operations
    STYLE_UNDOREDO = 32
    #  Enable the clipboard
    STYLE_CLIPBOARD = 64
    # Enable mouse hovering
    STYLE_HOVERING = 128
    # Enable highligting of shapes able to accept dragged shape(s)
    STYLE_HIGHLIGHTING = 256
    # Use gradient color for the canvas background
    STYLE_GRADIENT_BACKGROUND = 512
    # Print also canvas background
    STYLE_PRINT_BACKGROUND = 1024
    # Process mouse wheel by the canvas (canvas scale will be changed)
    STYLE_PROCESS_MOUSEWHEEL = 2048
    STYLE_DEFAULT = (STYLE_MULTI_SELECTION
                     | STYLE_MULTI_SIZE_CHANGE
                     | STYLE_DND
                     | STYLE_GRADIENT_BACKGROUND
                     | STYLE_SHOW_GRID
                     | STYLE_UNDOREDO
                     | STYLE_CLIPBOARD
                     | STYLE_HOVERING
                     | STYLE_HIGHLIGHTING)


class EnumShapeConnectionStyle:
    ANYWHERE = 1
    ONLY_ON_PORT = 2
    NONE = -1


class EnumShapeStyle:
    # Interactive parent change is allowed
    REPARENT = 1
    # Interactive position change is allowed
    REPOSITION = 2
    # Interactive size change is allowed
    RESIZE = 4
    # Shape is highlighted at mouse hovering
    HOVERING = 8
    # Shape is highlighted at shape dragging
    HIGHLIGHTING = 16
    # Shape is always inside its parent
    ALWAYS_INSIDE = 32
    # User data is destroyed at the shape deletion
    DELETE_USER_DATA = 64
    # The DEL key is processed by the shape (not by the shape canvas)
    PROCESS_K_DEL = 128
    # Show handles if the shape is selected
    SHOW_HANDLES = 256
    # Show shadow under the shape
    SHOW_SHADOW = 512
    # Lock children relative position if the parent is resized
    LOCK_CHILDREN = 1024
    # Emit events (catchable in shape canvas)
    EMIT_EVENTS = 2048
    # Propagate mouse dragging event to parent shape
    PROPAGATE_DRAGGING = 4096
    # Propagate selection to parent shape
    # (it means this shape cannot be selected because its focus is redirected to its parent shape)
    PROPAGATE_SELECTION = 8192
    # Propagate interactive connection request to parent shape
    # (it means this shape cannot be connected interactively because this feature is redirected to its parent shape)
    PROPAGATE_INTERACTIVE_CONNECTION = 16384
    # Do no resize the shape to fit its children automatically
    NO_FIT_TO_CHILDREN = 32768
    # Do no resize the shape to fit its children automatically
    PROPAGATE_HOVERING = 65536
    # Propagate hovering to parent
    PROPAGATE_HIGHLIGHTING = 131072
    STYLE_DEFAULT = (REPARENT | REPOSITION | RESIZE | HOVERING
                     | HIGHLIGHTING | SHOW_HANDLES | ALWAYS_INSIDE | DELETE_USER_DATA)


WX_GUI_GRID_COL_LABEL_HEIGHT = 20
