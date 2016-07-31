#!/usr/bin/env python3
# encoding: utf-8
# === This file is part of Calamares - <http://github.com/calamares> ===
#
#   Copyright 2014, Philip Müller <philm@manjaro.org>
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

import os
import subprocess

import libcalamares

import shutil

from libcalamares.utils import target_env_call
from subprocess.call import check_call

def run():
	""" Configure the hardware """

	install_path = libcalamares.globalstorage.value( "rootMountPoint" )

	# Copy generated xorg.xonf to target
	if os.path.exists("/etc/X11/xorg.conf"):
		shutil.copy2('/etc/X11/xorg.conf',
		os.path.join(install_path, 'etc/X11/xorg.conf'))

	# TODO: Maybe we can drop this
	# Configure ALSA
	# configure_alsa

	# Set pulse
	if os.path.exists("/usr/bin/pulseaudio-ctl"):
		target_env_call(['pulseaudio-ctl', 'normal'])

	# Save settings
	target_env_call(['alsactl', '-f', '/etc/asound.state', 'store'])

        # TODO: port mhwd script to python
        path = = '/usr/lib/calamares/modules/drivercfg/'


	mhwd_script = path + "mhwd.sh"
        #try:
        check_call(["/usr/bin/bash", mhwd_script, install_path])

	return None
