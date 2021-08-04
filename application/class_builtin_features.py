import os
from .class_app_file_io import *


class BuiltInFeature:
    def __init__(self, name):
        self.name = name
        self.infFile = None
        self.evtFile = None
        self.stcFile = None
        self.oboFile = None
        self.overviewImage = None

    def get_path_file_name(self, file_path):
        _path, _base_name = os.path.split(file_path)
        return _path, _base_name

    def get_inf_file_content(self):
        if self.infFile is not None:
            _io = ApplicationInfFileIO(*self.get_path_file_name(self.infFile))
            _io.read()
            return _io

    def get_evt_file_content(self):
        if self.evtFile is not None:
            _io = ApplicationEvtFileIO(*self.get_path_file_name(self.evtFile))
            _io.read()
            return _io

    def get_stc_file_content(self):
        if self.stcFile is not None:
            _io = ApplicationStcFileIO(*self.get_path_file_name(self.stcFile))
            _io.read()
            return _io

    def get_obo_file_content(self):
        if self.oboFile is not None:
            _io = ApplicationOboFileIO(*self.get_path_file_name(self.oboFile))
            _io.read()
            return _io
