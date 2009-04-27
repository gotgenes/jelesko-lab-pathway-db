#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Dumps the proteins in the database to a FASTA formatted file.

"""

__author__ = 'Chris Lasher'
__email__ = 'chris DOT lasher <AT> gmail DOT com'

from django.core.management.base import NoArgsCommand, CommandError
from optparse import make_option

from jelesko_web.blast_fasta.models import Protein

from Bio.Seq import Seq
from Bio.SeqIO.FastaIO import FastaWriter
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import IUPAC

class Command(NoArgsCommand):

    help="""\
Dumps the proteins in the proteins table out to a FASTA formatted file.

NOTE: This will only write the GIs (or equivalent) for the header line.\
"""
    option_list = NoArgsCommand.option_list + (
            make_option(
                '-o', '--outfile', default='jeleskodb.faa',
                help="path to outfile [DEFAULT: %default]"
            ),
    )


    def _records_to_seqs(self, records):
        for record in records:
            # check if this is a GI number from NCBI; this SHOULD be
            # indicated by the fact that the identifier is entirely
            # numbers; all others should be prefixed by a code, e.g.,
            # JGI
            if record.gi.isdigit():
                identifier = 'gi|%s' % record.gi
            else:
                identifier = 'lcl|%s' % record.gi
            seq_rec = SeqRecord(
                    Seq(record.sequence.strip(), IUPAC.protein),
                    identifier
            )
            # skip records which, for whatever reason, have no sequence
            if len(seq_rec):
                yield seq_rec
            else:
                continue


    def handle_noargs(self, **options):
        outfilename = options['outfile']
        outfileh = open(outfilename, 'w')
        print "Fetching records."
        records = Protein.objects.all()
        seqs = self._records_to_seqs(records)
        print "Writing records to %s" % outfilename
        writer = FastaWriter(outfileh, record2title=lambda x: x.id)
        writer.write_file(seqs)
        outfileh.close()
        print "Done."

