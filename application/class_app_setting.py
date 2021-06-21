import os


class AppSetting:
    projectPath = os.path.join(os.getcwd(), 'projects')
    applicationPath = os.path.join(os.getcwd(), 'application')
    applicationDataPath = os.path.join(applicationPath, 'data')
    featureLibsPath = os.path.join(applicationDataPath, 'feature_libs')


APP_SETTING = AppSetting()
