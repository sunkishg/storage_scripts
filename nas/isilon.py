#!/usr/bin/env python
# -*- coding: utf-8 -*-
#


from run_command import Cmd
from calc import Cal
from re import search
from json import loads
from math import ceil


class Isilon(object):
	"""docstring"""

	def __init__(self,cluster):
		"""docstring"""
		self.cluster = cluster


	def processout(command):
		"""docstring"""
	output = Cmd(command).runcmd()
	return output.get('stdout', '')

	def quotas(self):
		"""docstring"""
		quota_dict = dict()
		quota_cmd = "ssh root@{0} '/usr/bin/isi quota quotas list --format=json'".format(self.cluster)
		quota_output = self.processout(quota_cmd)
		try:
			quota_jsondump = loads(quota_output)
		except:
			quota_jsondump = loads("{}")
		if len(quota_jsondump) == 0:
			return {'none': "yes"}
		else:
			for quota in quota_jsondump:
				path = quota.get('path', None)
				if path not None:
					hardquota = Cal(quota['thresholds']['hard']).convert_units()
					advisoryquota = Cal(quota['thresholds']['advisory']).convert_units()
					ussage = Cal(quota['usage_derived']).convert_units()
					availspace = ceil((hardquota - ussage) * 100) / 100
					filesyscap = ceil(((ussage / hardquota) * 100) * 100) / 100
					quota_dict[path] = {'total': hardquota, 'used': ussage, 'avail': availspace, 'cap': filesyscap, 'advisory': advisoryquota}

		return quota_dict

