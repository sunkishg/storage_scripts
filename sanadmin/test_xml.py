#!/usr/bin/env python

# import python modules
import sys
import pprint
import logging
import collections
import subprocess
import xml.etree.ElementTree as ET

def nested_dict():
    return collections.defaultdict(nested_dict)


def get_xml_text(elem, tag):
    try:
        x = elem.find(tag).text
    except:
        x = 0

    return x


def sg_to_dict():
    sgs = nested_dict()
    xml_string = open(r'C:\Users\sunkishg\Desktop\0456_symsg_list.xml')
    sgtree = ET.fromstring(xml_string.read())

    for elem in sgtree.findall('SG'):

        sg_name  = get_xml_text(elem, 'SG_Info/name')

        sgs[sg_name]['symmid'] = get_xml_text(elem, 'SG_Info/symid')
        sgs[sg_name]['slo_name'] = get_xml_text(elem, 'SG_Info/SLO_name')
        sgs[sg_name]['workload'] = get_xml_text(elem, 'SG_Info/Workload')
        sgs[sg_name]['srp_name'] = get_xml_text(elem, 'SG_Info/SRP_name')
        sgs[sg_name]['hostlimit'] = get_xml_text(elem, 'SG_Info/HostIOLimit_status')
        sgs[sg_name]['dynamic'] = get_xml_text(elem, 'SG_Info/Dynamic_Distribution')
        sgs[sg_name]['iops'] = get_xml_text(elem, 'SG_Info/HostIOLimit_max_io_sec')
        sgs[sg_name]['mbs'] = get_xml_text(elem, 'SG_Info/HostIOLimit_max_mb_sec')
        sgs[sg_name]['mv'] = get_xml_text(elem, 'SG_Info/Masking_views')

        sgs[sg_name]['child'] = list()
        sgs[sg_name]['parent'] = list()


        for elem_sg_group in elem.findall('SG_Info/SG_group_info/SG'):
            relation     = get_xml_text(elem_sg_group, 'Cascade_Status')
            sg_group_name = get_xml_text(elem_sg_group, 'name')
            if relation == 'IsChild':
                sgs[sg_name]['child'].append(sg_group_name)
            elif relation == 'IsParent':
                sgs[sg_name]['parent'].append(sg_group_name)


        if  not sgs[sg_name]['parent'] and not sgs[sg_name]['child']:
            sgs[sg_name]['relation'] = 'S'
        elif sgs[sg_name]['parent']:
            sgs[sg_name]['relation'] = 'C'
        elif sgs[sg_name]['child']:
            sgs[sg_name]['relation'] = 'P'


        for lun in elem.findall('DEVS_List/Device'):
            lun_id = get_xml_text(lun, 'dev_name')
            lun_mb = get_xml_text(lun, 'megabytes')
            sgs[sg_name]['luns'][lun_id] = int(lun_mb) # store the size as int


        sgs[sg_name]['num_luns'] = len(sgs[sg_name]['luns'])
        sgs[sg_name]['total_size'] = sum(sgs[sg_name]['luns'].values()) // 1024
        sgs[sg_name]['total_luns'] = sgs[sg_name]['luns'].keys()

    # print(sgs)

    sg_relation = list()
    for sg in sgs:
        sg_name = sg

        if not sgs[sg]['parent'] and not sgs[sg]['child']:
            sg_relation.append([sg_name])
        elif not sgs[sg]['parent']:
            x = ",".join(sgs[sg]['child'])
            x = sg_name + ',' + x
            sg_relation.append(x.split(","))
        else:
            pass

    header = list()

    for i in sorted(sg_relation):
        for sg_name in i:
            row = list()
            row.append(sg_name)
            row.append(sgs[sg_name]['relation'])
            row.append(str(sgs[sg_name]['num_luns']))
            row.append(str(sgs[sg_name]['total_size']))
            row.append(sgs[sg_name]['slo_name'])
            row.append(sgs[sg_name]['workload'])
            row.append(sgs[sg_name]['mv'])
            header.append(",".join(row))

    hostname = 'cdlenthf9db01'

    for line in header:
        if hostname in line:
            data = line.split(',')
            if data[1] == 'S' or data[1] == 'P':
                host_name = data[0]
                print(host_name)
                print(','.join(sgs[host_name]['total_luns']))
            else:
                print(line)

sg_to_dict()