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
import time


# NCBI's FTP site
FTP_SITE = 'ftp.ncbi.nih.gov'

# this is a blacklist of directories we do not wish to descend into.
# Ideally, we should move this into a configuration file, but for right
# now, it will do to keep it here.
BLACKLIST = frozenset((
        'BACENDS',
        'CLONEEND',
        'FOSMIDS',
        'MapView',
        'TARGET',
        'TOOLS',
        'WGS_BACTERIA_OLD',
        'genomeprj',
        'mapview',
        'CLUSTERS',
        ))

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
    print "Exploring %s/" % top

    dirs, files = ftpwalk._ftp_listdir(connection)

    # So one trick we've learned is that if there's a subdirectory
    # called 'protein' in the current directory, that one will have all
    # the protein files in a file called 'protein.fa.gz'. We skip
    # straight to that and then move on.

    discovered_fasta_files = ['/'.join((top, file)) for file in
            _identify_faa(files)]

    if discovered_fasta_files:
        print "Discovered FASTA files."
        yield discovered_fasta_files

    else:
        # We discovered that if there's a subdirectory called 'protein'
        # in the current directory, that will contain a file called
        # 'protein.fa.gz' that contains all the predicted proteins. This
        # seems to be present when the genome hasn't been completely
        # assembled.
        if 'protein' in dirs:
            path = '/'.join((top, 'protein'))
            for fasta_files in fastawalk(connection, path):
                yield fasta_files
        else:
            for dname in dirs:
                path = '/'.join((top, dname,))
                if dname in BLACKLIST:
                    print "Skipping %s" % path
                else:
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


def download_fasta_files(connection, ftp_paths, dest_dir, skip_list=[]):
    """
    Download specified FASTA files.

    NOTE: Files named protein.fa.gz will be renamed based off of their
    organism directories. For example
    `/genomes/Bos_taurus/protein/protein.fa.gz` will be downloaded as
    `Bos_taurus.faa.gz` and then uncompressed as `Bos_taurus.faa`.

    NOTE: The files retrieved will be the set of all those listed in
    `ftp_paths` minus the set of those in `skip_list`.

    NOTE: `skip_list` should only be the file names, not the complete
    file paths.

    :Parameters:
    - `connection`: an established FTP connection
    - `ftp_paths`: paths of files to retrieve from the NCBI FTP server
    - `dest_dir`: directory to store the files in
    - `skip_list`: a list of file names to avoid downloading

    """

    # Make skip_list a set for quicker lookups
    skip_list = frozenset(skip_list)

    for path in file_paths:
        split_path = path.split('/')
        filename = split_path[-1]
        # we need to rename the file if it's protein.fa.gz, otherwise
        # we'll just wind up overwriting files
        if filename == 'protein.fa.gz':
            # these files appear in
            # /../../organism_name/protein/protein.fa.gz
            # so just grab the organism name and rename it to that
            organism_name = split_path[-3]
            filename = '%s.faa.gz' % organism_name

        # skip this file if it's in the skip list
        if filename in skip_list:
            print "Skipping %s" % path
            continue

        dest_path = os.path.sep.join((dest_dir, filename))
        print "Retrieving %s" % path
        print "Downloading to %s" % dest_path
        download_fileh = open(dest_path, 'wb')
        connection.retrbinary('RETR %s' % path, download_fileh.write)
        download_fileh.close()

        # if this is a gzipped file, we need to uncompress it
        if filename.endswith('.gz'):
            print "Uncompressing %s" % dest_path
            zipfileh = gzip.open(dest_path)
            outfileh = open(dest_path[:-3], 'w')
            for line in zipfileh:
                outfileh.write(line)
            zipfileh.close()
            outfileh.close()


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
