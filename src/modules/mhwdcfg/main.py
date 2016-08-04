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
import shutil
import argparse
import shlex

import libcalamares
import libcalamares.globalstorage

from libcalamares.utils import target_env_call

class MhwdController:
	def __init__(self):
		self._xconf = "/etc/X11/xorg.conf"
		self.__videodrv = ""
		self.__drvtype = ""
		self.__root = globalstorage.value( "rootMountPoint" )
		self.__cmd = "mhwd"
		self.__kernelcmdline = subprocess.call(["cat", "/proc/cmdline"])

	@property
	def kernelcmdline(self):
		return self.__kernelcmdline
			
	@property
	def xconf(self):
		return self.__xconf

	@property
	def videodrv(self):
		return self.__videodrv

	@videodrv.setter
	def videodrv(self, drv):
		self.__videodrv = drv
		
	@property
	def root(self):
		return self.__root

	@property
	def cmd(self):
		return self.__cmd

	@property
	def drvtype(self):
		return self.__drvtype
	
	@drvtype.setter
	def drvtype(self, val):
		self.__drvtype = val
	
	def get_cmdline(self, key):
			options = shlex.split(self.kernelcmdline)
			params = {}
			for arg in options:
				if '=' not in arg:
					continue
				
				key, val = arg.split('=', 1)
				params[key] = val
				
				return params
			
	def configureNetDrv(self):
		target_env_call([self.cmd, "--auto", "pci", "free", 0200])
		target_env_call([self.cmd, "--auto", "pci", "free", 0280])

	def configureVideoDrv(self):
		
		if self.nonfree = "yes" or self.nonfree = "true":
			if self.video = "vesa":
				target_env_call([self.cmd, "--install", "pci", "video", "video-vesa"])
			else:
				target_env_call([self.cmd, "--auto", "pci", "video", "nonfree", 0300])
		else:
			if self.video = "vesa":
				target_env_call([self.cmd, "--install", "pci", "video", "video-vesa"])
			else:
				target_env_call([self.cmd, "--auto", "pci", "video", "free", 0300])

	def run(self):
		# Copy generated xorg.xonf to target
		if os.path.exists(self.xconf):
			shutil.copy2(self.xconf, os.path.join(self.root, 'etc/X11/xorg.conf'))
			
		#self.videodrv(self.get_cmdline("vga"))
		self.drvtype(self.get_cmdline("overlay"))
		self.configureNetDrv()
		self.configureVideoDrv()


def run():
	""" Configure the hardware """

	mhwd = MhwdController()

	return mhwd.run()
