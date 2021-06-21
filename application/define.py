import enum

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
    MODEL = 1
    DEV_FEATURE = 2
    DEV_FEATURE_STATE = 3
    DEV_FEATURE_EVENT = 4
    USER_STATE_FEATURE = 5
    USER_STATE_FEATURE_STATE = 6
    SESSIONS = 20
    SCRIPTS = 21
    SESSION = 22
    FEATURE_LIB = 50
    FEATURE_LIB_ITEM = 51
    ITEM_STATE = 100
    ITEM_TRANSITION = 110
    ITEM_NODE_NOTE = 120


class EnumPanelRole(enum.IntEnum):
    STATE_CHART_CANVAS = 0


class EnumAppSignals:
    sigV2VModelTreeItemDoubleClicked = 'sigV2VModelTreeItemDoubleClicked'
    sigV2VCanvasToolbarModeChanged = 'sigV2VCanvasToolbarModeChanged'
    sigV2VGuiModeDelItemRequested = 'sigV2VGuiModeDelItemRequested'
    sigV2VCanvasNodeDClicked = 'sigV2VCanvasNodeDClicked'
    sigV2VCanvasTransitionDClicked = 'sigV2VCanvasTransitionDClicked'
    sigV2VCanvasNodeShowProps = 'sigV2VCanvasNodeShowProps'
    sigV2VCanvasNodeNoteDClicked = 'sigV2VCanvasNodeNoteDClicked'


class EnumMBTEventType:
    OUTGOING = 'outgoing'
    INCOMING = 'incoming'
    ALL_VALUES = [OUTGOING, INCOMING]
