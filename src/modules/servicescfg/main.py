#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# === This file is part of Calamares - <http://github.com/calamares> ===
#
#   Copyright 2016, Artoo <artoo@manjaro.org>
#
#   Calamares is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Calamares is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Calamares. If not, see <http://www.gnu.org/licenses/>.

import libcalamares
import os

from libcalamares.utils import check_target_env_call, debug

class ServicesController:
    def __init__(self):
        self.__root = libcalamares.globalstorage.value('rootMountPoint')
        self.__services = libcalamares.job.configuration.get('services', [])

    @property
    def root(self):
        return self.__root
    
    @property
    def services(self):
        return self.__services

    def update(self, action, status):
        for svc in self.services[status]:
            if os.path.exists(self.root + "/etc/init.d/" + svc["name"]):
                check_target_env_call(["rc-update", action, svc["name"], svc["runlevel"]])

    def run(self):
        for key in self.services.keys():
            if key == "enabled":
                self.update("add", key)
            elif key == "disabled":
                self.update("del", key)

        return None

def run():
    """ Setup openrc services """
    sc = ServicesController()
    return sc.run()
