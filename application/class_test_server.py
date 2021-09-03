# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : class_test_server.py
# ------------------------------------------------------------------------------
#
# File          : class_test_server.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import threading
from xmlrpc.server import SimpleXMLRPCServer
from pubsub import pub
from .define import EnumAppSignals


class MBTOnlineTestServer:
    def __init__(self, runner):
        self.port = 8180
        self.address = 'localhost'
        self.isRunning = False
        self.runner = runner
        self.rpcServerThread = threading.Thread(target=self._run)
        self.rpcServer = None

    def _run(self):
        pub.sendMessage(EnumAppSignals.sigV2VTCConsoleAddInfoContent.value,
                        content="MBTXmlRpcTestServer Listening on %s:%s..." % (self.address, self.port))
        self.rpcServer = SimpleXMLRPCServer(("localhost", 8180),allow_none=True,use_builtin_types=True)
        self.rpcServer.register_instance(self.runner, True)
        self.rpcServer.serve_forever()

    def start(self):
        if not self.isRunning:
            self.rpcServerThread.start()
            self.isRunning = True

    def stop(self):
        if self.isRunning:
            if self.rpcServer is not None:
                self.rpcServer.shutdown()
            self.isRunning = False
            self.rpcServerThread = threading.Thread(target=self._run)
            pub.sendMessage(EnumAppSignals.sigV2VTCConsoleAddInfoContent.value,
                            content="MBTXmlRpcTestServer stopped")