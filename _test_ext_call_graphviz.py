# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : _test_ext_call_graphviz.py
# ------------------------------------------------------------------------------
#
# File          : _test_ext_call_graphviz.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import os
import subprocess
#import pygraphiv
from application.class_app_setting import APP_SETTING
from application.class_graphviz import Graphviz
_dot_lng = 'digraph G {compound=true;   subgraph cluster1 {   label="PWR";      node3 [label="sOK",tooltip="sOK"];      node4 [label="sUnder",tooltip="sUnder"];      node5 [label="sOver",tooltip="sOver"];      node6 [label="INIT",tooltip="INIT"];   }   subgraph cluster2 {   label="Root";      node7 [label="sNO_PARED",tooltip="sNO_PARED"];      node8 [label="INIT",tooltip="INIT"];      node9 [label="sPARED",tooltip="sPARED"];      node10 [label="sRUN",tooltip="sRUN"];      node11 [label="sDIAG",tooltip="sDIAG"];      node12 [label="sFS",tooltip="sFS"];      node13 [label="sPOWERED",tooltip="sPOWERED"];   }node3->node4 [label="t2under"];node3->node5 [label="t2over"];node4->node3 [label="t2ok"];node4->node5 [label="t2over"];node5->node3 [label="t2ok"];node5->node4 [label="t2under"];node6->node3 [label="t2init"];node7->node9 [label="t2Parameterize"];node7->node11 [label="t2ParFailed"];node8->node13 [label="t2Init"];node9->node10 [label="t2StartSafeComm"];node10->node11 [label="t2HasDiag"];node10->node12 [label="t2FS"];node10->node9 [label="t2StopSafeComm"];node11->node10 [label="t2DiagAcked"];node11->node12 [label="t2FS"];node12->node13 [label="t2Repower"];node13->node7 [label="t2PowerOK"];}'

_g=Graphviz(APP_SETTING.graphvizBinPath,APP_SETTING.graphvizTempDefaultPNGPath)
_g.render_dot_string_to_file(_dot_lng)

