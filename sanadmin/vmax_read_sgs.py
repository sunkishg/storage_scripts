#!/usr/bin/env python
#
# import python modules

import collections
import xml.etree.ElementTree as ET

# Create nested dic
def nested_dict():
    return collections.defaultdict(nested_dict)


# Return the text for a specific XML tag
def get_xml_text(elem, tag):
    
    try:
        x = elem.find(tag).text
    except:
        x = "None"

    return x

def sg_to_dict(symmid):
    sgs = nested_dict()
    xml_string = run_command("symsg -sid " + symmid + " list -v -output xml_e")
    sgtree = ET.fromstring(xml_string)
    #for each SG
    for elem in sgtree.findall('SG'):
        # get Storage Group Name
        sg_name  = get_xml_text(elem, 'SG_Info/name')
        # get some SG informations
        sgs[sg_name]['symmid'] = get_xml_text(elem, 'SG_Info/symid')
        sgs[sg_name]['slo_name'] = get_xml_text(elem, 'SG_Info/SLO_name')
        sgs[sg_name]['workload'] = get_xml_text(elem, 'SG_Info/Workload')
        sgs[sg_name]['srp_name'] = get_xml_text(elem, 'SG_Info/SRP_name')
        sgs[sg_name]['hostlimit'] = get_xml_text(elem, 'SG_Info/HostIOLimit_status')
        sgs[sg_name]['dynamic'] = get_xml_text(elem, 'SG_Info/Dynamic_Distribution')
        sgs[sg_name]['iops'] = get_xml_text(elem, 'SG_Info/HostIOLimit_max_io_sec')
        sgs[sg_name]['mbs'] = get_xml_text(elem, 'SG_Info/HostIOLimit_max_mb_sec')
        sgs[sg_name]['mv'] = get_xml_text(elem, 'SG_Info/Masking_views')
        # initialize list of sgs parent and childs
        sgs[sg_name]['child'] = list()
        sgs[sg_name]['parent'] = list()

        # populate lists of SGs parent and childs
        for elem_sg_group in elem.findall('SG_Info/SG_group_info/SG'):
            relation     = get_xml_text(elem_sg_group, 'Cascade_Status')
            sg_group_name = get_xml_text(elem_sg_group, 'name')
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
            lun_id = get_xml_text(lun, 'dev_name')
            lun_mb = get_xml_text(lun, 'megabytes')
            sgs[sg_name]['luns'][lun_id] = int(lun_mb) # store the size as int

        # Get the number of luns
        sgs[sg_name]['num_luns'] = len(sgs[sg_name]['luns'])
        
        # Sum all luns size and store value in GB
        sgs[sg_name]['total_size'] = sum(sgs[sg_name]['luns'].values()) // 1024

        #get the total Number of luns
        sgs[sg_name]['total_luns'] = sgs[sg_name]['luns'].keys()
        

    if not log.disabled:
        log.debug("sg dict:")
        pprint.pprint(sgs)
    return sgs


##############################################################################
# Function to read the Storage Group dictionary and return a list
# with storage groups relationship.
# List format:
# [ ['sgpai','sgchild','sgchild'],['sgstandalone'],['sgpai','sgchild'],...]
##############################################################################
def get_sgs_relationship(sgs):
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

    if not log.disabled:
        log.debug("sg_relation list:")
        pprint.pprint(sg_relation)
    return sg_relation


##############################################################################
# Print the SG dictionary using PrettyTable library
##############################################################################
def print_sg_info(sgs_relationship, sgs, symmid, hostname):
    # Special color for Parent and Standalone SGs
    p_color = '\033[01;37;44m'
    nocolor = '\033[0m'

    header = list()
    # header.append("SG_Name")
    # header.append("Relation")
    # header.append("SymmID")
    # header.append("# LUNs")
    # header.append("Total_Size (GB)")
    # #header.append("SRP")
    # header.append("SLO")
    # header.append("Workload")
    # header.append("Host_Limit")
    # header.append("Host_Limit_IOPS")
    # header.append("Host_Limit_MBs")
    # header.append("Dynamic_Distr")
    # header.append("Masking")

    # output = prettytable.PrettyTable(header)
    # output.format = True

    # each SG parent has a sub list with its children
    for i in sorted(sgs_relationship):
        # for each sg
        for sg_name in i:
            row = list()
            if sgs[sg_name]['relation'] == 'P' and COLORS:
                row.append(p_color + sg_name)
            elif sgs[sg_name]['relation'] == 'S' and COLORS:
                row.append(p_color + sg_name)
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
            if sgs[sg_name]['relation'] == 'P' and COLORS:
                row.append(sgs[sg_name]['mv'] + nocolor)
            elif sgs[sg_name]['relation'] == 'S' and COLORS:
                row.append(sgs[sg_name]['mv'] + nocolor)
            else:
                row.append(sgs[sg_name]['mv'])
            header.append(",".join(row))

    for line in header:
        if hostname in line:
            data = line.split(',')
            if data[1] == 'S' or data[1] == 'P':
                host_name = data[0]
                total_lun_nos = ','.join(sgs[host_name]['total_luns'])
                print total_lun_nos
                if len(total_lun_nos) > 0:
                    total_luns_output = run_command("symcfg -sid {0} list -tdev -detail -gb -dev {1} -output xml_e".format(symmid, total_lun_nos))
                    sgtree = ET.fromstring(total_luns_output)
                    recods = sgtree.findall('Symmetrix/ThinDevs/Totals')
                    for item in recods:
                        total_tracks_gb = item.find('total_tracks_gb').text
                        total_alloc_tracks_gb = item.find('total_alloc_tracks_gb').text
                        total_alloc_percent = item.find('total_alloc_percent').text
                        print(line, total_tracks_gb, total_alloc_tracks_gb, total_alloc_percent)
            else:
                lun_size_list = sgs[host_name]['luns'].values()
                lun_size_dict = dict()
                for l in lun_size_list:
                    l = l // 1024
                    if l in lun_size_dict:
                        lun_size_dict[l] += 1
                    else:
                        lun_size_dict[l] = 1

                print(line,lun_size_dict)


    # output.align["SG_Name"] = "l"
    # print(output)


##############################################################################
# Parses the command line arguments
##############################################################################
def parse_parameters():
    # epilog message: Custom text after the help
    epilog = '''
    Example of use:
        %s -sid 001
        %s -v -sid 002
    ''' % (sys.argv[0],sys.argv[0])
    # Create the argparse object and define global options
    parser = argparse.ArgumentParser(description='Script to show Storage Group details',
                                    formatter_class=argparse.RawDescriptionHelpFormatter,
                                    epilog=epilog)
    parser.add_argument('--version',
                        action='version',
                        version=VERSION)
    parser.add_argument('--verbose', '-v',
                        action='store_true',
                        help='verbose flag',
                        dest='verbose')
    parser.add_argument('-sid',
                        type=str,
                        required=True,
                        help='Symmetrix ID')
    parser.add_argument('SG_NAME', help='Storage Group Name to show LUNs space utilization')
    # If there is no parameter, print help
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)

    return parser.parse_args()


##############################################################################
# Main function
##############################################################################
def main():
    global log

    # Create the log structure
    log = setup_logging()

    # Parser the command line
    args = parse_parameters()

    # check if we need verbose output
    if not args.verbose:
        log.disabled = True
    log.debug('CMD line args: %s', vars(args))

    if not args.sid.isdigit():
        message("red", "Error: SymmID must be a number", 1)
    if not args.SG_NAME:
        message("red", "Error: please provide a hostname", 1)

    sgs = sg_to_dict(args.sid)
    sgs_relationship = get_sgs_relationship(sgs)
    print_sg_info(sgs_relationship, sgs, args.sid, args.SG_NAME)


##############################################################################
# Run from command line
##############################################################################
if __name__ == '__main__':
    main()


# vim: ts=4
