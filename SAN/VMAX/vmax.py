#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""docstring"""

import re
from subcmd import Cmd
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
        #print retcode
        if retcode.get('return_code', -1) == 0:
            return retcode.get('stdout', '<?xml version="1.0" ?>\n<metadata>\n</metadata>')
        else:
            return retcode.get('stdout', '<?xml version="1.0" ?>\n<metadata>\n</metadata>')


    def list(self):
        """docstring"""
        list_cmd = "{0}/symcfg list -output xml_e".format(self.symcli_path)
        symout = self.symcmd(list_cmd)
        stuff = ET.fromstring(symout)
        arrays = stuff.findall('Symmetrix/Symm_Info')
        arrays_list = list()
        for item in arrays:
            arrays_list.append(item.find('symid').text)
        return arrays_list

    def faports(self,array,director):
        """docstring"""
        cmd = "{0}/symcfg list -fa all -port -output xml_e -sid {1}".format(self.symcli_path, array)
        symout = self.symcmd(list_cmd)
        stuff = ET.fromstring(symout)
        fas = stuff.findall('Symmetrix/Director/Dir_Info')
        ports = stuff.findall('Symmetrix/Director/Port/Port_Info')

        for i in ports:
            port = i.find('port').text
            port_status = i.find('port_status').text
            portlist.append("{0}-{1}".format(port, port_status))

        for item in fas:
            fa = item.find('id').text.split('-')[1]
            portnos = item.find('ports').text
            for i in range(int(portnos)):
                fas_list.append(fa)

        zipdata = zip(fas_list,portlist)
        for n in zipdata:
            falist.append("{0}:{1}".format(n[0], n[1]))

        del fas_list, portlist, zipdata

        # rawdata = [line.split(';')[0] for line in falist if re.findall('4D', line) if line.split(";")[1] == 'Online'] 
        dirstatus = [line for line in falist if re.findall('^{}'.format(director), line)]
        return dirstatus


    def devmask_login_record(self,array,dirname):
        """docstring"""
        arrays_dict = dict()
        wwns_dict = dict()
        results = {'error': [],'goodout': []}
        cmd = "{0}/symaccess list logins -output xml_e -sid {1}".format(self.symcli_path, array)
        symout = self.symcmd(cmd)
        stuff = ET.fromstring(symout)
        login_recods = stuff.findall('Symmetrix/Devmask_Login_Record')
        # wwn_Login_records = stuff.findall('Symmetrix/Devmask_Login_Record/Login')

        for item in login_recods:
            director = item.find('director').text.split('-')[1]
            port = item.find('port').text
            dirport = "{0}:{1}".format(director, port)
            arrays_dict[dirport] = dict()
            login = item.findall('Login')
            for pwwn in login:
                originator_port_wwn = pwwn.find('originator_port_wwn').text
                logged_in = pwwn.find('logged_in').text
                on_fabric = pwwn.find('on_fabric').text
                if logged_in == 'Yes' and on_fabric == 'Yes':
                    wwns_dict.setdefault(originator_port_wwn, []).append(dirport)
                    arrays_dict[dirport][originator_port_wwn] = dict()

        for faport,values in sorted(arrays_dict.items()):
            if re.search('^{0}'.format(dirname),faport):
                for wwn,wwn_info in values.items():
                    wwncmd = "{0}/symaccess -sid {1} list -type init -wwn {2} -output xml_e".format(self.symcli_path, array, wwn)
                    wwnout =  self.symcmd(wwncmd)
                    wwninfo = ET.fromstring(wwnout)
                    wwndata = wwninfo.findall('Symmetrix/Initiator_Group/Group_Info')
                    for item in wwndata:
                        initiator_group_name = item.find('group_name').text
                        mask_view_name = item.find('Mask_View_Names/view_name').text

                        mv_cmd = "{0}/symaccess -sid {1} show view {2} -output xml_e".format(self.symcli_path, array, mask_view_name.split()[0])
                        ig_cmd = "{0}/symaccess -sid {1} show {2} -type init -output xml_e".format(self.symcli_path, array, initiator_group_name.split()[0])
                        
                        mv_out = self.symcmd(mv_cmd)
                        ig_out = self.symcmd(ig_cmd)

                        ig_info = ET.fromstring(ig_out)
                        ig_data = ig_info.findall('Symmetrix/Initiator_Group/Group_Info/Initiator_List/Initiator')
                        
                        node_wwn = list()
                        for nwwn in ig_data:
                            alter_wwn = nwwn.find('wwn').text
                            if alter_wwn != wwn:
                                node_wwn.append(alter_wwn)
                        
                        mv_info = ET.fromstring(mv_out)
                        pg_data = mv_info.findall('Symmetrix/Masking_View/View_Info/port_info/Director_Identification')
                        pg_list = list()
                        for item in pg_data:
                            pg_dir = item.find('dir').text
                            pg_port = item.find('port').text
                            pg_dirport = "{0}:{1}".format(pg_dir.split('-')[1],pg_port)
                            pg_list.append(pg_dirport)

                        arrays_dict[faport][wwn] = {'mask_view_name': mask_view_name, 'initiator_group_name': initiator_group_name, 'alter_wwn': node_wwn, 'pg_list': pg_list}

        for dirport,wwndict in arrays_dict.items():
            if re.search('^{0}'.format(dirname), dirport):
                for pwwn,wwninfo in wwndict.items():
                    alter_wwn = wwninfo.get('alter_wwn',['0'])
                    pg_list = wwninfo.get('pg_list',['0'])
                    initiator_group_name = wwninfo.get('initiator_group_name','Not found')
                    mask_view_name = wwninfo.get('mask_view_name','Not found')
                    if alter_wwn == ['0'] or pg_list == ['0'] or initiator_group_name == 'Not found' or mask_view_name == 'Not found':
                        error_string = "{0},{1},Not found,Not found,Not found,Not found".format(dirport, pwwn)
                        results.setdefault('error', []).append(error_string)
                    else:
                        remotedirport_list = list()
                        for alw in alter_wwn:
                            remotedirport = wwns_dict.get(alw,[0])
                            remotedirport_list.append(remotedirport)
                        else:
                            rdirs = [x for i in remotedirport_list for x in i]
                        del remotedirport_list
                        s = set(rdirs)
                        uniq_dirs = [x for x in pg_list if x in s]
                        good_string = "{0},{1},{2},{3},{4},{5}".format(dirport, pwwn, ','.join(alter_wwn), ','.join(uniq_dirs), initiator_group_name, mask_view_name)
                        results.setdefault('goodout', []).append(good_string)

        return results


def main():
    x = VMAX()
    arraylist = x.list()
    print "arrays: {0}".format(arraylist)
    arr = raw_input("Choose array from the above List: ")
    c = raw_input("Choose FA port: ")
    data = x.devmask_login_record(arr,c)
    errors = data.get('error', "None")
    goodout = data.get('goodout', "None")

    if len(errors) >= 1 or not "None":
        print "#" * 20, "WWNs Without multipath", "#" * 20
        print "Dir,PWWN,Alternate_WWN,Remote_Dirs,IG,MV"
        print "\n".join([i for i in errors])
        print "#" * 68,"\n"
    else:
        print "#"*20, "All WWNs connected to the Dirport have alternative path", "#"*20

    if len(goodout) >= 1 or not "None":
        print "#" * 20, "WWNs With multipath info", "#" * 20
        print "Dir,PWWN,Alternate_WWN,Remote_Dirs,IG,MV"
        print "\n".join([i for i in goodout])
        print "#" * 68

if __name__ == '__main__':
    main()

