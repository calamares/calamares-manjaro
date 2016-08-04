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

import os
import subprocess
import shlex

import libcalamares

from libcalamares.utils import target_env_call, debug
from subprocess import call, CalledProcessError

class MhwdController:
	def __init__(self):
		self.__video = ""
		self.__buses = job.configuration.get('buses', [])
		self.__hwids = job.configuration.get('hwids', [])
		self.__islocal = job.configuration['local']
		self.__repo = job.configuration['repo']
		self.__root = globalstorage.value( "rootMountPoint" )
		self.__kernelline = call(["cat", "/proc/cmdline"])

	@property
	def kernelline(self):
		return self.__kernelline

	@property
	def video(self):
		opts = shlex.split(self.kernelline)
		for op in opts:
			if '=' not in op:
				continue

			key, val = op.split('=', 1)
			if key == "overlay":
				self.__video == str(val)
				
		return self.__video

	@property
	def root(self):
		return self.__root
	
	@property
	def islocal(self):
		return self.__islocal
	
	@property
	def repo(self):
		return self.__repo
	
	@property
	def hwids(self):
		return self.__hwids
	
	@property
	def buses(self):
		return self.__buses

	def configure(self, bus, id):
		args = ["mhwd", "-a", bus, self.video, id]
		if self.local:
			args += ["--pmconfig", self.repo]
		
		try:
			target_env_call(args)
		except CalledProcessError as e:
			debug("Cannot configure drivers", "mhwd terminted with exit code {}.".format(e.returncode))

	def run(self):
		for b in self.buses:
			self.configure(self.buses[b], 0300)
			self.configure(self.buses[b], 0200)

def run():
	""" Configure the hardware """

	mhwd = MhwdController()

	return mhwd.run()
