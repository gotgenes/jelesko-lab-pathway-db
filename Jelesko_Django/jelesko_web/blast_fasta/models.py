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
