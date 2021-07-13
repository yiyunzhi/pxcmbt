# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_test_runner.py
# ------------------------------------------------------------------------------
#
# File          : class_test_runner.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
from collections import OrderedDict


class MBTRunner:
    def __init__(self, features=None):
        self.features = OrderedDict()
        if features is not None and isinstance(features, list):
            [self.features.update({x.uuid: x}) for x in features]
            self.build()
        self.suites = list()
        self.cursor = 0

    def add_feature(self, feature):
        self.features.update({feature.uuid: feature})

    def remove_feature(self, uuid):
        if uuid in self.features:
            self.features.pop(uuid)

    def build(self):
        self.suites.clear()
        for uid, feature in self.features.items():
            [self.suites.append(x) for x in feature]

    def next(self):
        _params = {'cursor': self.cursor,
                   'total': len(self.suites),
                   }
        _progress_info = urllib.parse.urlencode(_params, doseq=True)
        if self.cursor >= len(self.suites):
            _state_info = 'state=END'
            _res = '%s&%s' % (_state_info, _progress_info)
        else:
            _state_info = 'state=OK'
            _res = self.suites[self.cursor]
            self.cursor += 1
            _res = '%s&%s&%s' % (_state_info, _res, _progress_info)
        return _res

    def get_percent(self):
        if self.suites:
            return self.cursor / len(self.suites)
        else:
            return .0

    def abort(self):
        return True

    def restart(self):
        self.build()
        self.cursor = 0
        return True

    def restart_from(self, cursor):
        if cursor < len(self.suites):
            self.cursor = cursor
            return True
        else:
            return False
