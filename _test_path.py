import os
from application.class_app_setting import APP_SETTING
from application.class_builtin_features import BuiltInFeature
from application.class_project import Project

proj = Project('test')
_inf=proj.builtInFeaturesMap['pwr'].get_inf_file_content()
print(_inf)
