#!/usr/bin/env python3
# encoding: utf-8
#
#   Copyright 2014, Artoo <artoo@manjaro.org>
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

import shlex

import libcalamares

from libcalamares.utils import target_env_call, debug
from subprocess import call, CalledProcessError

class MhwdController:
	def __init__(self):
		self.__root = libcalamares.globalstorage.value( "rootMountPoint" )
		self.__kernelline = call(["cat", "/proc/cmdline"])
		self.__video = ""
		self.__bus_types = libcalamares.job.configuration.get('bus_types', [])
		self.__identifiers = libcalamares.job.configuration.get('identifiers', [])
		self.__local_repo = libcalamares.job.configuration['local_repo']
		self.__repo_conf = libcalamares.job.configuration['repo_conf']

	@property
	def kernelline(self):
		return self.__kernelline

	@property
	def video(self):
		for opt in shlex.split(self.kernelline):
			if '=' not in opt:
				continue
			key, self.__video = opt.split('=', 1)
			if key == "overlay":
				return str(self.__video)

	@property
	def root(self):
		return self.__root

	@property
	def local_repo(self):
		return self.__local_repo

	@property
	def repo_conf(self):
		return self.__repo_conf

	@property
	def identifiers(self):
		return self.__identifiers

	@property
	def bus_types(self):
		return self.__bus_types

	def configure(self, bn, val):
		args = ["mhwd", "-a", bn, self.video, val]
		if self.local_repo:
			args += ["--pmconfig", self.repo_conf]

		try:
			target_env_call(args)
		except CalledProcessError as e:
			debug("Cannot configure drivers", "mhwd terminted with exit code {}.".format(e.returncode))

	def run(self):
		nids = lambda x: self.identifiers['net']
		vids = lambda x: self.identifiers['vid']
		for bus in self.bus_types:
			for idx in nids:
				self.configure(bus, idx)
			for idx in vids:
				self.configure(bus, idx)

def run():
	""" Configure the hardware """

	mhwd = MhwdController()

	return mhwd.run()
