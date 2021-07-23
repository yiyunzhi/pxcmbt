import os
import yaml
from .class_app_setting import APP_SETTING
from .define import *
from .utils_helper import *


class ApplicationFileHeader:
    def __init__(self, **kwargs):
        self.version = kwargs.get('version')
        self.author = kwargs.get('author')
        self.date = kwargs.get('date')
        self.description = kwargs.get('description')
        self.type = kwargs.get('type')

    def persist(self):
        pass


class ApplicationFileBody:
    def __init__(self, **kwargs):
        pass


class DotGraphStringIO:
    def __init__(self):
        self.content = ''

    def write(self, val):
        self.content += val

    def clear(self):
        self.content = ''


class DotGraphHtmlFileIO:
    def __init__(self):
        self.filePath = APP_SETTING.applicationMaskStateDotGraphHtmlTemplatePath
        self.fileName = 'index.html'
        self.outputFileName = '_index.html'
        self.content = None
        self.dotGraphStringIO = DotGraphStringIO()

    def read(self):
        with open(os.path.join(self.filePath, self.fileName), encoding='utf-8') as f:
            self.content = f.read()

    def write(self, val):
        pass

    def update_dot_graph(self, dot_string=None):
        if dot_string is None:
            dot_string = self.dotGraphStringIO.content
        if dot_string is not None:
            dot_string = dot_string.replace('\n', '').replace('\r', '').replace('\t', '')
            _html_content = self.content.replace('$DOT_GRAPH_STRING', dot_string)
            with open(os.path.join(self.filePath, self.outputFileName), 'w', encoding='utf-8') as f:
                f.write(_html_content)
            return os.path.join(self.filePath, self.outputFileName)
        return None


class ApplicationFileIO:
    HEADER_K = 'HEADER'
    BODY_K = 'BODY'

    def __init__(self, file_path, file_name, header_cls=ApplicationFileHeader, body_cls=ApplicationFileBody):
        self.extend = '.*'
        self.headerCls = header_cls
        self.bodyCls = body_cls
        self.filePath = file_path
        self.fileName = file_name
        self.header = None
        self.body = None

    def read(self):
        with open(os.path.join(self.filePath, self.fileName)) as f:
            _data = yaml.load(f, Loader=yaml.Loader)
            if _data is None:
                # todo: log or show a message box
                return
            if self.HEADER_K in _data and self.headerCls is not None:
                _header = _data.get(self.HEADER_K)
                if _header is None:
                    _header = dict()
                self.header = self.headerCls(**_header)
            if self.BODY_K in _data and self.bodyCls is not None:
                _body = _data.get(self.BODY_K)
                if _body is None:
                    _body = dict()
                self.body = self.bodyCls(**_body)

    def write(self, data):
        if '.' in self.fileName:
            _file_name = self.fileName
        else:
            _file_name = self.fileName + self.extend
        _file_full_path = os.path.join(self.filePath, _file_name)
        with open(_file_full_path, "w") as f:
            yaml.dump(data, f)

    def get_author(self):
        return self.header.author

    def get_version(self):
        return self.header.version

    def get_description(self):
        return self.header.description

    def get_type(self):
        return self.header.type


class ApplicationInfFileHeader(ApplicationFileHeader):
    def __init__(self, **kwargs):
        ApplicationFileHeader.__init__(self, **kwargs)

    def persist(self):
        _d = {'version': APP_VERSION,
              'author': util_get_computer_name(),
              'date': util_date_now(),
              'type': 'MBT_FEATURE_LIB'}
        return _d


class ApplicationInfFileBody(ApplicationFileBody):
    def __init__(self, **kwargs):
        ApplicationFileBody.__init__(self, **kwargs)
        self.state = kwargs.get('state')
        self.event = kwargs.get('event')


class ApplicationInfFileIO(ApplicationFileIO):
    def __init__(self, file_path, file_name):
        ApplicationFileIO.__init__(self, file_path, file_name, header_cls=ApplicationInfFileHeader,
                                   body_cls=ApplicationInfFileBody)
        self.extend = '.inf'
        self.headerDescription = ''
        self.headerLibName = ''

    def write(self, data):
        _hdr = self.headerCls()
        _hdr_d = _hdr.persist()
        _hdr_d.update({'description': self.headerDescription})
        _hdr_d.update({'libName': self.headerLibName})
        _data = dict({self.HEADER_K: _hdr_d, self.BODY_K: data})
        super(ApplicationInfFileIO, self).write(_data)


class ApplicationStcFileHeader(ApplicationFileHeader):
    def __init__(self, **kwargs):
        ApplicationFileHeader.__init__(self, **kwargs)

    def persist(self):
        _d = {'version': APP_VERSION,
              'author': util_get_computer_name(),
              'date': util_date_now(),
              'type': 'MBT_STC'}
        return _d


class ApplicationStcFileBody(ApplicationFileBody):
    def __init__(self, **kwargs):
        ApplicationFileBody.__init__(self, **kwargs)
        self.canvas = kwargs.get('canvas')
        self.nodes = kwargs.get('nodes')
        self.wires = kwargs.get('wires')

    def get_dict(self):
        return {'canvas': self.canvas, 'nodes': self.nodes, 'wires': self.wires}

    def get_transitions_list(self):
        if self.wires is not None:
            return [x['text'] for x in self.wires]
        return []

    def get_states_list(self):
        if self.nodes is not None:
            return [x['nameText'] for x in self.nodes]
        return []

    def get_init_state_name(self):
        pass


class ApplicationRsvFileBody(ApplicationFileBody):
    def __init__(self, **kwargs):
        ApplicationFileBody.__init__(self, **kwargs)


class ApplicationStcFileIO(ApplicationFileIO):
    def __init__(self, file_path, file_name):
        ApplicationFileIO.__init__(self, file_path, file_name, header_cls=ApplicationStcFileHeader,
                                   body_cls=ApplicationStcFileBody)
        self.extend = '.stc'

    def write(self, data=None):
        _hdr = self.headerCls()
        if data is None:
            if self.body:
                _data = dict({self.HEADER_K: _hdr.persist(), self.BODY_K: self.body.get_dict()})
            else:
                _data = dict({self.HEADER_K: _hdr.persist(), self.BODY_K: {}})
        else:
            _data = dict({self.HEADER_K: _hdr.persist(), self.BODY_K: data})
        super(ApplicationStcFileIO, self).write(_data)


class ApplicationRsvFileHeader(ApplicationFileHeader):
    def __init__(self, **kwargs):
        ApplicationFileHeader.__init__(self, **kwargs)

    def persist(self):
        _d = {'version': APP_VERSION,
              'author': util_get_computer_name(),
              'date': util_date_now(),
              'type': 'MBT_RSV'}
        return _d


class ApplicationRsvFileIO(ApplicationFileIO):
    def __init__(self, file_path, file_name):
        ApplicationFileIO.__init__(self, file_path, file_name, header_cls=ApplicationRsvFileHeader,
                                   body_cls=ApplicationRsvFileBody)
        self.extend = '.rsv'

    def write(self, data):
        _hdr = self.headerCls()
        _data = dict({self.HEADER_K: _hdr.persist(), self.BODY_K: data})
        super(ApplicationRsvFileIO, self).write(_data)


class ApplicationEvtFileBody(ApplicationFileBody):
    def __init__(self, **kwargs):
        ApplicationFileBody.__init__(self, **kwargs)
        self.events = kwargs


class ApplicationEvtFileHeader(ApplicationFileHeader):
    def __init__(self, **kwargs):
        ApplicationFileHeader.__init__(self, **kwargs)

    def persist(self):
        _d = {'version': APP_VERSION,
              'author': util_get_computer_name(),
              'date': util_date_now(),
              'type': 'MBT_EVT'}
        return _d


class ApplicationEvtFileIO(ApplicationFileIO):
    def __init__(self, file_path, file_name):
        ApplicationFileIO.__init__(self, file_path, file_name, header_cls=ApplicationEvtFileHeader,
                                   body_cls=ApplicationEvtFileBody)
        self.extend = '.evt'

    def write(self, data):
        _hdr = self.headerCls()
        _data = dict({self.HEADER_K: _hdr.persist(), self.BODY_K: data})
        super(ApplicationEvtFileIO, self).write(_data)


class ApplicationProjFileBody(ApplicationFileBody):
    def __init__(self, **kwargs):
        ApplicationFileBody.__init__(self, **kwargs)
        self.model = kwargs.get('model')
        self.rack = kwargs.get('rack')


class ApplicationProjFileHeader(ApplicationFileHeader):
    def __init__(self, **kwargs):
        ApplicationFileHeader.__init__(self, **kwargs)

    def persist(self):
        _d = {'version': APP_VERSION,
              'author': util_get_computer_name(),
              'date': util_date_now(),
              'type': 'MBT_PROJ'}
        return _d


class ApplicationProjFileIO(ApplicationFileIO):
    def __init__(self, file_path, file_name):
        ApplicationFileIO.__init__(self, file_path, file_name, header_cls=ApplicationProjFileHeader,
                                   body_cls=ApplicationProjFileBody)
        self.extend = '.proj'

    def write(self, data):
        _file_full_path = os.path.join(self.filePath, self.fileName)
        _hdr = self.headerCls()
        _data = dict({self.HEADER_K: _hdr.persist(), self.BODY_K: data})
        with open(_file_full_path, "w") as f:
            yaml.dump(_data, f)
