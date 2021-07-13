import enum

APP_NAME = 'PxCE MBT Editor'
APP_VERSION = '2.0.1'
REQ_WX_VERSION_STRING = '4.1.1'
APP_CONSOLE_TIME_WX_FMT = '%m/%d %H:%M:%S.%l'
APP_CONSOLE_TIME_PY_FMT = '%m/%d %H:%M:%S.%f'


class StandardItemData:
    __slots__ = ['uuid', 'role', 'flag', 'labelReadonly', 'tooltip', 'slotPath', 'parentUUID']

    def __init__(self, **kwargs):
        self.uuid = kwargs.get('uuid')
        self.role = kwargs.get('role')
        self.flag = kwargs.get('flag')
        self.labelReadonly = kwargs.get('labelReadonly')
        self.tooltip = kwargs.get('tooltip')
        self.slotPath = kwargs.get('slotPath')
        self.parentUUID = kwargs.get('parentUUID')


class ConsoleItemFlagEnum:
    FLAG_INFO = 'INFO'
    FLAG_WARNING = 'WARNING'
    FLAG_ERROR = 'ERROR'


class EnumWorkDomain(enum.IntEnum):
    MODEL = 0
    RACK = 1


class EnumItemRole(enum.IntEnum):
    ROOT = 0
    MODEL = 1
    DEV_FEATURE = 2
    DEV_FEATURE_STATE = 3
    DEV_FEATURE_EVENT = 4
    SESSIONS = 20
    SCRIPTS = 21
    SESSION = 22
    USER_FEATURE = 50
    USER_FEATURE_ITEM = 51
    USER_FEATURE_STATE = 52
    USER_FEATURE_EVENT = 53
    ITEM_STATE = 100
    ITEM_TRANSITION = 110
    ITEM_NODE_NOTE = 120


class EnumPanelRole(enum.IntEnum):
    STATE_CHART_CANVAS = 0


class EnumAppSignals(enum.Enum):
    sigV2VModelTreeItemDoubleClicked = 'sigV2VModelTreeItemDoubleClicked'
    sigV2VCanvasToolbarModeChanged = 'sigV2VCanvasToolbarModeChanged'
    sigV2VGuiModeDelItemRequested = 'sigV2VGuiModeDelItemRequested'
    sigV2VCanvasNodeDClicked = 'sigV2VCanvasNodeDClicked'
    sigV2VCanvasTransitionDClicked = 'sigV2VCanvasTransitionDClicked'
    sigV2VCanvasNodeShowProps = 'sigV2VCanvasNodeShowProps'
    sigV2VCanvasNodeNoteDClicked = 'sigV2VCanvasNodeNoteDClicked'
    sigV2VProjectAddUserFeature = 'sigV2VProjectAddUserFeature'
    sigV2VProjectNewUserFeature = 'sigV2VProjectNewUserFeature'
    sigV2VProjectSaveUserFeatureAsLib = 'sigV2VProjectSaveUserFeatureAsLib'
    sigV2VMaskUserFeatureOnRoot = 'sigV2VMaskUserFeatureOnRoot'


class EnumMBTEventType(enum.Enum):
    OUTGOING = 'outgoing'
    INCOMING = 'incoming'
    ALL_VALUES = ['outgoing', 'incoming']


class EnumMBTEventDataType(enum.Enum):
    INTEGER = 'integer'
    STRING = 'string'
    FLOAT = 'float'
    ALL = ['integer', 'string', 'float']
