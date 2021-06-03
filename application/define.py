import enum
from blinker import signal

APP_NAME = 'PxCE MBT Editor'
REQ_WX_VERSION_STRING = '4.1.1'
APP_CONSOLE_TIME_WX_FMT = '%m/%d %H:%M:%S.%l'
APP_CONSOLE_TIME_PY_FMT = '%m/%d %H:%M:%S.%f'


class StandardItemData:
    __slots__ = ['uuid', 'role', 'flag', 'labelReadonly', 'tooltip', 'slotPath', 'parentUUID']
    pass


class ConsoleItemFlagEnum:
    FLAG_INFO = 'INFO'
    FLAG_WARNING = 'WARNING'
    FLAG_ERROR = 'ERROR'


class EnumItemRole(enum.IntEnum):
    ROOT = 0
    DEV_FEATURE = 1
    DEV_FEATURE_STATE = 2
    USER_STATE_FEATURE = 3
    USER_STATE_FEATURE_STATE = 4
    FEATURE_LIB = 50
    FEATURE_LIB_ITEM = 51


class EnumPanelRole(enum.IntEnum):
    STATE_CHART_CANVAS = 0


class EnumAppSignals:
    sigV2VModelTreeItemDoubleClicked = signal('sigV2VModelTreeItemDoubleClicked')
