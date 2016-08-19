#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# === This file is part of Calamares - <http://github.com/calamares> ===
#
#   Copyright 2014 - 2015, Philip Müller <philm@manjaro.org>
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
import shutil
from subprocess import check_call
from os.path import join, exists
from libcalamares import target_env_call

class ConfigController:
    def __init__(self):
        self.__root = libcalamares.globalstorage.value( "rootMountPoint" )
        self.__keyrings = libcalamares.job.configuration.get('keyrings', [])

    @property
    def root(self):
        return self.__root
      
    def init_keyring(self):
        check_target_env_call(["pacman-key", "--init"])

    def populate_keyring(self):
        check_target_env_call(["pacman-key", "--populate"] + self.keyrings)
        
    def setExpression(self, pattern, file):
        check_call(["sed", "-e", pattern, "-i", join(self.root, file)])
        
    def terminate(self, proc):
        target_env_call(['killall', '-9', proc])
        
    def copy_file(self, file):
        if exists("/" + file):
            shutil.copy2("/" + file, join(self.root, file))
    
    def remove_pkg(self, pkg, path):
        if exists(join(self.root, path)):
            target_env_call(['pacman', '-R', '--noconfirm', pkg])
    
    def run(self):
        self.init_keyring()
        self.populate_keyring()

        # Remove calamares
        self.remove_pkg("calamares", "usr/bin/calamares")

        # Copy mirror list
        self.copy_file('etc/pacman.d/mirrorlist')
        
        # Workaround for pacman-key bug FS#45351 https://bugs.archlinux.org/task/45351
        # We have to kill gpg-agent because if it stays around we can't reliably unmount
        # the target partition.
        self.terminate('gpg-agent')
        
        # configure openrc specific settings
        if exists(join(self.root, "usr/bin/openrc")):
            self.setExpression('s|^.*rc_shell=.*|rc_shell="/usr/bin/sulogin"|', "etc/rc.conf")
            self.setExpression('s|^.*rc_controller_cgroups=.*|rc_controller_cgroups="YES"|', "etc/rc.conf")
            exp = 's|^.*keymap=.*|keymap="' + libcalamares.globalstorage.value("keyboardLayout") + '"|'
            self.setExpression(exp, "etc/conf.d/keymaps")
            for dm in libcalamares.globalstorage.value("displayManagers"):
                exp = 's|^.*DISPLAYMANAGER=.*|DISPLAYMANAGER="' + dm + '"|'
                self.setExpression(exp, "etc/conf.d/xdm")
                if dm == "lightdm":
                    self.setExpression('s|^.*minimum-vt=.*|minimum-vt=7|', "etc/lightdm/lightdm.conf")
                    self.setExpression('s|pam_systemd.so|pam_ck_connector.so nox11|', "etc/pam.d/lightdm-greeter")
        
        # Update grub.cfg
        if exists(join(self.root, "usr/bin/update-grub")) and libcalamares.globalstorage.value("bootLoader") is not None:
            target_env_call(["update-grub"])
    
def run():
    """ Misc postinstall configurations """

    config = ConfigController()
    
    return config.run()
