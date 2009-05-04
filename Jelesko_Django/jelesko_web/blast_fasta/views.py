#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django import forms
import models
from django.forms.util import ErrorList

from Bio.Blast import NCBIStandalone
from Bio.Blast import NCBIXML

import datetime
import os
import subprocess
import textwrap

import parsing_fasta

# Output files will be stored under the MEDIA_ROOT found in settings.py.
OUTPUT_DIR = settings.MEDIA_ROOT.rstrip('/')

# Fill this in with appropriate options of BLASTDB formatted databases
# NOTE: keep the value (e.g., 'completedb') 25 characters or less
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

MAPPING_HEADER = "Jelesko ID\tGI\tGenus species\n"

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


class FastaForm(forms.ModelForm):

    class Meta:
        model = models.FastaRun

    def clean(self):
        cleaned_data = self.cleaned_data
        seq = cleaned_data.get("seq")
        number_sequence = cleaned_data.get("number_sequence")
        number_alignment_highest = cleaned_data.get("number_alignment_highest")
        number_alignment_lowest = cleaned_data.get("number_alignment_lowest")
        if not seq:
            msg=u"Please enter a sequence"
            self._errors["seq"] = ErrorList([msg])
        if number_sequence and number_sequence <= 0:
            msg=u"Please enter a value greater than 0"
            self._errors["number_sequence"] = ErrorList([msg])
        if number_alignment_lowest:
            if number_alignment_lowest > number_alignment_highest:
                msg=u"Please enter an E-value smaller than the highest E-Value"
                self._errors["number_alignment_lowest"] = ErrorList([msg])
            elif number_alignment_lowest < 0:
                msg=u"Please enter a non-negative value"
                self._errors["number_alignment_lowest"] = ErrorList([msg])
        return cleaned_data


def _timedelta_to_minutes(td):
    """
    Converts a timedelta to minutes as a floating point.

    :Parameters:
    - `td` a datetime.timedelta instance

    """

    minutes = 1440 * td.days + td.seconds / 60.0
    return minutes


def _run_fasta_program(request, cmd, template_path, use_ktup=True):
    """
    Runs a FASTA type program (e.g., fasta35, ssearch35)

    :Parameters:
    - `request`: a Django HTTPRequest type object
    - `cmd`: a list containing the initial command (e.g., ['fasta35', '-q'])
    - `template_path`: path to the template for the result

    """

    # the form was submitted
    if request.method == 'POST':
        timestamp = datetime.datetime.now()
        outfile_dir = timestamp.strftime(models.SEARCH_RESULTS_DIR)
        full_outfile_dir = os.sep.join(
            (OUTPUT_DIR, outfile_dir)
        )
        os.mkdir(full_outfile_dir)

        query_filename = os.sep.join((full_outfile_dir, 'query.faa'))
        query_file = open(query_filename, 'w')

        f = FastaForm(request.POST)
        if not f.is_valid():
            print "Not valid."
            return render_to_response(
                    template_path,
                    {'form': f, 'res': ''}
            )

        query_file.write(f.cleaned_data['seq'])
        query_file.close()

        # start setting up the command
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
        if use_ktup:
            kt = f.cleaned_data['ktup']
        db = f.cleaned_data['database_option']
        subject = BLAST_DB_PATHS[db]

        # TODO: change this to take user-defined name later
        outfile_name = '%s_results.txt' % cmd[0]
        outfile_path = os.sep.join((outfile_dir, outfile_name))
        full_outfile_path = os.sep.join(
            (full_outfile_dir, outfile_name)
        )

        cmd.extend(
            ('-s', s, '-O', full_outfile_path, query_filename, subject)
        )
        if use_ktup:
            cmd.append(kt)

        start = datetime.datetime.now()
        subprocess.check_call(cmd)
        end = datetime.datetime.now()
        duration = _timedelta_to_minutes(end - start)

        fasta_output = open(full_outfile_path)
        try:
            res = parsing_fasta.parsing_fasta(fasta_output)
        except TypeError:
            res = []

        fasta_output.close()
        os.remove(query_filename)

        search_result = models.Search(
            program=cmd[0],
            results_file=outfile_path,
            timestamp=timestamp
        )
        search_result.save()

        resdata = {
            'records': res,
            'search_id': search_result.id
        }

        return render_to_response(
                template_path,
                {
                    'form': f,
                    'resdata': resdata,
                    'duration': duration,
                }
        )

    # user has not sent a POST request; present user with blank form
    else:
        form = FastaForm()
        return render_to_response(
                template_path,
                {'form': form}
        )


def fasta(request):
    cmd = ['fasta35', '-q']
    template_path = 'blast_fasta/fasta.html'
    return _run_fasta_program(request, cmd, template_path)


def ssearch(request):
    cmd = ['ssearch35', '-q']
    template_path = 'blast_fasta/ssearch.html'
    return _run_fasta_program(request, cmd, template_path,
            use_ktup=False)


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
                        b = models.Protein.objects.get(gi=gi_number)
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


def _make_jelesko_id(protein, suffix_no=None):
    """
    Creates the Jelesko ID for a given protein.

    :Parameters:
    - `protein`: a Protein model instance
    - `suffix_no`: an integer for a suffix (optional; if None, no suffix
      is appended)

    """

    genus, species = protein.genus_species.split()[:2]
    genus = genus[:3]
    species = species[:3]
    if suffix_no is not None:
        jelesko_id = "%s %s.%d" % (genus, species, suffix_no)
    else:
        jelesko_id = "%s %s" % (genus, species)
    return jelesko_id


def _protein_to_fasta(header, protein):
    """
    Creates an output string in FASTA format for a given protein.

    """

    fastastr_list = ['>%s' % header]
    fastastr_list.extend(textwrap.wrap(protein.sequence, 60))
    fastastr_list.append('')
    fastastr = '\n'.join(fastastr_list)
    return fastastr


def _protein_to_mapping(id_str, protein):
    """
    Creates a mapping line for a protein.

    """

    mapping_line = '%s\t%s\t%s\n' % (
        id_str, protein.gi, protein.genus_species
    )
    return mapping_line


def _output_to_sel_files(jelesko_id, protein, fasta_fileh, map_fileh):

    fasta_str = _protein_to_fasta(jelesko_id, protein)
    fasta_fileh.write(fasta_str)
    map_str = _protein_to_mapping(jelesko_id, protein)
    map_fileh.write(map_str)


def seqrequest(request):
    """
    Handles requests for sequences in a given result.

    """

    gis = request.POST.getlist('gis')
    search_id = request.POST.get('search_id')
    comment = request.POST.get('comment', '')

    # TODO: This parameter checking is all bullshit. This needs to be
    # written into a real Form class with real parameter checking.
    if not search_id:
        return HttpResponse('Problem with the search_id.')

    try:
        search_id = int(search_id)
    except ValueError:
        return HttpResponse('search_id is not an int.')

    try:
        search = models.Search.objects.get(id=search_id)
    except models.Search.DoesNotExist:
        return HttpResponse('A search of id %d does not exist.' % (
                            search_id))

    if len(comment) > 140:
        return HttpResponse('comment was too long.')


    # It's important to note that this line below will not catch
    # requests for GI numbers that don't exist in the database; those
    # will silently be ignored.
    proteins = models.Protein.objects.filter(gi__in=gis)
    species_dict = {}

    timestamp = datetime.datetime.now()
    outfile_dir = timestamp.strftime(models.SELECTIONS_DIR)
    full_outfile_dir = os.sep.join(
        (OUTPUT_DIR, outfile_dir)
    )
    os.mkdir(full_outfile_dir)

    # TODO: change this to take input from user for names
    fasta_file_name = 'selections.faa'
    fasta_file_path = os.sep.join((outfile_dir, fasta_file_name))
    full_fasta_file_path = os.sep.join(
        (full_outfile_dir, fasta_file_name)
    )
    fasta_fileh = open(full_fasta_file_path, 'w')
    map_file_name = 'mapping.txt'
    map_file_path = os.sep.join((outfile_dir, map_file_name))
    full_map_file_path = os.sep.join((full_outfile_dir, map_file_name))
    map_fileh = open(full_map_file_path, 'w')

    try:
        for protein in proteins:
            if protein.genus_species in species_dict:
                species_dict[protein.genus_species].append(protein)
            else:
                species_dict[protein.genus_species] = [protein]

        map_fileh.write(MAPPING_HEADER)

        for species_str, proteins in species_dict.items():
            genus, species = species_str.split()[:2]
            if len(proteins) > 1:
                for i, protein in enumerate(proteins):
                    jelesko_id = _make_jelesko_id(protein, i + 1)
                    _output_to_sel_files(
                        jelesko_id, protein, fasta_fileh, map_fileh
                    )
            else:
                jelesko_id = _make_jelesko_id(protein)
                _output_to_sel_files(
                    jelesko_id, protein, fasta_fileh, map_fileh
                )

    finally:
        fasta_fileh.close()
        map_fileh.close()

    # create an entry in the Selections table
    selection = models.SequenceSelection(
        search=search,
        sequences_file=fasta_file_path,
        map_file=map_file_path,
        timestamp=timestamp,
        comment=comment
    )
    selection.save()

    # redirect user to page containing links to these files
    return HttpResponseRedirect(
        reverse(seqselection, args=[selection.id])
    )


def seqselection(request, selection_id):

    selection = get_object_or_404(
        models.SequenceSelection, id=selection_id
    )
    return render_to_response(
        'blast_fasta/selection.html',
        {
            'selection': selection
        }
    )
