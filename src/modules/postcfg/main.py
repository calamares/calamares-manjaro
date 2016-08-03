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

def run():
    """ Misc postinstall configurations """

    install_path = libcalamares.globalstorage.value( "rootMountPoint" )

    # Update grub.cfg
    if os.path.exists("{!s}/usr/bin/update-grub".format(install_path)) and libcalamares.globalstorage.value("bootLoader") is not None:
        libcalamares.utils.target_env_call(["update-grub"])

    # Remove calamares
    if os.path.exists("{!s}/usr/bin/calamares".format(install_path)):
        libcalamares.utils.target_env_call(['pacman', '-R', '--noconfirm', 'calamares'])

    # Copy mirror list
    shutil.copy2('/etc/pacman.d/mirrorlist',
             os.path.join(install_path, 'etc/pacman.d/mirrorlist'))

    # Copy random generated keys by pacman-init to target
    if os.path.exists("{!s}/etc/pacman.d/gnupg".format(install_path)):
        os.system("rm -rf {!s}/etc/pacman.d/gnupg".format(install_path))
    os.system("cp -a /etc/pacman.d/gnupg {!s}/etc/pacman.d/".format(install_path))
    libcalamares.utils.target_env_call(['pacman-key', '--populate', 'archlinux', 'manjaro'])
    
    # Workaround for pacman-key bug FS#45351 https://bugs.archlinux.org/task/45351
    # We have to kill gpg-agent because if it stays around we can't reliably unmount
    # the target partition.
    libcalamares.utils.target_env_call(['killall', '-9', 'gpg-agent'])

    # Set /etc/keyboard.conf (keyboardctl is depreciated)
    if os.path.exists("{!s}/etc/keyboard.conf".format(install_path)):
        keyboard_layout = libcalamares.globalstorage.value("keyboardLayout")
        keyboard_variant = libcalamares.globalstorage.value("keyboardVariant")
        consolefh = open("{!s}/etc/keyboard.conf".format(install_path), "r")
        newconsolefh = open("{!s}/etc/keyboard.new".format(install_path), "w")
        for line in consolefh:
            line = line.rstrip("\r\n")
            if(line.startswith("XKBLAYOUT=")):
                newconsolefh.write("XKBLAYOUT=\"{!s}\"\n".format(keyboard_layout))
            elif(line.startswith("XKBVARIANT=") and keyboard_variant != ''):
                newconsolefh.write("XKBVARIANT=\"{!s}\"\n".format(keyboard_variant))
            else:
                newconsolefh.write("{!s}\n".format(line))
        consolefh.close()
        newconsolefh.close()
        libcalamares.utils.target_env_call(['mv', '/etc/keyboard.conf', '/etc/keyboard.conf.old'])
        libcalamares.utils.target_env_call(['mv', '/etc/keyboard.new', '/etc/keyboard.conf'])

    return None
