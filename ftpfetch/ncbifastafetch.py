#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
This module fetches prokaryotic genomes from NCBI's ftp database.

"""

__author__ = 'Chris Lasher'
__email__ = 'chris DOT lasher <AT> gmail DOT com'

import ftplib
from optparse import OptionParser
import os
import sys
import tarfile


# NCBI's FTP site
FTP_SITE = 'ftp.ncbi.nih.gov'
# The main Prokaryote parent directory and tarball of genomes
PROK_DIR = 'genomes/Bacteria'
PROK_TARBALL = 'all.gbk.tar.gz'


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


def connect_to_ncbi(site=FTP_SITE):
    """
    Establish an FTP connection to NCBI.

    :Parameters:
    - `site`: NCBI's site location

    """

    connection = ftplib.FTP(site)
    # Log in as 'Anonymous' with password 'anonymous'
    connection.login()
    return connection


def _parse_dir_line(line, subdirs):
    """
    Parses an NCBI FTP directory listing and returns a list of
    subdirectories.

    :Parameters:
    - `listing`: text output from an FTP dir listing
    - `subdirs`: a list of known existing subdirectories

    """

    # we're looking for lines like the following:
    # dr-xr-xr-x  52 ftp      anonymous     8192 Mar  6 20:26 genomes
    # and returning the 'genomes' part
    split_line = line.split()
    if split_line[0].startswith('d'):
        subdirs.append(split_line[-1])


def list_subdirs(connection, directory):
    """
    Returns a list of subdirectories of a given directory.

    :Parameters:
    - `connection`: an established FTP connection
    - `directory`: a directory to list

    """

    subdirs = []
    connection.retrlines('LIST %s' % directory, lambda x:
            _parse_dir_line(x, subdirs))
    return subdirs


def fetch_prok_genomes(connection, prok_genome_path, outfile):
    """
    Get a listing of all the directories in the Prokaryotic (Bacteria)
    directory.

    :Parameters:
    - `connection`: an established FTP connection
    - `prok_genome_path`: the path to the prokaryotic genomes GenBank
      file
    - `outfile`: a file handle to write data to (should be opened for
      binary data)

    """

    connection.retrbinary(
            'RETR %s' % prok_genome_path,
            outfile.write
    )


def extract_genomes(tarball_name):
    """
    Extracts the genomes from the tarball.

    :Parameters:
    - `tarball_name`: the filename of the tarball file

    """

    archive = tarfile.open(tarball_name)
    archive.extractall()
    archive.close()


def main(argv):
    # collect initial input from the user
    cli_parser = make_cli_parser()
    opts, args = cli_parser.parse_args(argv)
    if not len(args) == 1:
        cli_parser.error("Please provide one directory path.")
    dir_path = args[0]
    if not os.path.isdir(dir_path):
        cli_parser.error("%s is not a directory." % dir_path)
    os.chdir(dir_path)

    # fetch the file from NCBI
    print "Connecting to NCBI."
    ftp_connection = connect_to_ncbi(FTP_SITE)
    download_file = open(PROK_TARBALL, 'wb')
    prok_genome_path = '/'.join((PROK_DIR, PROK_TARBALL))
    print "Fetching genomes tarball. This will take a while..."
    fetch_prok_genomes(ftp_connection, prok_genome_path, download_file)
    download_file.close()
    print "Download finished."
    print "Unpacking tarball."
    extract_genomes(download_file.name)
    print "Finished unpacking."


if __name__ == '__main__':
    main(sys.argv[1:])
