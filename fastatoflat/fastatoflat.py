#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Converts an NCBI FASTA protein file to a flat file for database input.

"""

__author__ = 'Chris Lasher'
__email__ = 'chris DOT lasher <AT> gmail DOT com'

import Bio.SeqIO
import copy
from optparse import OptionParser
import os
import re
import sys
import time

OUTFILE_NAME = 'outfile.txt'

GENUS_SPECIES_RE = re.compile(r'\[(.+?)\]')
HEADER = "gi\taccession\tgenus_species\tannotation\tdownload_date\tsequence\n"

def make_cli_parser():
    """
    Creates the command line interface parser.

    """

    usage = "\n".join([
        """\
python %prog [OPTIONS] FASTAFILE1 FASTAFILE2 ...

ARGUMENTS:
  FASTAFILE1, FASTAFILE2, ...: paths to one or more FASTA formatted files
""",
        __doc__
    ])
    cli_parser = OptionParser(usage)
    cli_parser.add_option(
            '-o', '--outfile', default=OUTFILE_NAME,
            help="path to output file [Default: %default]"
    )
    return cli_parser


def record_to_dict(fasta_record):
    """
    Parses a FASTA record to a dictionary with the following keys:

    - `gi`: the GI number of the record
    - `accession`: the GenBank accession for the record
    - `genus_species`: the genus and species name for the record's
        organism
    - `annotation`: the full annotation string
    - `sequence`: the sequence of the record

    :Parameters:
    - `fasta_record`: a SeqRecord object returned by Bio.SeqIO.parse()

    """

    record_dict = {}
    split_header = fasta_record.description.split('|')
    assert len(split_header) == 5
    assert split_header[0] in ('gi', 'GI')
    record_dict['gi'] = split_header[1]
    description = split_header[4].strip()
    if split_header[2] in ('ref', 'REF'):
        record_dict['accession'] = split_header[3]
    # this is hear in case it's a mitochondrial sequence
    # We're looking to pull information from a line like below.
    #>gi|5819099|gnl|NCBI_MITO|ND1_10014 NADH dehydrogenase subunit 1 [Balaenoptera physalus]
    elif split_header[3] == 'NCBI_MITO':
        accession, junk = split_header[4].split(None, 1)
        record_dict['accession'] = accession
    else:
        raise ValueError("Unrecognized FASTA header\n%s" %
                fasta_record.description)
    record_dict['annotation'] = description
    # We have to find all matches; sometimes there will be [blah blah]
    # in the description. The very last one should be [Genus species].
    genus_species_matches = GENUS_SPECIES_RE.findall(description)
    if genus_species_matches:
        record_dict['genus_species'] = genus_species_matches[-1]
    else:
        record_dict['genus_species'] = ''
    record_dict['sequence'] = fasta_record.seq.tostring()
    return record_dict


def parse_fasta_to_dicts(fasta_fileh):
    """
    Parses FASTA records, yielding a dictionary for each containing the
    following keys:

    - `gi`: the GI number of the record
    - `accession`: the GenBank accession for the record
    - `genus_species`: the genus and species name for the record's
        organism
    - `annotation`: the full annotation string
    - `sequence`: the sequence of the record

    :Parameters:
    - `fasta_fileh`: a FASTA file handle

    """

    for record in Bio.SeqIO.parse(fasta_fileh, 'fasta'):
        yield record_to_dict(record)


def fdict_to_str(fasta_dict, date):
    """
    Parses a FASTA dictionary to an output string.

    :Parameters:
    - `fasta_dict`: a dictionary from a parsed FASTA record
    - `date`: the date the file was downloaded

    """

    out_dict = copy.copy(fasta_dict)
    out_dict['date'] = date
    outstr = ("%(gi)s\t%(accession)s\t%(genus_species)s\t%(annotation)s"
            "\t%(date)s\t%(sequence)s" % out_dict)
    return outstr


def fasta_to_flatfile(fasta_fileh, file_date, outfileh):
    """
    Parses a FASTA file and writes out a flat file suitable for database
    import.

    :Parameters:
    - `fasta_fileh`: a FASTA file handle
    - `file_date`: the date the file was downloaded
    - `outfileh`: file handle to write to

    """

    parsed_dicts = parse_fasta_to_dicts(fasta_fileh)

    # we need a hack in case the genus and species name is provided;
    # we'll use the last used value
    last_genus_species = ''
    for parsed_dict in parsed_dicts:
        if not parsed_dict['genus_species']:
            parsed_dict['genus_species'] = last_genus_species
        out_string = fdict_to_str(parsed_dict, file_date)
        outfileh.write(out_string)
        outfileh.write("\n")
        last_genus_species = parsed_dict['genus_species']


def _get_file_ctime(filename):
    """
    Returns the file creation time of a given file in the following
    format: YYYY-MM-DD HH:MM (ISO-8601 format)

    :Parameters:
    - `filename`: the file's name (path)

    """

    unix_time = os.path.getctime(filename)
    file_ctime = time.strftime('%Y-%m-%d %H:%M',
            time.localtime(unix_time))
    return file_ctime


def main(argv):
    cli_parser = make_cli_parser()
    opts, args = cli_parser.parse_args(argv)
    if not args:
        MSG = "Please provide the path to at least one FASTA file."
        cli_parser.error(MSG)
    outfileh = open(opts.outfile, 'w')
    outfileh.write(HEADER)
    for filename in args:
        print "Parsing %s" % filename
        fasta_fileh = open(filename)
        download_time = _get_file_ctime(filename)
        fasta_to_flatfile(fasta_fileh, download_time, outfileh)
        print "Output written to %s" % opts.outfile
        fasta_fileh.close()

    outfileh.close()
    print "Finished processing files."


if __name__ == '__main__':
    main(sys.argv[1:])
