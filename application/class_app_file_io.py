from yaml import CLoader, load


class ApplicationFileHeader:
    def __init__(self, **kwargs):
        self.version = kwargs.get('version')
        self.author = kwargs.get('author')
        self.date = kwargs.get('date')
        self.description = kwargs.get('description')
        self.type = kwargs.get('type')


class ApplicationFileBody:
    def __init__(self, **kwargs):
        pass


class ApplicationFileIO:
    HEADER_K = 'HEADER'
    BODY_K = 'BODY'

    def __init__(self, file_path, header_cls=ApplicationFileHeader, body_cls=ApplicationFileBody):
        self.extend = '.*'
        self.headerCls = header_cls
        self.bodyCls = body_cls
        self.filePath = file_path
        self.header = None
        self.body = None

    def read(self):
        with open(self.filePath) as f:
            _data = load(f, CLoader)
            if self.HEADER_K in _data and self.headerCls is not None:
                self.header = self.headerCls(**_data.get(self.HEADER_K))
            if self.BODY_K in _data and self.bodyCls is not None:
                self.body = self.bodyCls(**_data.get(self.BODY_K))

    def write(self, data):
        pass

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
    def __init__(self, file_path):
        ApplicationFileIO.__init__(self, file_path, body_cls=ApplicationInfFileBody)
        self.extend = '.inf'


class ApplicationStcFileBody(ApplicationFileBody):
    def __init__(self, **kwargs):
        ApplicationFileBody.__init__(self, **kwargs)
        self.canvas = kwargs.get('canvas')
        self.nodes = kwargs.get('nodes')
        self.wires = kwargs.get('wires')


class ApplicationStcFileIO(ApplicationFileIO):
    def __init__(self, file_path):
        ApplicationFileIO.__init__(self, file_path, body_cls=ApplicationStcFileBody)
        self.extend = '.stc'

    def write(self, data):
        print('ApplicationStcFileIO write', data)


class ApplicationEvtFileBody(ApplicationFileBody):
    def __init__(self, **kwargs):
        ApplicationFileBody.__init__(self, **kwargs)
        self.events = kwargs.get('canvas')


class ApplicationEvtFileIO(ApplicationFileIO):
    def __init__(self, file_path):
        ApplicationFileIO.__init__(self, file_path, body_cls=ApplicationEvtFileBody)
        self.extend = '.evt'
