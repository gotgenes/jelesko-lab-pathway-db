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
HEADER = "gi\taccession\tgenus_species\tannotation\tsequence\n"

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
    if genus_species_match:
        record_dict['genus_species'] = genus_species_match.group(1)
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


def fdict_to_str(fasta_dict):
    """
    Parses a FASTA dictionary to an output string.

    :Parameters:
    - `fasta_dict`: a dictionary from a parsed FASTA record

    """

    outstr = ("%(gi)s\t%(accession)s\t%(genus_species)s\t%(annotation)s"
            "\t%(sequence)s" % fasta_dict)
    return outstr


def fasta_to_flatfile(fasta_fileh, outfileh):
    """
    Parses a FASTA file and writes out a flat file suitable for database
    import.

    :Parameters:
    - `fasta_fileh`: a FASTA file handle
    - `outfileh`: file handle to write to

    """

    parsed_dicts = parse_fasta_to_dicts(fasta_fileh)
    out_strings = (fdict_to_str(parsed_dict) for parsed_dict in
            parsed_dicts)
    output = "\n".join(out_strings)
    outfileh.write(output)
    outfileh.write("\n")


def main(argv):
    cli_parser = make_cli_parser()
    opts, args = cli_parser.parse_args(argv)
    if not args:
        MSG = "Please provide the path to at least one FASTA file."
        cli_parser.error(MSG)
    outfileh = open('outfile.txt', 'w')
    outfileh.write(HEADER)
    for filename in args:
        print "Parsing %s" % filename
        fasta_fileh = open(filename)
        fasta_to_flatfile(fasta_fileh, outfileh)
        print "Output written to %s" % outfileh.name
        fasta_fileh.close()

    print "Finished processing files."


if __name__ == '__main__':
    main(sys.argv[1:])
