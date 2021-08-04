import os
from .define import EnumItemRole, EnumWorkDomain


class AppSetting:
    projectPath = os.path.join(os.getcwd(), 'projects')
    applicationPath = os.path.join(os.getcwd(), 'application')
    applicationThirdPartyPath = os.path.join(applicationPath, 'thirdparty')
    applicationTempPath = os.path.join(applicationPath, 'temp')
    applicationDataPath = os.path.join(applicationPath, 'data')
    applicationDataBasePath = os.path.join(applicationDataPath, 'base')
    featureLibsPath = os.path.join(applicationDataPath, 'feature_libs')
    rootFeatureLibsPath = os.path.join(applicationDataPath, 'root_feature_libs')
    graphvizBinPath = os.path.join(applicationThirdPartyPath, 'graphviz-2.48.0\\Graphviz\\bin')
    graphvizTempPath = os.path.join(applicationTempPath, 'graphviz')
    graphvizTempDefaultPNGPath = os.path.join(graphvizTempPath, 'default.png')
    evtFileExt = '.evt'
    stateFileExt = '.stc'
    resolverFileExt = '.rsv'
    observableFileExt = '.obo'
    infoFileExt = '.inf'
    projFileExt = '.proj'

    def get_extend_by_role(self, role):
        if role in [EnumItemRole.USER_FEATURE_STATE, EnumItemRole.DEV_FEATURE_STATE]:
            return EnumWorkDomain.MODEL, self.stateFileExt
        elif role in [EnumItemRole.USER_FEATURE_EVENT, EnumItemRole.DEV_FEATURE_EVENT]:
            return EnumWorkDomain.MODEL, self.evtFileExt
        elif role in [EnumItemRole.USER_FEATURE_RESOLVER]:
            return EnumWorkDomain.MODEL, self.resolverFileExt
        elif role in [EnumItemRole.DEV_FEATURE_OBO]:
            return EnumWorkDomain.MODEL, self.observableFileExt
        else:
            return None, None


APP_SETTING = AppSetting()
