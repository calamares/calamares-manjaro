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

from subprocess import call, CalledProcessError
from libcalamares.utils import target_env_call

class PacmanController:
	def __init__(self):
		self.__operations = libcalamares.globalstorage.value("packageOperations")

	@property
	def operations(self):
		return self.__operations

	def install(self, local=False):
		if local:
			flags = "-U"
		else:
			flags = "-Sy"

		try:
			target_env_call(["pacman", flags, "--noconfirm"] + self.operations["install"])
		except CalledProcessError as e:
			libcalamares.utils.debug("Cannot install selected packages.", "pacman terminated with exit code {}.".format(e.returncode))

	def remove(self):
		try:
			target_env_call(["pacman", "-Rs", "--noconfirm"] + self.operations["remove"])
		except CalledProcessError as e:
			libcalamares.utils.debug("Cannot remove selected packages.", "pacman terminated with exit code {}.".format(e.returncode))


class ChrootController:
	def __init__(self):
		self.__root = libcalamares.globalstorage.value('rootMountPoint')
		self.__directories = libcalamares.job.configuration.get('directories', [])
		self.__requirements = libcalamares.job.configuration.get('requirements', [])
		self.__keyrings = libcalamares.job.configuration.get('keyrings', [])
		if "branch" in libcalamares.job.configuration:
			self.__branch = libcalamares.job.configuration["branch"]
		else:
			self.__branch = ""
		self.__pacman = PacmanController()

	@property
	def root(self):
		return self.__root

	@property
	def pacman(self):
		return self.__pacman

	@property
	def branch(self):
		return self.__branch

	@property
	def keyrings(self):
		return self.__keyrings

	@property
	def requirements(self):
		return self.__requirements

	@property
	def directories(self):
		return self.__directories

	def initilize(self):
		try:
			call(["pacman", "-Sy", "--noconfirm", "--cachedir", os.path.join(self.root, "var/cache/pacman/pkg"), "--root", self.root] + self.requirements)
		except CalledProcessError as e:
			libcalamares.utils.debug("Cannot install pacman.", "pacman terminated with exit code {}.".format(e.returncode))

	def copy_pacman_mmirrors_conf(self):
		if os.path.exists("/etc/resolv.conf"):
			try:
				shutil.copy2("/etc/pacman-mirrors.conf", "{!s}/etc/".format(self.root))
			except FileNotFoundError as e:
				libcalamares.utils.debug("Cannot copy pacman-mirrors.conf {}".format(e.returncode))

	def copy_resolv_conf(self):
		if os.path.exists("/etc/resolv.conf"):
			try:
				shutil.copy2("/etc/resolv.conf", "{!s}/etc/".format(self.root))
			except FileNotFoundError as e:
				libcalamares.utils.debug("Cannot copy resolv.conf {}".format(e.returncode))

	def copy_mirrorlist(self):
		if os.path.exists("/etc/pacman.d/mirrorlist"):
			try:
				shutil.copy2("/etc/pacman.d/mirrorlist", "{!s}/etc/pacman.d/".format(self.root))
			except FileNotFoundError as e:
				libcalamares.utils.debug("Cannot copy mirrorlist {}".format(e.returncode))

	def rank_mirrors(self):
		try:
			target_env_call(["pacman-mirrors", "-g", "-m", "rank"])
		except CalledProcessError as e:
			libcalamares.utils.debug("Cannot rank mirrors", "pacman-mirrors terminated with exit code {}.".format(e.returncode))

	def populate_keyring(self, keys):
		try:
			target_env_call(["pacman-key", "--populate"] + keys)
		except CalledProcessError as e:
			libcalamares.utils.debug("Cannot populate keyring", "pacman-key terminated with exit code {}.".format(e.returncode))

	def init_keyring(self):
			try:
				target_env_call(["pacman-key", "--init"])
			except CalledProcessError as e:
				libcalamares.utils.debug("Cannot init keyring", "pacman-key terminated with exit code {}.".format(e.returncode))

	def prepare(self):
		for target in self.directories:
			path = self.root + target["name"]
			if not os.path.exists(path):
				cal_umask = os.umask(0)
				libcalamares.utils.debug("Create: {}".format(path))
				#mod = oct(target["mode"])
				#libcalamares.utils.debug("Mode: {}".format(mod))
				os.makedirs(path, mode=0o755)
				os.chmod(os.path.join(self.root, "run"), 0o755)
				os.umask(cal_umask)
				if  self.branch:
					self.copy_pacman_mmirrors_conf()

				self.copy_resolv_conf()

	def run(self, rank=False):
		self.prepare()
		self.initilize()
		self.init_keyring()
		self.populate_keyring(self.keyrings)
		self.copy_mirrorlist()
		if rank is True:
			self.rank_mirrors()

		for op in self.pacman.operations.keys():
			if op == "install":
				self.pacman.install()
			elif op == "remove":
				self.pacman.remove()
			elif op == "localInstall":
				self.pacman.install(local=True)

		return None

def run():
	""" Create chroot dirs and install pacman, kernel and netinstall selection """

	targetRoot = ChrootController()

	return targetRoot.run(rank=True)
