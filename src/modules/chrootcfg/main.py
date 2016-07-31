#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

import os
import shutil
import libcalamares
import subprocess

from subprocess import check_call, CalledProcessError
from libcalamares.utils import target_env_call

def rank_mirrors():
	try:
		target_env_call(["pacman-mirrors",  "-g", "-m", "rank"])
	except CalledProcessError as e:
		debug("Cannot rank mirrors", "pacman-mirrors terminated with exit code {}.".format(e.returncode))


def install(root_dir, pkg):
	cache_dir = root_dir + "/var/cache/pacman/pkg"

	try:
		check_call(["pacman", "-Sy", "--noconfirm", "--cachedir", cache_dir, "--root", root_dir, pkg])
	except CalledProcessError as e:
		return "Cannot install pacman.", "pacman terminated with exit code {}.".format(e.returncode)

	try:
		target_env_call(["pacman-key", "--init"])
		target_env_call(["pacman-key", "--populate", "archlinux", "manjaro"])
	except CalledProcessError as e:
		debug("Cannot init and populate keyring", "pacman-key terminated with exit code {}.".format(e.returncode))


def prepare(root_dir, dirs):

	for d in dirs:
		name = root_dir + d['name']
		if not os.path.exists(name):
			cal_umask = os.umask(0)

			os.makedirs(name, mode=0o755)

			run_dir = root_dir + "/run"

			os.chmod(run_dir, mode=0o755)

			os.umask( cal_umask )

			shutil.copy2("/etc/pacman-mirrors.conf", "{!s}/etc/".format(root_dir))



def run():
	""" Create chroot apifs """

	rootMountPoint = libcalamares.globalstorage.value('rootMountPoint')

	requirements = libcalamares.job.configuration.get('requirements', [])

	prepare(rootMountPoint, requirements)

	install(rootMountPoint, "pacman")

	rank_mirrors()

	return None
