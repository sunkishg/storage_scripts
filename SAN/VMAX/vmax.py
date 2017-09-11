#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from ..subcmd import Cmd
import xml.etree.ElementTree as ET

class VMAX(object):
    """
    Class VMAX() works with EMC VMAX Storage arrays
    """

    def __init__(self, symcli_path='/usr/symcli/bin'):
        """
        :param symcli_path: Path installation of SYMCLI
        """

        self.symcli_path = symcli_path

    def __repr__(self):
        """
        :return: representation (<VMAX>).
        """

        representation = '<SAN.EMC.VMAX>'
        return representation

    def validate_args(self):
        """ Validate if the required args is declared. """

        if self.symcli_path == '':
            return 'The symcli path is required'


    def symcmd(self,command):
        retcode = Cmd(command).runcmd()
        if retcode.get('return_code', -1) == 0:
            return retcode.get('stdout', "")
        else:
            return retcode.get('stderr', "")


    def list(self):
        """docstring"""
        list_cmd = "{0}/symcfg list -output xml_e".format(self.symcli_path)
        symout = VMAX.symcmd(list_cmd)
        stuff = ET.fromstring(symout.read())
        arrays = stuff.findall('Symmetrix/Symm_Info')
        arrays_list = list()
        for item in arrays:
            arrays_list.append(item.find('symid').text)
        return arrays_list
