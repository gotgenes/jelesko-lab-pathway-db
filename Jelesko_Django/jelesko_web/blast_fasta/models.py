from django.db import models

# Create your models here.

SEARCH_RESULTS_DIR = 'searches/%Y%m%d%H%M%S'
SELECTIONS_DIR = 'selects/%Y%m%d%H%M%S'

class Protein(models.Model):
    """A class to represent a protein downloaded from a repository."""

    gi = models.CharField(max_length=15, primary_key=True)
    accession = models.CharField(max_length=15)
    genus_species = models.CharField(max_length=100)
    annotation = models.TextField()
    download_date = models.DateTimeField()
    sequence = models.TextField()

    def __unicode__(self):
        return self.gi


class Search(models.Model):
    """A class to represent search runs."""

    program = models.CharField(max_length=20)
    results_file = models.FileField(
        upload_to=(SEARCH_RESULTS_DIR)
    )
    timestamp = models.DateTimeField()

    def __unicode__(self):
        return u'%s %s' % (self.program, self.timestamp)


class SequenceSelection(models.Model):
    """A class to represent a selection of sequences."""

    search = models.ForeignKey('Search')
    sequences_file = models.FileField(
        upload_to=(SELECTIONS_DIR)
    )
    map_file = models.FileField(upload_to='selections')
    timestamp = models.DateTimeField()
    comment = models.CharField(max_length=140, blank=True)

    def __unicode__(self):
        return self.timestamp


class FastaRun(models.Model):

    # the user-input FASTA formatted protein sequence
    query_seq = models.TextField()
    # -b "Number of sequence scores to be shown on output."
    number_sequence = models.PositiveIntegerField(blank=True)
    # -E "Limit the number of scores and alignments shown based on the
    # expected number of scores." Overrides the expectation value.
    number_alignment_highest = models.FloatField(default=10.0,
            blank=True)
    # -F "Limit the number of scores and alignments shown based on the
    # expected number of scores." Sets the highest E-value shown.
    number_alignment_lowest = models.FloatField(blank=True)
    mfoptions = [
            ('P250', 'PAM250'),
            ('P120', 'PAM120'),
            ('BL50', 'BLOSUM50'),
            ('BL62', 'BLOSUM62'),
            ('BL80', 'BLOSUM80')
    ]
    matrix_file = models.CharField(
            max_length=4,
            choices=mfoptions,
            default='BL50'
    )
    database_option = models.CharField(
            max_length=25,
            choices=BLAST_DBS,
            default=INITIAL_DB_CHOICE
    )
    ktupoptions = [(1, 1), (2, 2)]
    ktup = models.PositiveIntegerField(
            choices=ktupoptions,
            default=2,
            blank=True
    )
