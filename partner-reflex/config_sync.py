#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import sys
import json
from gi.repository import Gio
sys.path.append('/usr/lib/config-sync')
from vcc_param import VccParam
from vcc_userlock import VccUserLock


def get_reflex_list():
    return [
        "config-sync",
    ]


def get_reflex_properties(name):
    if name == "config-sync":
        return {
            "need-plugin": ["mesh"],
            "protocol": "config-sync",
            "role": "p2p",
        }
    else:
        assert False


def get_reflex_object(fullname):
    if name == "config-sync":
        return _PluginObject()
    else:
        assert False


class _PluginObject:

    def on_init(self):
        self.param = VccParam()

        if not os.path.exists(self.param.dataDir):
            os.makedirs(self.param.dataDir)

        self.localRepo = VccLocalRepo(self.param,
                                      lambda: self.on_repo_change("localhost"))

        self.remoteRepoDict = dict()
        for peername in os.listdir(self.param.dataDir):
            if peername != "localhost":
                self.remoteRepoDict[peername] = VccRepo(self.param,
                                                        peername,
                                                        lambda: self.on_repo_change(peername))

        self.apiServer = _ApiServer(self, "/tmp.socket")
        self.bPause = False

    def on_fini(self):
        self.apiServer.dispose()
        for repoObj in self.remoteRepoDict.values():
            repoObj.dispose()
        self.localRepo.dispose()

    def on_peer_appear(self, peername, ip, uid):
        dict2 = self.remoteRepoDict.copy()
        dict2[self.my_hostname] = self.localRepo

        if peername not in self.remoteRepoDict:
            self.remoteRepoDict[peername] = VccRepo(self.param,
                                                    peername,
                                                    lambda: self.on_repo_change(peername))

        self.send_message_to_peer(peername, {"pull-request": dict2})

    def on_peer_disappear(self, peername):
        pass

    def on_receive_message_from_peer(self, peername, message):
        if self.bPause:
            return

        if "pull-request" in message:
            for repo_name, port in message["pull-request"]:
                if repo_name == self.my_hostname:
                    self.localRepo.pull_from(peername, port)
                elif repo_name in self.remoteRepoDict:
                    self.remoteRepoDict[repo_name].pull_from(peername, port)
            return

        if "pull-request-needed" in message:
            dict2 = dict()
            for repo_name in message["pull-request-needed"]:
                if repo_name == self.my_hostname:
                    dict2[repo_name] = self.localRepo.start_server()
                elif repo_name in self.remoteRepoDict:
                    dict2[repo_name] = self.remoteRepoDict[repo_name].start_server()
            if len(dict2) > 0:
                self.send_message_to_peer(peername, {"pull-request": dict2})
            return

        assert False

    def on_repo_change(self, repo_name):
        if repo_name == "localhost":
            port = self.localRepo.start_server()                        # fixme, what if the server already started
            repo_name = self.my_hostname
        else:
            port = self.remoteRepoDict[repo_name].start_server()

        for pi in self.peer_info:
            self.send_message_to_peer(pi["hostname"], {
                "pull-request": {repo_name: port},
            })

    def on_trigger(self):
        pass

    def on_pause(self):
        assert not self.bPause
        self.bPause = True


    def on_resume(self):
        assert self.bPause
        self.bPause = False












    def _send_pull_request_needed(self, peername, repo_name):
        message = {
            "pull-request-needed": {
                "repo-name": repo_name,
            }
        }
        self.send_message_to_peer(peername, message)

