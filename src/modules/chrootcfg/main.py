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
from libcalamares.utils import target_env_call, check_target_env_call

class ChrootController:
	def __init__(self):
		self.__root = libcalamares.globalstorage.value('rootMountPoint')
		self.__cache = os.path.join(self.__root, "var/cache/pacman/pkg")
		self.__requirements = libcalamares.job.configuration.get('requirements', [])
		self.__packages = libcalamares.job.configuration.get('packages', [])

	@property
	def root(self):
		return self.__root

	@property
	def packages(self):
		return self.__packages

	@property
	def cache(self):
		return self.__cache

	@property
	def requirements(self):
		return self.__requirements

	def install(self, pkg):
		try:
			check_call(["pacman", "-Sy", "--noconfirm", "--cachedir", self.cache, "--root", self.root, pkg])
		except CalledProcessError as e:
			libcalamares.utils.debug("Cannot install pacman.", "pacman terminated with exit code {}.".format(e.returncode))

	def copy_pacmmirrors_conf(self):
		shutil.copy2("/etc/pacman-mirrors.conf", "{!s}/etc/".format(self.root))


	def copy_mirrorlist(self):
		shutil.copy2("/etc/pacman.d/mirrorlist", "{!s}/etc/pacman.d/".format(self.root))

	def rank_mirrors(self):
		try:
			target_env_call(["pacman-mirrors", "-g", "-m", "rank"])
		except CalledProcessError as e:
			libcalamares.utils.debug("Cannot rank mirrors", "pacman-mirrors terminated with exit code {}.".format(e.returncode))

	def init_keyrings(self):
			try:
				target_env_call(["pacman-key", "--init"])
				target_env_call(["pacman-key", "--populate", "archlinux", "manjaro"])
			except CalledProcessError as e:
				libcalamares.utils.debug("Cannot init and populate keyring", "pacman-key terminated with exit code {}.".format(e.returncode))

	def prepare(self):
		for d in self.requirements:
			path = self.root + d['directory']
			if not os.path.exists(path):
				cal_umask = os.umask(0)
				libcalamares.utils.debug("Create {}.".format(d['directory']))
				os.makedirs(path, mode=0o755)
				os.chmod(os.path.join(self.root, "run"), 0o755)
				os.umask(cal_umask)
				self.copy_pacmmirrors_conf()

	def run(self):
		self.prepare()
		for p in self.packages:
			self.install(p)
			if p == "pacman":
				self.init_keyrings()
				self.copy_mirrorlist()
				self.rank_mirrors()


		return None


def run():
	""" Create chroot apifs and install pacman and kernel """

	targetRoot = ChrootController()

	return targetRoot.run()
