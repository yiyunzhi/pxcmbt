import os
from .define import EnumItemRole, EnumWorkDomain


class AppSetting:
    projectPath = os.path.join(os.getcwd(), 'projects')
    applicationPath = os.path.join(os.getcwd(), 'application')
    applicationDataPath = os.path.join(applicationPath, 'data')
    applicationHtmlTemplatePath = os.path.join(applicationDataPath, 'html_template')
    applicationMaskStateDotGraphHtmlTemplatePath = os.path.join(applicationHtmlTemplatePath, 'masked_state_dot_graph')
    featureLibsPath = os.path.join(applicationDataPath, 'feature_libs')
    evtFileExt = '.evt'
    stateFileExt = '.stc'
    infoFileExt = '.inf'
    projFileExt = '.proj'

    def get_extend_by_role(self, role):
        if role in [EnumItemRole.USER_FEATURE_STATE, EnumItemRole.DEV_FEATURE_STATE]:
            return EnumWorkDomain.MODEL, self.stateFileExt
        elif role in [EnumItemRole.USER_FEATURE_EVENT, EnumItemRole.DEV_FEATURE_EVENT]:
            return EnumWorkDomain.MODEL, self.evtFileExt
        else:
            return None,None


APP_SETTING = AppSetting()
