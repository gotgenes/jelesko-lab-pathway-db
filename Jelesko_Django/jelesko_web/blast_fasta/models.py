from django.db import models

# Create your models here.

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
    results_file = models.FileField(upload_to="searchresults")
    timestamp = models.DateTimeField()

    def __unicode__(self):
        return u'%s %s' % (self.program, self.timestamp)


class SequenceSelection(models.Model):
    """A class to represent a selection of sequences."""

    search = models.ForeignKey('Search')
    sequences_file = models.FileField(upload_to="selections")
    translation_file = models.FileField(upload_to="selections")
    timestamp = models.DateTimeField()

    def __unicode__(self):
        return self.timestamp

