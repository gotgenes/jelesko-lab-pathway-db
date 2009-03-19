#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Converts an NCBI FASTA protein file to a flat file for database input.

"""

__author__ = 'Chris Lasher'
__email__ = 'chris DOT lasher <AT> gmail DOT com'

import Bio.SeqIO
from optparse import OptionParser
import re
import sys

GENUS_SPECIES_RE = re.compile(r'\[(.+)\]')

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
    assert split_header[2] in ('ref', 'REF')
    record_dict['accession'] = split_header[3]
    description = split_header[4].strip()
    record_dict['annotation'] = description
    genus_species_match = GENUS_SPECIES_RE.search(description)
    record_dict['genus_species'] = genus_species_match.group(1)
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


def fasta_to_flatfile(fasta_fileh, outfileh):
    """
    Parses a FASTA file and writes out a flat file suitable for database
    import.

    :Parameters:
    - `fasta_fileh`: a FASTA file handle
    - `outfileh`: file handle to write to

    """

    parsed_records = parse_fasta_to_dicts(fasta_fileh)
    #TODO: Do stuff here
    # ...
    outfileh.write("\n".join(output))
    outfileh.write("\n")


def main(argv):
    cli_parser = make_cli_parser()
    opts, args = cli_parser.parse_args(argv)
    if not args:
        MSG = "Please provide the path to at least one FASTA file."
        cli_parser.error(MSG)
    for filename in args:
        print "Parsing %s" % filename
    #TODO


if __name__ == '__main__':
    main(sys.argv[1:])
