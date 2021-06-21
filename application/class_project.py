import os
import yaml
from .class_app_setting import APP_SETTING
from .class_app_file_io import *


class Project:
    def __init__(self, name):
        self.name = name
        self.workspacePath = APP_SETTING.projectPath
        self.path = os.path.join(APP_SETTING.projectPath, name)
        self.modelPath = os.path.join(self.path, 'model')
        self.rackPath = os.path.join(self.path, 'rack')
        self.modelRootUuid = '00000000000000000000000000000000'
        self._evtFileExt = '.evt'
        self._projFileExt = '.proj'
        self.projectEntryFilePath = os.path.join(self.path, self.name + self._projFileExt)
        self.savedState = False

    def set_project_workspace_path(self, path):
        self.path = os.path.join(path, self.name)
        self.modelPath = os.path.join(self.path, 'model')
        self.rackPath = os.path.join(self.path, 'rack')
        self.projectEntryFilePath = os.path.join(self.path, self.name + self._projFileExt)

    def get_project_data(self):
        pass

    def create_new_project(self):
        os.makedirs(self.path)
        os.makedirs(self.modelPath)
        os.makedirs(self.rackPath)
        self.create_project_entry_file()

    def create_project_entry_file(self):
        os.makedirs(self.projectEntryFilePath)

    def get_project_entry_file(self):
        _f = None
        with open(self.projectEntryFilePath, 'r', encoding='utf-8') as f:
            pass
        return _f

    def get_event_data(self, role, uuid):
        _dummy_evt_name = 'abcdefghijk'
        _file_name = _dummy_evt_name + self._evtFileExt
        _path = os.path.join(self.modelPath, _file_name)
        _data = None
        with open(_path, 'r', encoding='utf-8') as f:
            _data = yaml.load(f, yaml.CLoader)
        return _data

    def save_canvas(self, canvas):
        _d = canvas.serialize()
        _uuid = canvas.uuid
        _role = canvas.role
        _file_io = ApplicationStcFileIO(self.modelPath)
        _file_io.write(_d)
