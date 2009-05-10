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
BLAST_DBS = [
        # Example:
        #('completedb', 'Complete DB'),
        ('completedb', 'Complete DB'),
        ('toydb', 'Toy DB')
]

# Specify paths to the actual databases
BLAST_DB_PATHS = {
        # Example:
        #'completedb': '/var/local/blastdbs/complete.db',
        'completedb':
        '/home/chris/files/downloads/sequences/dbs/jeleskodb.faa',
        'toydb': '/home/chris/files/downloads/sequences/dbs/test.faa',
}

# This should be one of the above. e.g., 'Complete DB'
INITIAL_DB_CHOICE = 'toydb'

MAPPING_HEADER = "Jelesko ID\tGI\tGenus species\n"

FASTA_PROG = 'fasta35'
SSEARCH_PROG = 'ssearch35'
BLAST_PROG = 'blastall'

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
            initial='2',
            required=False
    )
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


def _run_fasta_program(
        request,
        cmd,
        template_path,
        view_name,
        use_ktup=True
    ):
    """
    Runs a FASTA type program (e.g., fasta35, ssearch35)

    :Parameters:
    - `request`: a Django HTTPRequest type object
    - `cmd`: a list containing the initial command (e.g., ['fasta35', '-q'])
    - `template_path`: path to the template for the result
    - `view_name`: the name of the view to send a search request to
      (this should usually come from a url name in urls.py)
    - `use_ktup`: if `True`, uses the ktup paramater

    """

    # Get the URL to submit to
    submit_to = reverse(view_name)

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
                    {'form': f, 'res': '', 'submit_to': submit_to}
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
                    'submit_to': submit_to,
                    'resdata': resdata,
                    'duration': duration,
                }
        )

    # user has not sent a POST request; present user with blank form
    else:
        form = FastaForm()
        return render_to_response(
                template_path,
                {'form': form, 'submit_to': submit_to}
        )

def _run_blast_program(
        request,
        cmd,
        template_path,
        view_name
    ):
    """
    Runs a BLAST type program (e.g., blastall)

    :Parameters:
    - `request`: a Django HTTPRequest type object
    - `cmd`: a list containing the initial command (e.g., ['fasta35', '-q'])
    - `template_path`: path to the template for the result
    """

    # Get the URL to submit to
    submit_to = reverse(view_name)

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

        f = BlastForm(request.POST)
        if not f.is_valid():
            print "Not valid."
            return render_to_response(
                    template_path,
                    {'form': f, 'res': '', 'submit_to': submit_to}
            )

        query_file.write(f.cleaned_data['seq'])
        query_file.close()

        # start setting up the command
        if f.cleaned_data['evalue']:
            E = f.cleaned_data['evalue']
            cmd.extend(('-e', str(E)))
        db = f.cleaned_data['database_option']
        subject = BLAST_DB_PATHS[db]

        # TODO: change this to take user-defined name later
        outfile_name = '%s_results.txt' % cmd[0]
        outfile_path = os.sep.join((outfile_dir, outfile_name))
        full_outfile_path = os.sep.join(
            (full_outfile_dir, outfile_name)
        )

        cmd.extend(
        ('-i', query_filename, '-d', subject, '-o', full_outfile_path)
        )

        start = datetime.datetime.now()
        subprocess.check_call(cmd)
        end = datetime.datetime.now()
        duration = _timedelta_to_minutes(end - start)

        fasta_output = open(full_outfile_path)
        try:
            res = parsing_fasta.parsing_blast(fasta_output)
            print res
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
                    'submit_to': submit_to,
                    'resdata': resdata,
                    'duration': duration,
                }
        )

    # user has not sent a POST request; present user with blank form
    else:
        form = FastaForm()
        return render_to_response(
                template_path,
                {'form': form, 'submit_to': submit_to}
        )
                                     


def fasta(request):
    cmd = [FASTA_PROG, '-q']
    template_path = 'blast_fasta/fasta.html'
    return _run_fasta_program(request, cmd, template_path, 'fasta')


def ssearch(request):
    cmd = [SSEARCH_PROG, '-q']
    template_path = 'blast_fasta/ssearch.html'
    return _run_fasta_program(request, cmd, template_path, 'ssearch',
            use_ktup=False)

def blast(request):
	"""docstring for blast2"""
	cmd = [BLAST_PROG]
	program = 'blastp'
	cmd.extend(
	('-p', program)
	)
	template_path = 'blast_fasta/blast.html'
	return _run_blast_program(request, cmd, template_path, 'blast') 


def _make_jelesko_id(protein, suffix_no=None):
    """
    Creates the Jelesko ID for a given protein.

    :Parameters:
    - `protein`: a Protein model instance
    - `suffix_no`: an integer for a suffix (optional; if None, no suffix
      is appended)

    """

    split_gs = protein.genus_species.split()
    genus_species_code = [item[:3] for item in split_gs[:2]]
    try:
        if genus_species_code[1] == 'sp.':
            genus_species_code.extend(split_gs[2:])
    except IndexError:
        pass
    if suffix_no is not None:
        genus_species_code.append(str(suffix_no))
    jelesko_id = '_'.join(genus_species_code)
    return jelesko_id


def guess_defline_prefix(identifier):
    """
    Attempts to guess the Defline prefix (e.g., 'gi|' or 'lcl|') for a
    given identifier.

    :Parameters:
    - `identifier`: a sequence identifier (e.g., a GI number)

    """

    if identifier.isdigit():
        return 'gi|'
    else:
        return 'lcl|'


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


def _output_to_sel_files(
        jelesko_id, protein,
        fasta_fileh,
        gi_fasta_fileh,
        map_fileh
        ):

    fasta_str = _protein_to_fasta(jelesko_id, protein)
    fasta_fileh.write(fasta_str)
    gi_header = guess_defline_prefix(protein.gi) + protein.gi
    gi_fasta_str = _protein_to_fasta(gi_header, protein)
    gi_fasta_fileh.write(gi_fasta_str)
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
    gi_fasta_file_name = 'selections_gi.faa'
    fasta_file_path = os.sep.join((outfile_dir, fasta_file_name))
    full_fasta_file_path = os.sep.join(
        (full_outfile_dir, fasta_file_name)
    )
    fasta_fileh = open(full_fasta_file_path, 'w')
    gi_fasta_file_path = os.sep.join((outfile_dir, gi_fasta_file_name))
    full_gi_fasta_file_path = os.sep.join(
        (full_outfile_dir, gi_fasta_file_name)
    )
    gi_fasta_fileh = open(full_gi_fasta_file_path, 'w')
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
            if len(proteins) > 1:
                for i, protein in enumerate(proteins):
                    jelesko_id = _make_jelesko_id(protein, i + 1)
                    _output_to_sel_files(
                        jelesko_id,
                        protein,
                        fasta_fileh,
                        gi_fasta_fileh,
                        map_fileh
                    )
            else:
                protein = proteins[0]
                jelesko_id = _make_jelesko_id(protein)
                _output_to_sel_files(
                    jelesko_id,
                    protein,
                    fasta_fileh,
                    gi_fasta_fileh,
                    map_fileh
                )

    finally:
        fasta_fileh.close()
        gi_fasta_fileh.close()
        map_fileh.close()

    # create an entry in the Selections table
    selection = models.SequenceSelection(
        search=search,
        sequences_file=fasta_file_path,
        gi_sequences_file=gi_fasta_file_path,
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
