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

import os, shutil, subprocess, sys, re

import libcalamares

from libcalamares.utils import check_target_env_call, debug
from os.path import join

class OperationTracker:
	def __init__(self):
		self._downloaded = 0
		self._installed = 0
		self._total = 0

	@property
	def downloaded(self):
		return self._downloaded

	@downloaded.setter
	def downloaded(self, value):
		self._downloaded = value

	@property
	def installed(self):
		return self._installed

	@installed.setter
	def installed(self, value):
		self._installed = value

	@property
	def total(self):
		return self._total

	@total.setter
	def total(self, value):
		self._total = value

ON_POSIX = 'posix' in sys.builtin_module_names

class PacmanController:
	def __init__(self, root):
		self.__root = root
		self.__operations = libcalamares.globalstorage.value("packageOperations")
		self.__tracker = OperationTracker()
		self._progress = float(0)

	@property
	def tracker(self):
		return self.__tracker

	@property
	def root(self):
		return self.__root

	@property
	def operations(self):
		return self.__operations

	@property
	def progress(self):
		return self._progress

	@progress.setter
	def progress(self, value):
		self._progress = value

	def send_pg(self, counter):
		if self.tracker.total != 0:
			step = 0.05
			step += 0.95 * (counter / float(self.tracker.total))
			self.progress += step / float(self.tracker.total)
			debug("Progress: {}".format(self.progress))

		libcalamares.job.setprogress(self.progress)

	def parse_output(self, cmd):
		cal_env = os.environ
		cal_env["LC_ALL"] = "C"
		last = []

		process = subprocess.Popen(cmd, env=cal_env, bufsize=1, stdout=subprocess.PIPE, close_fds=ON_POSIX)

		for line in iter(process.stdout.readline, b''):
			pkgs = re.findall(r'\((\d+)\)', line.decode())
			dl = re.findall(r'downloading\s+(.*).pkg.tar.xz', line.decode())
			inst = re.findall(r'installing(.*)\.\.\.', line.decode())

			if pkgs:
				self.tracker.total = (int(pkgs[0]))
				debug("Number of packages: {}".format(self.tracker.total))

			if dl:
				if dl != last:
					self.tracker.downloaded += 1
					debug("Downloading: {}".format(dl[0]))
					debug("Downloaded packages: {}".format(self.tracker.downloaded))
					self.send_pg(self.tracker.downloaded)

				last = dl
			elif inst:
				self.tracker.installed += 1
				debug("Installing: {}".format(inst[0]))
				debug("Installed packages: {}".format(self.tracker.installed))
				self.send_pg(self.tracker.installed)


		if process.returncode != 0:
			process.terminate()
			return "pacman failed with error code {}.".format(process.returncode)

		return None

	def install(self, local=False):
		cachedir = join(self.root, "var/cache/pacman/pkg")
		dbdir = join(self.root, "var/lib/pacman")
		args = ["pacman", "--noconfirm"]
		if local:
			args.extend(["-U"])
		else:
			args.extend(["-Sy"])

		args.extend(["--cachedir", cachedir, "--root", self.root, "--dbpath", dbdir])
		cmd =  args + self.operations["install"]
		self.parse_output(cmd)

	def remove(self):
		args = ["chroot", self.root, "pacman", "-Rs", "--noconfirm"]
		cmd = args + self.operations["remove"]
		check_target_env_call(cmd)

	def run(self):
		for op in self.operations.keys():
			if op == "install":
				self.install()
			elif op == "localInstall":
				self.install(local=True)
			elif op == "remove":
				self.tracker.total(len(self.operations["remove"]))
				self.remove()

		return None

class ChrootController:
	def __init__(self):
		self.__root = libcalamares.globalstorage.value('rootMountPoint')
		self.__requirements = libcalamares.job.configuration.get('requirements', [])

	@property
	def root(self):
		return self.__root

	@property
	def requirements(self):
		return self.__requirements

	def make_dirs(self):
		for target in self.requirements:
			dest = self.root + target["name"]
			if not os.path.exists(dest):
				debug("Create: {}".format(dest))
				mod = int(target["mode"],8)
				debug("Mode: {}".format(oct(mod)))
				os.makedirs(dest, mode=mod)

	def prepare(self):
		cal_umask = os.umask(0)
		self.make_dirs()
		path = join(self.root, "run")
		debug("Fix permissions: {}".format(path))
		os.chmod(path, 0o755)
		os.umask(cal_umask)

	def run(self):
		self.prepare()
		pacman = PacmanController(self.root)

		return pacman.run()

def run():
	""" Create chroot dirs and install pacman, kernel and netinstall selection """

	targetRoot = ChrootController()

	return targetRoot.run()
