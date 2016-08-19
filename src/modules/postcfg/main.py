#!/usr/bin/env python3
# encoding: utf-8
# === This file is part of Calamares - <http://github.com/calamares> ===
#
#   Copyright 2014 - 2015, Philip Müller <philm@manjaro.org>
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
from os.path import join
from libcalamares import target_env_call
    
def run():
    """ Misc postinstall configurations """

    install_path = libcalamares.globalstorage.value( "rootMountPoint" )

    # Update grub.cfg
    if os.path.exists(join(install_path, "usr/bin/update-grub")) and libcalamares.globalstorage.value("bootLoader") is not None:
        target_env_call(["update-grub"])

    # Remove calamares
    if os.path.exists(join(install_path, "usr/bin/calamares")):
        target_env_call(['pacman', '-R', '--noconfirm', 'calamares'])

    # Copy mirror list
    shutil.copy2('/etc/pacman.d/mirrorlist',
             join(install_path, 'etc/pacman.d/mirrorlist'))

    target_env_call(['pacman-key', '--init'])
    target_env_call(['pacman-key', '--populate', 'archlinux', 'manjaro'])
    
    # Workaround for pacman-key bug FS#45351 https://bugs.archlinux.org/task/45351
    # We have to kill gpg-agent because if it stays around we can't reliably unmount
    # the target partition.
    target_env_call(['killall', '-9', 'gpg-agent'])
        
    if os.path.exists(join(install_path, "usr/bin/openrc")):
        check_call(["sed", "-e", 's|^.*rc_shell=.*|rc_shell="/usr/bin/sulogin"|', "-e", 's|^.*rc_controller_cgroups=.*|rc_controller_cgroups="YES"|', "-i", join(install_path, "etc/rc.conf")])
        kbl = libcalamares.globalstorage.value("keyboardLayout")
        rep_str = 's|^.*keymap=.*|keymap="' + kbl + '"|'
        check_call(["sed", "-e", rep_str, "-i", join(install_path, "etc/conf.d/keymaps")])
        for dm in libcalamares.globalstorage.value("displayManagers"):
            rep_str = 's|^.*DISPLAYMANAGER=.*|DISPLAYMANAGER="' + dm + '"|'
            check_call(["sed", "-e", rep_str, "-i", join(install_path, "etc/conf.d/xdm")])
            if dm == "lightdm":
                check_call(["sed", "-e", 's|^.*minimum-vt=.*|minimum-vt=7|', "-i", join(install_path, "etc/lightdm/lightdm.conf")])
                check_call(["sed", "-e", 's|pam_systemd.so|pam_ck_connector.so nox11|', "-i", join(install_path, "etc/pam.d/lightdm-greeter")])

    return None
