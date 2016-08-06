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

from libcalamares.utils import target_env_call, check_target_env_call, debug
from subprocess import CalledProcessError

class ServicesController:
    def __init__(self):
        self.__services = libcalamares.job.configuration.get('services', [])

    @property
    def services(self):
        return self.__services

    def update(self, action, status):
        for svc in self.services[status]:
                check_target_env_call(["rc-update", action, svc["name"], svc["runlevel"]])

    def run(self):
        svc = lambda x: self.services[x]
        self.update("add", svc["enabled"])
        if svc["disabled"] is not None:
            self.update("del", svc["disabled"])
        #=======================================================================
        # for key in self.services.keys():
        #     if key == "enabled":
        #         self.update("add", "enabled")
        #     elif key == "disabled":
        #         self.update("del", "disabled")
        #=======================================================================

        return None

def run():
    """ Setup openrc services """
    sc = ServicesController()
    return sc.run()
