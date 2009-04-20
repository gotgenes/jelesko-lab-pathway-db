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
            seq_rec = SeqRecord(
                    Seq(record.sequence, IUPAC.protein),
                    record.gi
            )
            yield seq_rec


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

