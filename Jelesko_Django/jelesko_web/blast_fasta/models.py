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
    comment = models.CharField(max_length=140)

    def __unicode__(self):
        return self.timestamp

