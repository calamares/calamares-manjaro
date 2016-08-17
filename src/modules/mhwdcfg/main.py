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

from libcalamares.utils import check_target_env_call, debug

class MhwdController:
	def __init__(self):
		self.__root = libcalamares.globalstorage.value( "rootMountPoint" )
		self.__bus = libcalamares.job.configuration.get('bus', [])
		self.__identifier = libcalamares.job.configuration.get('identifier', [])
		self.__local_repo = libcalamares.job.configuration['local_repo']
		self.__repo_conf = libcalamares.job.configuration['repo_conf']
		self._driver = libcalamares.job.configuration['driver']

	@property
	def driver(self):
		return self._driver
# 		with open("/proc/cmdline") as f:
# 			for opt in f.readline().strip().split():
# 				if '=' not in opt:
# 					continue
# 				key, val = opt.split("=", 1)
# 				if key == "overlay":
# 					self._video = val
# 					return self._video
# 
# 		f.close()

	@driver.setter
	def driver(self, value):
		self._driver = value
		
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
	def identifier(self):
		return self.__identifier

	@property
	def bus(self):
		return self.__bus

	def configure(self, bt, val):
		cmd = ["mhwd"]
		if self.local_repo:
			cmd.extend(["--pmconfig", self.repo_conf])
			
		cmd.extend(["-a", bt, str(self.driver), str(val).zfill(4)])
		check_target_env_call(cmd)

	def run(self):
		debug("Driver: {}".format(self.driver))
		for b in self.bus:
			for id in self.identifier['net']:
				debug("Device ID: {}".format(str(id).zfill(4)))
				self.configure(b, id)
			for id in self.identifier['vid']:
				debug("Device ID: {}".format(str(id).zfill(4)))
				self.configure(b, id)
				
		return None

def run():
	""" Configure the hardware """

	mhwd = MhwdController()
	
	return mhwd.run()

