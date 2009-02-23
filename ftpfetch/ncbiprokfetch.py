#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
This module fetches prokaryotic genomes from NCBI's ftp database.

"""

__author__ = 'Chris Lasher'
__email__ = 'chris DOT lasher <AT> gmail DOT com'

import ftplib
from optparse import OptionParser
import sys

# NCBI's FTP site
FTP_SITE = 'ftp.ncbi.nih.gov'


def make_cli_parser():
    """
    Creates the parser for the command line interface.

    """

    usage = "\n\n".join([
        """\
python %prog [OPTIONS] DIRECTORY

ARGUMENTS:
  DIRECTORY: the directory into which files will be deposited\
""",
        __doc__,
    ])
    cli_parser = OptionParser(usage)
    return cli_parser


def connect_to_ncbi(site):
    """
    Establish an FTP connection to NCBI.

    :Parameters:
    - `site`: NCBI's site location

    """

    connection = ftplib.FTP(FTP_SITE)
    # Log in as 'Anonymous' with password 'anonymous'
    connection.login()
    return connection


def fetch_prok_dirs(connection):
    """
    Get a listing of all the directories in the Prokaryotic directory.

    :Parameters:
    - `connection`: an established FTP connection

    """

    #TODO
    pass


def main(argv):
    cli_parser = make_cli_parser()
    opts, args = cli_parser.parse_args(argv)
    if not len(args) == 1:
        cli_parser.error("Please provide one directory path.")
    dir_path = args[0]
    if not os.path.isdir(dir_path):
        cli_parser.error("%s is not a directory." % dir_path)
    ftp_connection = connect_to_ncbi(FTP_SITE)
    ftp_prok_dirs = fetch_prok_dirs(ftp_connection)
    #TODO


if __name__ == '__main__':
    main(sys.argv[1:])
