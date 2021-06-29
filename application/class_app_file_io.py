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
            if self.HEADER_K in _data and self.headerCls is not None:
                self.header = self.headerCls(**_data.get(self.HEADER_K))
            if self.BODY_K in _data and self.bodyCls is not None:
                self.body = self.bodyCls(**_data.get(self.BODY_K))

    def write(self, data):
        _file_full_path = os.path.join(self.filePath, self.fileName + self.extend)
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


class ApplicationInfFileBody(ApplicationFileBody):
    def __init__(self, **kwargs):
        ApplicationFileBody.__init__(self, **kwargs)
        self.state = kwargs.get('state')
        self.event = kwargs.get('event')


class ApplicationInfFileIO(ApplicationFileIO):
    def __init__(self, file_path, file_name):
        ApplicationFileIO.__init__(self, file_path, file_name, body_cls=ApplicationInfFileBody)
        self.extend = '.inf'


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


class ApplicationStcFileIO(ApplicationFileIO):
    def __init__(self, file_path, file_name):
        ApplicationFileIO.__init__(self, file_path, file_name, header_cls=ApplicationStcFileHeader,
                                   body_cls=ApplicationStcFileBody)
        self.extend = '.stc'

    def write(self, data):
        _hdr = self.headerCls()
        _data = dict({self.HEADER_K: _hdr.persist(), self.BODY_K: data})
        super(ApplicationStcFileIO, self).write(_data)


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
