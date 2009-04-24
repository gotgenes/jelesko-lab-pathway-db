#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django import forms
from models import Protein

from Bio.Blast import NCBIStandalone
from Bio.Blast import NCBIXML

import datetime
import os
import subprocess
import tempfile
import time

import parsing_fasta

# Fill this in with the appropriate path; this is the location where
# output files from runs will be stored. It should be writeable by the
# user Django runs under (e.g., www-data for most Linux/Unix systems)
OUTPUT_DIR = ''
OUTPUT_DIR = OUTPUT_DIR.rstrip(os.sep)

# Fill this in with appropriate options of BLASTDB formatted databases
BLAST_DBS = [
        # Example:
        #('completedb', 'Complete DB'),
]

# Specify paths to the actual databases
BLAST_DB_PATHS = {
        # Example:
        #'completedb': '/var/local/blastdbs/complete.db',
}

# This should be one of the above. e.g., 'Complete DB'
INITIAL_DB_CHOICE = ''

class BlastForm(forms.Form):

    seq = forms.CharField(widget=forms.Textarea)
    evalue = forms.FloatField(initial=1)
    wordsize = forms.IntegerField(
            label='Word Size',
            initial=3
    )
    database_option = forms.ChoiceField(
            label='Database',
            choices=BLAST_DBS,
            initial=INITIAL_DB_CHOICE
    )


class FastaForm(forms.Form):

    # TODO: Add parameter validation.

    # the user-input FASTA formatted protein sequence
    seq = forms.CharField(widget=forms.Textarea)
    # -b "Number of sequence scores to be shown on output."
    number_sequence = forms.FloatField(required=False)
    # -E "Limit the number of scores and alignments shown based on the
    # expected number of scores." Overrides the expectation value.
    number_alignment_highest = forms.FloatField(initial=10.0,
            required=False)
    # -F "Limit the number of scores and alignments shown based on the
    # expected number of scores." Sets the highest E-value shown.
    number_alignment_lowest = forms.FloatField(required=False)
    mfoptions = [
            ('P250', 'PAM250'),
            ('P120', 'PAM120'),
            ('BL50', 'BLOSUM50'),
            ('BL62', 'BLOSUM62'),
            ('BL80', 'BLOSUM80')
    ]
    matrix_file = forms.ChoiceField(
            label='Matrix File',
            choices=mfoptions,
            initial='BL50'
    )
    database_option = forms.ChoiceField(
            label='Database',
            choices=BLAST_DBS,
            initial=INITIAL_DB_CHOICE
    )
    ktupoptions = [('1', '1'), ('2', '2')]
    ktup = forms.ChoiceField(
            label='Ktup',
            choices=ktupoptions,
            initial = '2'
    )


class displayform(forms.Form):
	"""docstring for displayform"""
	check_box = forms.BooleanField(required = False)
	gi_number = forms.CharField()
	bit_score = forms.CharField()
	e_value = forms.CharField()
	accession = forms.CharField()
	genus_species = forms.CharField()
	annotation = forms.CharField()
	download_date = forms.CharField()


def _timedelta_to_minutes(td):
    """
    Converts a timedelta to minutes as a floating point.

    :Parameters:
    - `td` a datetime.timedelta instance

    """

    minutes = 1440 * td.days + td.seconds / 60.0
    return minutes


def fasta(request):

    # TODO: Add parameter validation.

    # the form was submitted
    if request.method == 'POST':
        timestr = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
        query_filename = os.sep.join(
                (
                    OUTPUT_DIR,
                    'query-%s.faa' % (timestr)
                )
        )
        query_file = open(query_filename, 'w')

        f = FastaForm(request.POST)
        if not f.is_valid():
            print "Not valid."
            return render_to_response('blast_fasta/fasta2.html', {'form'
                    : f, 'res': ''})

        query_file.write(f.cleaned_data['seq'])
        query_file.close()

        # start setting up the command
        cmd = ['fasta35 -q']
        if f.cleaned_data['number_sequence']:
            b = f.cleaned_data['number_sequence']
            cmd.extend(('-b', str(b)))
        if f.cleaned_data['number_alignment_highest']:
            E = f.cleaned_data['number_alignment_highest']
            cmd.extend(('-E', str(E)))
        if f.cleaned_data['number_alignment_lowest']:
            F = f.cleaned_data['number_alignment_lowest']
            cmd.extend(('-F', str(F)))
        s = f.cleaned_data['matrix_file']
        kt = f.cleaned_data['ktup']
        db = f.cleaned_data['database_option']
        subject = BLAST_DB_PATHS[db]
        outfile_name = os.sep.join((
                OUTPUT_DIR,
                '%s_fasta_results.txt' % timestr
        ))
        cmd.extend(
            ('-s', s, '-O', outfile_name, query_filename, subject, kt)
        )

        start = datetime.datetime.now()
        subprocess.check_call(cmd)
        end = datetime.datetime.now()
        duration = _timedelta_to_minutes(end - start)

        fasta_output = open(outfile_name)
        try:
            res = parsing_fasta2.parsing_fasta(fasta_output)
        except TypeError:
            res = []

        fasta_output.close()
        # later, these should be stored in the database
        os.remove(query_filename)
        os.remove(outfile_name)
        return render_to_response(
                'blast_fasta/fasta2.html',
                {
                    'form': f,
                    'res': res,
                    'duration': duration,
                    'form2': displayform()
                }
        )

    # user has not sent a POST request; present user with blank form
    else:
        form = FastaForm()
        return render_to_response(
                'blast_fasta/fasta2.html',
                {'form': form}
        )

def ssearch(request):

    my_fasta_file = SEQUENCE_DATA_DIR + 'ssearch_seq.fasta'
    sqfile = open(my_fasta_file, 'w')
    if request.method == 'GET':
        f = FastaForm(request.GET)
        if not f.is_valid():
            return render_to_response('blast_fasta/ssearch.html',
                    {'form': f, 'res': ''})
        else:
            sqfile.write(f.cleaned_data['seq'])
            sqfile.close()
            if not f.cleaned_data['number_sequence']:
                b = 10
            else:
                b = f.cleaned_data['number_sequence']
            if not f.cleaned_data['number_alignment_highest']:
                E = 10
            else:
                E = f.cleaned_data['number_alignment_highest']
            if not f.cleaned_data['number_alignment_lowest']:
                F = 0
            else:
                F = f.cleaned_data['number_alignment_lowest']
            s = f.cleaned_data['matrix_file']
            db = f.cleaned_data['database_option']
            cmd = 'ssearch35 -b ' + str(b) + ' -E ' + str(E) + ' -F '\
                 + str(F) + ' -s ' + str(s) + ' ' + SEQUENCE_DATA_DIR\
                 + 'ssearch_seq.fasta ' + str(db) + ' > '\
                 + SEQUENCE_DATA_DIR + 'ssearch_output.txt'
            os.system(cmd)
            fasta_file = open(SEQUENCE_DATA_DIR + '/ssearch_output.txt')
        res = parsing_fasta2.parsing_fasta(fasta_file)
    return render_to_response('blast_fasta/ssearch.html', {'form': f,
                              'res': res})


def blast(request):
    """docstring for blast"""

    my_blast_dir = SEQUENCE_DATA_DIR
    my_blast_file = SEQUENCE_DATA_DIR + '/seq.fasta'
    sqfile = open(my_blast_file, 'w')
    my_blast_db = SEQUENCE_DATA_DIR + '/db.fasta'
    if request.method == 'GET':
        f = BlastForm(request.GET)
        if not f.is_valid():
            return render_to_response('blast_fasta/blast.html', {'form'
                    : f, 'res': ''})  # do sth else
        else:
            sqfile.write(f.cleaned_data['seq'])
            sqfile.close()
            if not f.cleaned_data['evalue']:  # does not work
                e = 1
            else:
                e = f.cleaned_data['evalue']

            my_blast_exe = '/usr/bin/blastall'

            (result_handle, error_handle) = \
                NCBIStandalone.blastall(blastcmd=my_blast_exe,
                    program='blastp', database=my_blast_db,
                    infile=my_blast_file, expectation=e)
            blast_records = NCBIXML.parse(result_handle)
            res = []
            for br in blast_records:
                for a in br.alignments:
                    for hsp in a.hsps:
                        title_desc = a.title.split('|')
                        gi_number = title_desc[-1]
                        b = Protein.objects.get(gi=gi_number)
                        accession = b.accession.strip()
                        genus_species = b.genus_species.strip()
                        annotation = b.annotation.strip()
                        download_date = b.download_date
                        res.append((
                            gi_number,
                            hsp.expect,
                            accession,
                            genus_species,
                            annotation,
                            download_date,
                            ))
    return render_to_response('blast_fasta/blast2.html', {'form': f,
                              'res': res})

