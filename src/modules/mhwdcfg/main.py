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

import libcalamares

from libcalamares.utils import target_env_call

class MhwdController:
	def __init__(self, root_dir):
		self._xconf = "/etc/X11/xorg.conf"
		self._video = getCmdLine(kernelline, "xdriver")
		self._nonfree = getCmdLine(kernelline, "nonfree")
		self._root = root_dir
		self._cmd = "mhwd"

	@staticmethod
	def getCmdLine(kline, arg):
		val = argparse.split(kline)

		return val

	@property
	def xconf(self):
		return self._xconf

	@property
	def video(self):
		return self._video

	@property
	def root(self):
		return self._root

	@property
	def cmd(self):
		return self._cmd

	@property
	def nonfree(self):
		return self._nonfree

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

		self.configureNetDrv()
		self.configureVideoDrv()


def run():
	""" Configure the hardware """

	rootMountPoint = libcalamares.globalstorage.value( "rootMountPoint" )

	mhwd = MhwdController(rootMountPoint)

	return mhwd.run()
