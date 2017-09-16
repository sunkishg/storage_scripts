#!/usr/bin/env python
# -*- coding: utf-8 -*-
#


from run_command import Cmd
from re import search


class Netapp(object):
	"""docstring"""
	
	def __init__(self,filer):
		"""docstring"""
		self.filer = filer

	def processout(command):
		"""docstring"""
		output = Cmd(command).runcmd()
		return output.get('stdout', '')

	def volspace(self):
		"""docstring"""
		volspace_dict = dict()
		volspace_command = "ssh storageops@{0} df -g".format(self.filer)
		volspace_output = self.processout(volspace_command)

		if volspace_output == '':
			return {'none': "yes"}
		else:
			for volline in volspace_output.splitlines():
				voldata = volline.split()
				if search('snapshot', volline) or search('snap reserve', volline) or search('Filesystem', volline) or len(voldata) < 4 : continue
				volname = voldata[0].split("/")[2]
				totalspace = voldata[1].split("GB")[0]
				usedspace = voldata[2].split("GB")[0]
				availspace = voldata[3].split("GB")[0]
				capacity = voldata[4].split("%")[0]
				volspace_dict[volname] = {'total': totalspace, 'used': usedspace, 'avail': availspace, 'cap': capacity}
		return volspace_dict


	def volinode(self):
		"""docstring"""
		volinode_dict = dict()
		volinode_command = "ssh storageops@{0} df -i".format(self.filer)
		volinode_output = self.processout(volinode_command)

		if volinode_output == '':
			return {'none': "yes"}
		else:
			for indline in volinode_output.splitlines():
				inddata = indline.split()
				if search("Filesystem", indline) or len(inddata) < 3: continue
				volume = inddata[0].split("/")[2]
				iused = inddata[1]
				ifree = inddata[2]
				icap = inddata[3].split("%")[0]
				volinode_dict[volume] = {'iused': iused, 'ifree': ifree, 'icap': icap}
			return volinode_dict

	def aggr(self):
		"""docstring"""
		aggr_dict = dict()
		aggr_command = "ssh storageops{0} df -Ag".format(self.filer)
		aggr_output = self.processout(aggr_command)

		if aggr_output == '':
			return {'none': "yes"}
		else:
			for aggrline in aggr_output.splitlines():
				aggrdata = aggrline.split()
				if search('snapshot', aggrline) or search('snap reserve', aggrline) or search('Aggregate', aggrline) or len(aggrdata) < 4 : continue
				aggrname = aggrdata[0]
				total = aggrdata[1].split("GB")[0]
				used = aggrdata[2].split("GB")[0]
				avail = aggrdata[3].split("GB")[0]
				aggrcap = aggrdata[4].split("%")[0]
				aggr_dict[aggrname] = {'total': total, 'used': used, 'avail': avail, 'aggrcap': aggrcap}
			return aggr_dict

