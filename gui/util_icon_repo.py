# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : Test Control System
# Sourcefile(s) : util_icon_repo.py
# ------------------------------------------------------------------------------
#
# File          : util_icon_repo.py
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
from .define_gui import PATH_GUI_IMAGES
from application.class_base import singleton


@singleton
class UtilIconRepo:
    def __init__(self):
        self._icon_size = (16, 16)
        self._image_list = wx.ImageList(*self._icon_size)
        self.fileIcon = self._image_list.Add(
            wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, self._icon_size))
        self.invalidIcon = self._image_list.Add(
            wx.ArtProvider.GetBitmap(wx.ART_MISSING_IMAGE, wx.ART_OTHER, self._icon_size))
        self.signalsIcon = self._image_list.Add(
            wx.ArtProvider.GetBitmap(wx.ART_LIST_VIEW, wx.ART_OTHER, self._icon_size))
        self.folderIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_folder.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.successIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_success.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.errorIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_error.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.warningIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_warning.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.sandglassIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_sandglass.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.pinIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_pin.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.cubeIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_cube.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.binaryIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_binary.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.ledIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_led.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.alarmTaIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_alarm_ta.png', wx.BITMAP_TYPE_PNG).Scale(
                *self._icon_size).ConvertToBitmap())
        self.eyeIcon = self._image_list.Add(
            wx.Image(PATH_GUI_IMAGES + '\\icon_eye.png', wx.BITMAP_TYPE_PNG).Scale(
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
