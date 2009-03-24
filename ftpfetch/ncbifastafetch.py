#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
This module fetches prokaryotic genomes from NCBI's ftp database.

"""

__author__ = 'Chris Lasher'
__email__ = 'chris DOT lasher <AT> gmail DOT com'

import ftplib
import ftpwalk
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


def fastawalk(connection, top):
    """
    Walks down the NCBI FTP directories and yields paths to found
    protein FASTA file.

    NOTE: This returns an iterator.

    :Parameters:
    - `connection`: an established FTP connection
    - `top`: the directory from which to start crawling down

    """

    # This is a recursive, depth-first-search type algorithm for
    # "walking" down the FTP directory structure at NCBI. There are a
    # couple of tricks here, but the important thing to note is that
    # this algorithm stops recursing to lower levels any time it can
    # find protein FASTA files in the "current" depth.

    # Make the FTP object's current directory to the top dir.
    connection.cwd(top)
    top = connection.pwd()
    print "Exploring %s" % top

    dirs, files = ftpwalk._ftp_listdir(connection)

    discovered_fasta_files = ['/'.join((top, file)) for file in
            _identify_faa(files)]

    if discovered_fasta_files:
        print "Discovered FASTA files."
        yield discovered_fasta_files

    else:
        for dname in dirs:
            path = '/'.join((top, dname))
            for fasta_files in fastawalk(connection, path):
                yield fasta_files


def _identify_faa(file_list):
    """
    Identify amino-acid FASTA formatted files in

    :Parameters:
    - `file_list`: a list of filenames

    """

    fasta_files = []
    for filename in file_list:
        if filename.endswith('.faa') or filename == 'protein.fa.gz':
            fasta_files.append(filename)
    return fasta_files


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


def dbg_main():
    connection = connect_to_ncbi()
    fasta_files = []
    for found_files in fastawalk(connection, '/genomes'):
        fasta_files.extend(found_files)
    for path in fasta_files:
        print path


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
    #main(sys.argv[1:])
    dbg_main()
