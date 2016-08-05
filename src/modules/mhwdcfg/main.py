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

import libcalamares

from libcalamares.utils import target_env_call, debug
from subprocess import CalledProcessError

class MhwdController:
	def __init__(self):
		self.__root = libcalamares.globalstorage.value( "rootMountPoint" )
		self.__bus_types = libcalamares.job.configuration.get('bus_types', [])
		self.__identifiers = libcalamares.job.configuration.get('identifiers', [])
		self.__local_repo = libcalamares.job.configuration['local_repo']
		self.__repo_conf = libcalamares.job.configuration['repo_conf']
		self.__video = None

	@property
	def video(self):
		f = open("/proc/cmdline")
		for opt in f.readline().strip().split():
			if '=' not in opt:
				continue
			key, val = opt.split("=", 1)
			if key == "overlay":
				self.__video = val
				return self.__video
				
		f.close()

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
		
	def configure(self, bus, val):
		args = ["mhwd", "-a", bus, self.video, val]
		if self.local_repo:
			args += ["--pmconfig", self.repo_conf]

		try:
			target_env_call(args)
		except CalledProcessError as e:
			debug("Cannot configure drivers", "mhwd terminted with exit code {}.".format(e.returncode))

	def run(self):
		debug("Video driver: {}".format(self.video))
		for bus in self.bus_types:
			for idx in self.identifiers['net']:
				self.configure(bus, str(idx))
			for idx in self.identifiers['vid']:
				self.configure(bus, str(idx))

def run():
	""" Configure the hardware """

	mhwd = MhwdController()

	return mhwd.run()

