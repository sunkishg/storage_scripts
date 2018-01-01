#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#

import re
import calc
import collections
from runsubcmd import Cmd
import xml.etree.ElementTree as ET

def nested_dict():
    return collections.defaultdict(nested_dict)


class VMAX(object):
    """
    Class EMC.VMAX() works with EMC VMAX Storage 1 and 2.
    Is necessary a SYMCLI installed and working well with your environment.
    For more information consult the EMC documentation.
    The default return for any command is an array:
    If command is OK:
    [return code, output]
    If command is not OK:
    [return code, error, output]
    """

    def __init__(self, symcli_path="/opt/emc/SYMCLI/bin/"):
        """
        :param symcli_path: Path installation of SYMCLI
        """

        self.symcli_path = symcli_path

    def __repr__(self):
        """
        :return: representation (<VMAX>).
        """

        representation = '<sanadmin.emc.VMAX>'
        return representation

    def validate_args(self):
        """ Validate if the required args is declared. """

        if self.symcli_path == '':
            return 'The symcli path is required'


    def symcmd(self,command='', xmlout=False):
        retcode = Cmd(command).runcmd()

        if xmlout:
            if retcode.get('return_code', -1) == 0:
                return retcode.get('stdout', '<?xml version="1.0" ?>\n<metadata>\n</metadata>')
            else:
                return '<?xml version="1.0" ?>\n<metadata>\n</metadata>'
        else:
            if retcode.get('return_code', -1) == 0:
                return retcode.get('stdout', " ")
            else:
                return retcode.get('stderr', " ")


    def get_xml_text(self, elem, tag):
        try:
            x = elem.find(tag).text
        except:
            x = 'none'
        
        return x


    def frames_list(self):
        """
        Get informations about all available Storages
        :return: the return code and list of storages
        """
        symmetrix_id_list = list()
        symcfg_list_cmd = '{0}/symcfg list -output xml_e'.format(self.symcli_path)
        symcfg_list_out = self.symcmd(command=symcfg_list_cmd, xmlout=True)
        etfst_out = ET.fromstring(symcfg_list_out)
        frames = etfst_out.findall('Symmetrix/Symm_Info')
        for item in frames:
            symmetrix_id_list.append(item.find('symid').text)

        return symmetrix_id_list


    def lspools(self,  sid='', args=''):
        """
        List all available pools on VMAX.
        :param sid: Identification of VMAX (SID)
        :param args: is optional. You can use parameters such as -thin
        :return: the return code and pools without legend.
        """

        self.validate_args()

        lspools_cmd = '{0}/symcfg -sid {1} list -pool {2}'.format(
            self.symcli_path, sid, args)

        lspools_out = Cmd(lspools_cmd).runcmd()


        if lspools_out[0] == 0:
            return lspools_out[0], lspools_out[1].split('Legend:')[0]
        else:
            return lspools_out

    def ign(self, sid='', wwn=''):
        """
        Get Initial Group Name (IGN) full output by the WWN.
        :param sid: Identification of VMAX (SID).
        :param wwn: wwn client.
        :return: array with return code and full output of IGN.
        """

        self.validate_args()

        ign_cmd = "{0}/symaccess -sid {1} -type init list -wwn {2}".format(
                self.symcli_path, sid, wwn)

        ign_out = Cmd(ign_cmd).runcmd()

        return ign_out


    def get_ign(self, sid='', wwn=''):
        """
        Get the Initiator Group Name by the WWN.
        :param sid: Identification of VMAX (SID).
        :param wwn: wwn client.
        :return: array with return code and only Initiator Group Name.
        """

        self.validate_args()

        ign_out = self.ign(sid, wwn)

        if ign_out[0] == 0:
            # spliting in lines
            ign_out_splitted = ign_out[1].split('\n')
            # cleaning the empty elements (filter) and removing whitespaces
            ign_out_splitted = filter(None, ign_out_splitted)[-1].split()[0]
            return ign_out[0], ign_out_splitted
        else:
            return ign_out

    def mvn(self, sid='', ign=''):
        """
        Get the Mask View Names with full informations using the Initiator
        Group Name.
        :param sid: Identification of VMAX (SID).
        :param ign: Initiator Group Name. check get_ign() or ign().
        :return: the return code and full Mask View Name informations.
        """

        mvn_cmd = "{0}/symaccess -sid {1} -type init show {2}".format(
            self.symcli_path, sid, ign)

        mvn_out = Cmd(mvn_cmd).runcmd()

        return mvn_out


    def get_mvn(self, sid='', ign=''):
        """
        Get the Mask View Names by Initiator Group Name.
        :param sid: Identification of VMAX (SID).
        :param ign: Initiator Group Name. check ign() or get_ign().
        :return: the return code and only Mask View Name.
        """
        self.validate_args()

        mvn_out = self.mvn(sid, ign)

        if mvn_out[0] == 0:
            mvn_splitted = mvn_out[1].split(
                    'Masking View Names'
            )[1].split(
                    '{'
            )[1].split(
                    '}')[0]

            mvn_array = [line for line in mvn_splitted.split('\n') if
                         line.strip() != '']

            mvn_out = [mvn_out[0]]
            for line in mvn_array:
                mvn_out.append(line.strip().split()[0])

            return mvn_out

        else:
            return mvn_out

    def sgn(self, sid='', mvn=''):
        """
         Get the Storage Group Name by the Mask View Name.
         :param sid: Identification of VMAX (SID).
         :param mvn: Mask View Name check mvn() or get_mvn().
         :return: the return code and full output Storage Group Name.
         """

        self.validate_args()

        sgn_cmd = '{0}/symaccess -sid {1} show view {2}'.format(
            self.symcli_path, sid, mvn)

        sgn_out = Cmd(sgn_cmd).runcmd()

        return sgn_out

    def get_sgn(self, sid='', mvn=''):
        """
         Get the Storage Group Name by the Mask View Name.
         :param sid: Identification of VMAX (SID).
         :param mvn: Mask View Name check sgn() or get_sgn().
         :return: the return code and only Storage Group Name.
         """
        self.validate_args()

        sgn_out = self.sgn(sid, mvn)

        if sgn_out[0] == 0:
            sgn_out_splitted = sgn_out[1].split('Storage Group Name ')[1]
            sgn_out_splitted = sgn_out_splitted.split()[1]

            return sgn_out[0], sgn_out_splitted
        else:
            return sgn_out

    def create_dev(self, sid='', count=0, lun_size=0, member_size=0,
                   lun_type='', pool='', sgn='', action='prepare'):
        """
        Create device(s) for Storage Group Name.
        :param sid: Identification of VMAX (SID)
        :param count: number of devices
        :param lun_size: the size of LUN (GB) Ex: 100
        :param member_size: Member size (only for lun_type=meta)
        :param lun_type: meta or regular
        :param pool: the pool for allocation (use lspools() to check)
        :param sgn: Storage Group Name
        :param action: strings 'prepare'(default) or 'commit'
        :return: returns the return code and output of allocation
        """

        # convert size GB to CYL
        lun_size = calc.gb2cyl(int(lun_size))
        member_size = calc.gb2cyl(int(member_size))

        # args validation
        self.validate_args()
        if (action != 'prepare') and (action != 'commit'):
            return [1, 'The parameter action need to be prepare or commit.']

        if lun_type == 'meta':
            create_dev_cmd = '{0}/symconfigure -sid {1} -cmd \"' \
                             'create dev count={2}, size={3} CYL, ' \
                             'emulation=FBA, config=TDEV, ' \
                             'meta_member_size={4} CYL, ' \
                             'meta_config=striped, binding to pool={5}, ' \
                             'sg={6} ;\" {7} -v -nop' \
                .format(self.symcli_path,
                        sid,
                        count,
                        lun_size,
                        member_size,
                        pool,
                        sgn,
                        action)

        elif lun_type == 'regular':

            create_dev_cmd = '{0}/symconfigure -sid {1} -cmd \"' \
                             'create dev count={2}, size={3} CYL, ' \
                             'emulation=FBA , config=TDEV , ' \
                             'binding to pool={4}, sg={5} ;\" {6} -v -nop' \
                .format(self.symcli_path,
                        sid,
                        count,
                        lun_size,
                        pool,
                        sgn,
                        action)

        else:
            return [1, 'argument dev_type is not valid. use: meta or regular']

        create_dev_out = Cmd(create_dev_cmd).runcmd()

        return create_dev_out


    def sg_to_dict(self, symmid, server_name):
        sgs = nested_dict()
        symsg_list_cmd = '{0}/symsg -sid {1} list -v -output xml_e'.format(self.symcli_path, symmid)
        symsg_list_out = self.symcmd(command=symsg_list_cmd, xmlout=True)
        sgtree = ET.fromstring(symsg_list_out)
        #for each SG
        for elem in sgtree.findall('SG'):
            # get Storage Group Name
            sg_name  = self.get_xml_text(elem, 'SG_Info/name')
            # get some SG informations
            sgs[sg_name]['symmid'] = self.get_xml_text(elem, 'SG_Info/symid')
            sgs[sg_name]['slo_name'] = self.get_xml_text(elem, 'SG_Info/SLO_name')
            sgs[sg_name]['workload'] = self.get_xml_text(elem, 'SG_Info/Workload')
            sgs[sg_name]['srp_name'] = self.get_xml_text(elem, 'SG_Info/SRP_name')
            sgs[sg_name]['hostlimit'] = self.get_xml_text(elem, 'SG_Info/HostIOLimit_status')
            sgs[sg_name]['dynamic'] = self.get_xml_text(elem, 'SG_Info/Dynamic_Distribution')
            sgs[sg_name]['iops'] = self.get_xml_text(elem, 'SG_Info/HostIOLimit_max_io_sec')
            sgs[sg_name]['mbs'] = self.get_xml_text(elem, 'SG_Info/HostIOLimit_max_mb_sec')
            sgs[sg_name]['mv'] = self.get_xml_text(elem, 'SG_Info/Masking_views')
            # initialize list of sgs parent and childs
            sgs[sg_name]['child'] = list()
            sgs[sg_name]['parent'] = list()

            # populate lists of SGs parent and childs
            for elem_sg_group in elem.findall('SG_Info/SG_group_info/SG'):
                relation     = self.get_xml_text(elem_sg_group, 'Cascade_Status')
                sg_group_name = self.get_xml_text(elem_sg_group, 'name')
                if relation == 'IsChild':
                    sgs[sg_name]['child'].append(sg_group_name)
                elif relation == 'IsParent':
                    sgs[sg_name]['parent'].append(sg_group_name)

            # Populate the 'relation' with S, P or C
            # S = standalone
            # P = Parent
            # C = Child
            if  not sgs[sg_name]['parent'] and not sgs[sg_name]['child']:
                sgs[sg_name]['relation'] = 'S'
            elif sgs[sg_name]['parent']:
                sgs[sg_name]['relation'] = 'C'
            elif sgs[sg_name]['child']:
                sgs[sg_name]['relation'] = 'P'

            # Populate the dictionary key 'luns' with lunid: its_size
            for lun in elem.findall('DEVS_List/Device'):
                lun_id = self.get_xml_text(lun, 'dev_name')
                lun_mb = self.get_xml_text(lun, 'megabytes')
                sgs[sg_name]['luns'][lun_id] = int(lun_mb) # store the size as int

            # Get the number of luns
            sgs[sg_name]['num_luns'] = len(sgs[sg_name]['luns'])
            # Sum all luns size and store value in GB
            sgs[sg_name]['total_size'] = sum(sgs[sg_name]['luns'].values()) // 1024

            #get the total Number of luns
            sgs[sg_name]['total_luns'] = sgs[sg_name]['luns'].keys()

        sg_relation = list()
        for sg in sgs:
            sg_name = sg
            # SG is standalone
            if not sgs[sg]['parent'] and not sgs[sg]['child']:
                sg_relation.append([sg_name])
            # If SG does not have a Parent, ie, it is parent
            # so, get the list of childs
            elif not sgs[sg]['parent']:
                # convert the list of child to string
                x = ",".join(sgs[sg]['child'])
                # add the sg_name (parent) in the beginning of string
                x = sg_name + ',' + x
                # convert string to list
                sg_relation.append(x.split(","))
            else:
                pass

        header = list()
        for i in sorted(sg_relation):
            # for each sg
            for sg_name in i:
                row = list()
                if sgs[sg_name]['relation'] == 'P':
                    row.append(sg_name)
                elif sgs[sg_name]['relation'] == 'S':
                    row.append(sg_name)
                else:
                    row.append(sg_name)
                row.append(sgs[sg_name]['relation'])
                # row.append(sgs[sg_name]['symmid'])
                row.append(str(sgs[sg_name]['num_luns']))
                row.append(str(sgs[sg_name]['total_size']))
                #row.append(sgs[sg_name]['srp_name'])
                row.append(sgs[sg_name]['slo_name'])
                row.append(sgs[sg_name]['workload'])
                # row.append(sgs[sg_name]['hostlimit'])
                # row.append(sgs[sg_name]['iops'])
                # row.append(sgs[sg_name]['mbs'])
                # row.append(sgs[sg_name]['dynamic'])
                if sgs[sg_name]['relation'] == 'P':
                    row.append(sgs[sg_name]['mv'])
                elif sgs[sg_name]['relation'] == 'S':
                    row.append(sgs[sg_name]['mv'])
                else:
                    row.append(sgs[sg_name]['mv'])
                header.append(",".join(row))
        out_list = list()
        for line in header:
            if server_name in line:
                # print(line)
                data = line.split(',')
                if data[1] == 'S' or data[1] == 'P':
                    server_sg_name = data[0]
                    total_lun_nos = ','.join(sgs[server_sg_name]['total_luns'])
                    symcfg_list_tdev = '{0}/symcfg -sid {1} list -tdev -detail -gb -dev {2} -output xml_e'.format(self.symcli_path, symmid, total_lun_nos)
                    symcfg_tdev_out = self.symcmd(command=symcfg_list_tdev, xmlout=True)
                    symcfg_tdev_xmlout = ET.fromstring(symcfg_tdev_out)
                    recods = symcfg_tdev_xmlout.findall('Symmetrix/ThinDevs/Totals')
                    for item in recods:
                        total_tracks_gb = item.find('total_tracks_gb').text
                        total_alloc_tracks_gb = item.find('total_alloc_tracks_gb').text
                        total_alloc_percent = item.find('total_alloc_percent').text
                        out_list.append("{0},{1},{2},{3}".format(line, total_tracks_gb, total_alloc_tracks_gb, total_alloc_percent))
                else:
                    server_sg_name = data[0]
                    lun_size_list = sgs[server_sg_name]['luns'].values()
                    lun_size_dict = dict()
                    for l in lun_size_list:
                        l = l // 1024
                        if l in lun_size_dict:
                            lun_size_dict[l] += 1
                        else:
                            lun_size_dict[l] = 1

                    out_list.append("{0},{1}".format(line, lun_size_dict))
        return out_list


    def vmax3_create_dev(self, sid='', count=0, size=0, storage_group='', action='prepare'):
        # args validation
        self.validate_args()
        if (action != 'prepare') and (action != 'commit'):
            return [1, 'The parameter action need to be prepare or commit.']

        create_tdev_cmd = '{0}/symconfigure -sid {1} -cmd "Create dev count={2},size={3} GB sg={4}, emulation=FBA,  config=tdev;" -v -nop {5}'.format(self.symcli_path, sid, count, size, storage_group, action)
        create_tdev_out = self.symcmd(command=symsg_list_cmd)
        return create_tdev_out