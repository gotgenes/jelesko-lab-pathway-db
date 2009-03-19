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


def parse_fasta_records(fasta_fileh):
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
        record_dict = {}
        split_header = record.description.split('|')
        assert len(split_header) == 5
        assert split_header[0] in ('gi', 'GI')
        record_dict['gi'] = split_header[1]
        assert split_header[2] in ('ref', 'REF')
        record_dict['accession'] = split_header[3]
        description = split_header[4].strip()
        record_dict['annotation'] = description
        genus_species_match = GENUS_SPECIES_RE.search(description)
        record_dict['genus_species'] = genus_species_match.group(1)
        record_dict['sequence'] = record.seq.tostring()
        yield record_dict


def main(argv):
    cli_parser = make_cli_parser()
    opts, args = cli_parser.parse_args(argv)
    if not args:
        MSG = "Please provide the path to at least one FASTA file."
        cli_parser.error(MSG)
    #TODO


if __name__ == '__main__':
    main(sys.argv[1:])
