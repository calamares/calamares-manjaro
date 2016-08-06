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

import os
import shutil
import libcalamares

from subprocess import call, CalledProcessError
from libcalamares.utils import target_env_call, debug

class PacmanController:
	def __init__(self):
		self.__operations = libcalamares.globalstorage.value("packageOperations")

	@property
	def operations(self):
		return self.__operations

	def run(self):
		for op in self.operations.keys():
			if op == "install":
				self.install()
			elif op == "remove":
				self.remove()
			elif op == "localInstall":
				self.install(local=True)

		return None

	def install(self, local=False):
		if local:
			flags = "-U"
		else:
			flags = "-Sy"

		try:
			target_env_call(["pacman", flags, "--noconfirm"] + self.operations["install"])
		except CalledProcessError as e:
			debug("Cannot install selected packages.", "pacman terminated with exit code {}.".format(e.returncode))

	def remove(self):
		try:
			target_env_call(["pacman", "-Rs", "--noconfirm"] + self.operations["remove"])
		except CalledProcessError as e:
			debug("Cannot remove selected packages.", "pacman terminated with exit code {}.".format(e.returncode))


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
		self.__umask = os.umask(0)

	@property
	def root(self):
		return self.__root

	@property
	def umask(self):
		return self.__umask

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
			debug("Cannot install pacman.", "pacman terminated with exit code {}.".format(e.returncode))

	def copy_file(self, file):
		if os.path.exists(os.path.join("/",file)):
			try:
				shutil.copy2(os.path.join("/",file), os.path.join(self.root, file))
			except FileNotFoundError as e:
				debug("Cannot copy {}".format(os.path.join("/",file)))

	def rank_mirrors(self):
		try:
			target_env_call(["pacman-mirrors", "-g", "-m", "rank", "-b", self.branch])
		except CalledProcessError as e:
			debug("Cannot rank mirrors", "pacman-mirrors terminated with exit code {}.".format(e.returncode))

	def populate_keyring(self):
		try:
			target_env_call(["pacman-key", "--populate"] + self.keyrings)
		except CalledProcessError as e:
			debug("Cannot populate keyring", "pacman-key terminated with exit code {}.".format(e.returncode))

	def init_keyring(self):
			try:
				target_env_call(["pacman-key", "--init"])
			except CalledProcessError as e:
				debug("Cannot init keyring", "pacman-key terminated with exit code {}.".format(e.returncode))

	def make_dirs(self):
		for target in self.directories:
			dir = self.root + target["name"]
			if not os.path.exists(dir):
				debug("Create: {}".format(dir))
				mod = int(target["mode"],8)
				debug("Mode: {}".format(oct(mod)))
				os.makedirs(dir, mode=mod)

	def prepare(self):
		self.make_dirs()
		path = os.path.join(self.root, "run")
		debug("Fix permissions: {}".format(path))
		os.chmod(path, 0o755)
		os.umask(self.umask)
		if self.branch:
			self.copy_file('etc/pacman-mirrors.conf')

		self.copy_file('etc/resolv.conf')

	def run(self, rank=False):
		self.prepare()
		self.initilize()
		self.init_keyring()
		self.populate_keyring()
		self.copy_file('etc/pacman.d/mirrorlist')
		if rank is True:
			self.rank_mirrors()

		return self.pacman.run()

def run():
	""" Create chroot dirs and install pacman, kernel and netinstall selection """

	targetRoot = ChrootController()

	return targetRoot.run(rank=True)
