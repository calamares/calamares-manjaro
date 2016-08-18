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

import libcalamares, glob, os, shutil

from libcalamares.utils import check_target_env_call, debug

class MhwdController:
	def __init__(self):
		self.__root = libcalamares.globalstorage.value( "rootMountPoint" )
		self.__bus = libcalamares.job.configuration.get('bus', [])
		self.__identifier = libcalamares.job.configuration.get('identifier', [])
		self.__local = libcalamares.job.configuration['local']
		self._driver = libcalamares.job.configuration['driver']

	@property
	def driver(self):
		return self._driver

	@driver.setter
	def driver(self, value):
		self._driver = value
		
	@property
	def root(self):
		return self.__root

	@property
	def local(self):
		return self.__local

	@property
	def identifier(self):
		return self.__identifier
	
	@property
	def bus(self):
		return self.__bus
	
	def copy_packages(self):
		dest = os.path.join(self.root, "var/cache/pacman/pkg/")
		for file in glob.glob("/opt/live/pkgs/*.pkg.tar.xz"):
				shutil.copy(file, dest)
		
	def configure(self, bus, id):
		cmd = ["mhwd", "-a", bus, str(self.driver), str(id).zfill(4)]
		if self.local:
			self.copy_packages()

		check_target_env_call(cmd)
				
	def run(self):
		debug("Driver: {}".format(self.driver))
		for b in self.bus:
			for id in self.identifier['net']:
				debug("Device ID: {}".format(str(id).zfill(4)))
				self.configure(b, id)
			for id in self.identifier['video']:
				debug("Device ID: {}".format(str(id).zfill(4)))
				self.configure(b, id)
				
		return None

def run():
	""" Configure the hardware """

	mhwd = MhwdController()
	
	return mhwd.run()
