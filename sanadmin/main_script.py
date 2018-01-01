#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, argparse
VERSION = '1.0'
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
    parser.add_argument('-host',
                        type=str,
                        required=False,
                        help='Host Name')
    parser.add_argument('-Luns',
                        type=str,
                        required=False,
                        help="Number of Luns*lun size(GBs) Example: 5x512,2x256")

    # If there is no parameter, print help
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    sys.stdout.write(str(args))

    if not args.sid.strip().isdigit():
        parser.print_help()
        sys.exit(0)

def extract_luns(args=None):
    luns_dict = dict()
    luns_list = args.luns.split(',')
    for l in luns_list:
        lun_nos = l.split()




def main():
    parse_parameters()

if __name__ == '__main__':
    main()
