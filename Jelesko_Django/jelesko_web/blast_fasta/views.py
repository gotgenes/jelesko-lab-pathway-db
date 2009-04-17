#!/usr/bin/python
# -*- coding: utf-8 -*-

# fill this in with the appropriate path
SEQUENCE_DATA_DIR = ''

# fill this in with appropriate paths to BLASTDB formatted Databases
BLASTDB_DBS = [
        # Example:
        #('/Users/caiyizhi/Desktop/db.fasta', 'Complete DB'),
]
# This should be one of the above. e.g., 'Complete DB'
INITIAL_DB_CHOICE = ''

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django import forms
from models import Protein

from Bio.Blast import NCBIStandalone
from Bio.Blast import NCBIXML
import os
import parsing_fasta2
import time

class BlastForm(forms.Form):

    seq = forms.CharField(widget=forms.Textarea)
    evalue = forms.FloatField(initial=1)  # initial only for unbound form, not here because get data from GET
    wsoptions = [
        ('9', '9'),
        ('10', '10'),
        ('11', '11'),
        ('12', '12'),
        ('14', '14'),
        ('16', '16'),
        ]


class FastaForm(forms.Form):

    # the user-input FASTA formatted protein sequence
    seq = forms.CharField(widget=forms.Textarea)
    # -b "Number of sequence scores to be shown on output."
    number_sequence = forms.FloatField(initial=10)
    # -E "Limit the number of scores and alignments shown based on the
    # expected number of scores." Overrides the expectation value.
    number_alignment_highest = forms.FloatField(initial=10)
    # -F "Limit the number of scores and alignments shown based on the
    # expected number of scores." Sets the highest E-value shown.
    number_alignment_lowest = forms.FloatField(initial=0.1)
    mfoptions = [
            ('P250', 'pam250.mat'),
            ('P120', 'pam120.mat'),
            ('BL50', 'BLOSUM50'),
            ('BL62', 'BLOSUM62'),
            ('BL80', 'BLOSUM80')
    ]
    matrix_file = forms.ChoiceField(
            label='Matrix File',
            choices=mfoptions,
            initial='BLOSUM50'
    )
    dboptions = BLAST_DBS
    database_option = forms.ChoiceField(
            label='Database',
            choices=dboptions,
            initial=INITIAL_DB_CHOICE
    )


def fasta(request):

    # TODO: All of these files need to be made into temporary files of
    # temporary names so that they don't get fricking overwritten when
    # multiple users use the system!

    # TODO: Add parameter validation.

    my_fasta_file = SEQUENCE_DATA_DIR + '/fasta_seq.fasta'
    sqfile = open(my_fasta_file, 'w')
    # the form was submitted
    if request.method == 'POST':
        # this will allow the form to remain "filled out"
        f = FastaForm(request.POST)
        if not f.is_valid():
            return render_to_response('blast_fasta/fasta.html', {'form'
                    : f, 'res': ''})

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
        # TODO: This could be made nicer using string formatting.
        cmd = 'fasta35 -b ' + str(b) + ' -E ' + str(E) + ' -F '\
             + str(F) + ' -s ' + str(s) + ' ' + SEQUENCE_DATA_DIR\
             + 'fasta_seq.fasta ' + str(db) + ' > '\
             + SEQUENCE_DATA_DIR + 'fasta_output.txt'
        start = time.clock()
        os.system(cmd)
        end = time.clock()
        duration = end - start
        fasta_file = open(SEQUENCE_DATA_DIR + 'fasta_output.txt')
        res = parsing_fasta2.parsing_fasta(fasta_file)
        return render_to_response(
                'blast_fasta/fasta.html',
                {'form': f, 'res': res, 'duration': duration}
        )

    # user has not sent a POST request; present user with blank form
    else:
        form = FastaForm()
        return render_to_response(
                'blast_fasta/fasta.html',
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

