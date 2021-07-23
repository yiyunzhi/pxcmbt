import os, shutil
import yaml
from .class_app_setting import APP_SETTING
from .class_app_file_io import *
from .class_builtin_features import BuiltInFeature


class Project:
    def __init__(self, name):
        self.name = name
        self.workspacePath = APP_SETTING.projectPath
        self.path = os.path.join(APP_SETTING.projectPath, name)
        self.modelPath = os.path.join(self.path, 'model')
        self.rackPath = os.path.join(self.path, 'rack')
        self.modelRootUuid = '00000000000000000000000000000000'
        self._evtFileExt = APP_SETTING.evtFileExt
        self._projFileExt = APP_SETTING.projFileExt
        self.projectEntryFilePath = os.path.join(self.path, self.name + self._projFileExt)
        self.builtInFeaturesMap = dict()
        self.update_built_in_features()
        self.savedState = False

    def update_built_in_features(self):
        self.builtInFeaturesMap.clear()
        for root, dirs, files in os.walk(APP_SETTING.featureLibsPath):
            if files:
                _name = root.split(os.sep)[-1]
                if _name not in self.builtInFeaturesMap:
                    self.builtInFeaturesMap.update({_name: BuiltInFeature(_name)})
                _feature = self.builtInFeaturesMap.get(_name)
                for file in files:
                    _file_path = os.path.join(root, file)
                    if file.endswith(APP_SETTING.infoFileExt):
                        _feature.infFile = _file_path
                    elif file.endswith(APP_SETTING.evtFileExt):
                        _feature.evtFile = _file_path
                    elif file.endswith(APP_SETTING.stateFileExt):
                        _feature.stcFile = _file_path

    def is_feature_lib_exist(self, name):
        return name in self.builtInFeaturesMap

    def create_feature_lib(self, name, desc, copy_state_uuid=None, copy_event_uuid=None):
        # fixme: first check given file if copyable
        _lib_path = os.path.join(APP_SETTING.featureLibsPath, name)
        os.makedirs(_lib_path)
        _inf_file_io = ApplicationInfFileIO(_lib_path, 'lib')
        _inf_file_io.headerDescription = desc
        _inf_file_io.headerLibName = 'Feature %s' % name
        _inf_file_io.write({'state': '%s.stc' % name, 'event': '%s.evt' % name})
        if copy_event_uuid is None:
            _file_io = ApplicationEvtFileIO(_lib_path, name)
            _file_io.write(None)
        else:
            _copy_event_from_path = os.path.join(self.modelPath, copy_event_uuid + APP_SETTING.evtFileExt)
            shutil.copyfile(_copy_event_from_path, os.path.join(_lib_path, name + APP_SETTING.evtFileExt))
        if copy_state_uuid is None:
            _file_io = ApplicationStcFileIO(_lib_path, name)
            _file_io.write(None)
        else:
            _copy_state_from_path = os.path.join(self.modelPath, copy_state_uuid + APP_SETTING.stateFileExt)
            shutil.copyfile(_copy_state_from_path, os.path.join(_lib_path, name + APP_SETTING.stateFileExt))
        self.update_built_in_features()

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

    def create_new_evt_file(self, name):
        _file_io = ApplicationEvtFileIO(self.modelPath, name)
        _file_io.write(None)

    def create_new_stc_file(self, name):
        _file_io = ApplicationStcFileIO(self.modelPath, name)
        _file_io.write(None)

    def create_new_rsv_file(self, name):
        _file_io = ApplicationRsvFileIO(self.modelPath, name)
        _file_io.write(None)

    def get_project_entry_file(self):
        _f = None
        with open(self.projectEntryFilePath, 'r', encoding='utf-8') as f:
            pass
        return _f

    # def get_user_feature_transitions(self, uuid):
    #     _file_io = self.get_file_io(uuid, EnumItemRole.USER_FEATURE_STATE)
    #     if _file_io is not None:
    #         _file_io.read()
    #         return _file_io.body.wires
    #     return None
    #
    # def get_root_feature_transitions(self, uuid):
    #     _file_io = self.get_file_io(uuid, EnumItemRole.DEV_FEATURE_STATE)
    #     if _file_io is not None:
    #         _file_io.read()
    #         return _file_io.body.wires
    #     return None

    def get_event_data(self, uuid):
        _guess_file_path = os.path.join(self.modelPath, uuid + APP_SETTING.evtFileExt)
        _exist = util_is_dir_exist(_guess_file_path)
        if _exist:
            _file_io = ApplicationEvtFileIO(self.modelPath, uuid + APP_SETTING.evtFileExt)
            _file_io.read()
            return _file_io
        else:
            return None

    def save_event(self, panel):
        _d = panel.serialize()
        _uuid = panel.uuid
        _role = panel.role
        _file_io = ApplicationEvtFileIO(self.modelPath, _uuid)
        _file_io.write(_d)

    def save_resolver(self, panel):
        _d = panel.serialize()
        _uuid = panel.uuid
        _role = panel.role
        _file_io = ApplicationRsvFileIO(self.modelPath, _uuid)
        _file_io.write(_d)

    def save_canvas(self, canvas):
        _d = canvas.serialize()
        _uuid = canvas.uuid
        _role = canvas.role
        _file_io = ApplicationStcFileIO(self.modelPath, _uuid)
        _file_io.write(_d)

    def save_project(self, project_mgr_pane):
        _d = project_mgr_pane.serialize()
        _file_io = ApplicationProjFileIO(self.path, self.name + self._projFileExt)
        _file_io.write(_d)

    def get_file_io(self, uuid, role):
        _work_domain, _file_extend = APP_SETTING.get_extend_by_role(role)
        if _file_extend is not None:
            _file_io = self.guess_file_io_by_file_extend(_file_extend)
            if _file_io is None:
                raise IOError('unknown file extend of uuid=%s' % uuid)
            if _work_domain == EnumWorkDomain.MODEL:
                _file_path_exist = os.path.exists(os.path.join(self.modelPath, uuid + _file_extend))
                if _file_path_exist:
                    _inst = _file_io(self.modelPath, uuid + _file_extend)
                    _inst.read()
                    return _inst
                else:
                    return None
        return None

    def guess_file_io_by_file_extend(self, extend):
        if extend == APP_SETTING.evtFileExt:
            return ApplicationEvtFileIO
        elif extend == APP_SETTING.stateFileExt:
            return ApplicationStcFileIO
        elif extend == APP_SETTING.infoFileExt:
            return ApplicationInfFileIO
        elif extend == APP_SETTING.resolverFileExt:
            return ApplicationRsvFileIO
        else:
            return None

    def open_project(self, project_path):
        _proj_path, _file_name = os.path.split(project_path)
        _workspace_path, _proj_name = os.path.split(_proj_path)
        self.name = _proj_name
        self.set_project_workspace_path(_workspace_path)
        _file_io = ApplicationProjFileIO(_proj_path, _file_name)
        _file_io.read()
        return _file_io

    def _renew_stc_uuid(self, file_io):
        _replaced = dict()
        _body = file_io.body
        _nodes = _body.nodes
        _wires = _body.wires
        for x in _nodes:
            _old_uuid = x['uuid']
            _new_uuid = util_get_uuid_string()
            _replaced.update({_old_uuid: _new_uuid})
            x['uuid'] = _new_uuid
        for x in _wires:
            _old_uuid = x['uuid']
            _old_src_node_uuid = x['srcNodeUUID']
            _old_dst_node_uuid = x['dstNodeUUID']
            if _old_uuid in _replaced:
                _new_uuid = _replaced[_old_uuid]
            else:
                _new_uuid = util_get_uuid_string()
            if _old_src_node_uuid in _replaced:
                _new_src_node_uuid = _replaced[_old_src_node_uuid]
            else:
                _new_src_node_uuid = util_get_uuid_string()
            if _old_dst_node_uuid in _replaced:
                _new_dst_node_uuid = _replaced[_old_dst_node_uuid]
            else:
                _new_dst_node_uuid = util_get_uuid_string()
            x['uuid'] = _new_uuid
            x['srcNodeUUID'] = _new_src_node_uuid
            x['dstNodeUUID'] = _new_dst_node_uuid

    def add_user_feature_state(self, feature_name, rename):
        _feature = self.builtInFeaturesMap.get(feature_name)
        if _feature is not None:
            _dst_path = os.path.join(self.modelPath, rename + APP_SETTING.stateFileExt)
            # copy from data to project and rename it
            shutil.copyfile(_feature.stcFile, _dst_path)
            # renew uuid
            _file_io = ApplicationStcFileIO(self.modelPath, rename + APP_SETTING.stateFileExt)
            _file_io.read()
            self._renew_stc_uuid(_file_io)
            _file_io.write()

    def add_user_feature_event(self, feature_name, rename):
        _feature = self.builtInFeaturesMap.get(feature_name)
        if _feature is not None:
            # copy from data to project and rename it
            shutil.copyfile(_feature.evtFile, os.path.join(self.modelPath, rename + APP_SETTING.evtFileExt))

    def add_root_feature_event(self, feature_name, rename):
        _feature = self.builtInFeaturesMap.get(feature_name)
        if _feature is not None:
            # copy from data to project and rename it
            shutil.copyfile(_feature.evtFile, os.path.join(self.modelPath, rename + APP_SETTING.evtFileExt))

    def add_root_feature_state(self, feature_name, rename):
        _feature = self.builtInFeaturesMap.get(feature_name)
        if _feature is not None:
            _dst_path = os.path.join(self.modelPath, rename + APP_SETTING.stateFileExt)
            # copy from data to project and rename it
            shutil.copyfile(_feature.stcFile, _dst_path)
            # renew uuid
            _file_io = ApplicationStcFileIO(self.modelPath, rename + APP_SETTING.stateFileExt)
            _file_io.read()
            self._renew_stc_uuid(_file_io)
            _file_io.write()

    def save_ui_perspective(self, perspective_str):
        with open(os.path.join(self.path, 'ui.pepc'), "w") as f:
            f.write(perspective_str)

    def load_ui_perspective(self):
        _path = os.path.join(self.path, 'ui.pepc')
        if util_is_dir_exist(_path):
            with open(os.path.join(self.path, 'ui.pepc'), "r") as f:
                return f.read()
        return None

    def remove_stc_file(self, uuid):
        _path = os.path.join(self.modelPath, uuid + APP_SETTING.stateFileExt)
        if util_is_dir_exist(_path):
            os.remove(_path)

    def remove_evt_file(self, uuid):
        _path = os.path.join(self.modelPath, uuid + APP_SETTING.evtFileExt)
        if util_is_dir_exist(_path):
            os.remove(_path)

    def remove_rsv_file(self, uuid):
        _path = os.path.join(self.modelPath, uuid + APP_SETTING.resolverFileExt)
        if util_is_dir_exist(_path):
            os.remove(_path)
