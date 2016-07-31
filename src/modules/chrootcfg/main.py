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

class ChrootController:
	def __init__(self, root_dir, reqs):
		self._root = root_dir
		self._pkgcache = root_dir + "/var/cache/pacman/pkg"
		self._reqdirs = reqs

	@property
	def root(self):
		return self._root

	@property
	def pkgcache(self):
		return self._pkgcache

	@property
	def reqdirs(self):
		return self._reqdirs

	def rank_mirrors(self):
		try:
			target_env_call(["pacman-mirrors",  "-g", "-m", "rank"])
		except CalledProcessError as e:
			debug("Cannot rank mirrors", "pacman-mirrors terminated with exit code {}.".format(e.returncode))


	def install(self, pkg):
		try:
			check_call(["pacman", "-Sy", "--noconfirm", "--cachedir", self.pkgcache, "--root", self.root, pkg])
		except CalledProcessError as e:
			debug("Cannot install pacman.", "pacman terminated with exit code {}.".format(e.returncode))

		try:
			target_env_call(["pacman-key", "--init"])
			target_env_call(["pacman-key", "--populate", "archlinux", "manjaro"])
		except CalledProcessError as e:
			debug("Cannot init and populate keyring", "pacman-key terminated with exit code {}.".format(e.returncode))

	def copy_pm_conf(self):
		shutil.copy2("/etc/pacman-mirrors.conf", "{!s}/etc/".format(self.root))


	def copy_mirrorlist(self):
		shutil.copy2("/etc/pacman.d/mirrorlist", "{!s}/etc/pacman.d/".format(self.root))


	def prepare(self, dirs):
		for d in dirs:
			name = self.root + d['name']
			if not os.path.exists(name):
				cal_umask = os.umask(0)

				os.makedirs(name, mode=0o755)

				run_dir = self.root + "/run"

				os.chmod(run_dir, mode=0o755)

				os.umask(cal_umask)

				self.copy_pm_conf()


	def run(self):
		self.prepare(self.reqdirs)
		self.install("pacman")
		self.copy_mirrorlist()
		self.rank_mirrors()


def run():
	""" Create chroot apifs """

	rootMountPoint = libcalamares.globalstorage.value('rootMountPoint')

	requirements = libcalamares.job.configuration.get('requirements', [])

	target = ChrootController(rootMountPoint, requirements)

	return target.run()
