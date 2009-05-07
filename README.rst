Introduction
============

This repository contains code and documentation for the GBCB 5874 project
with Dr. John Jelesko.

Deploying the FASTA Django Application
======================================

Downloading the application
---------------------------

The authoritative version of this application is hosted at GitHub under Chris
Lasher's master branch at:
http://github.com/gotgenes/jelesko-lab-pathway-db/tree/master

Obtain the code for this repository using

::
    git clone git://github.com/gotgenes/jelesko-lab-pathway-db.git [DIRNAME]

This will create a new directory under your present one called
jelesko-lab-pathway-db unless you specify a different DIRNAME. We refer to
this hereon as the repository path.

Configuring the application
---------------------------

You must define the ``MEDIA_ROOT`` and ``MEDIA_URL``. ``MEDIA_ROOT`` must have
read and write access for the user that Django is run under. When using Django
with Apache, this user is usually ``www-data`` on Debian-type systems, or
``apache`` on RedHat type systems. Verify this by looking under
``/etc/passwd``.

It is a really Good Idea (TM) to keep MEDIA_ROOT short. FASTA has a character
limit of 121 characters for file paths; the input and output to the FASTA
programs is saved under the MEDIA_ROOT in time-stamped directories. Thus, keep
MEDIA_ROOT short. Additionally, to serve files under this directory by Apache,
it must be under the DocumentRoot. For example, '/var/www/html/jdbmedia/'.

Under the MEDIA_ROOT, there must be two directories (also read-write-able by
the Django/Apache user): 'MEDIA_ROOT/selects/' and 'MEDIA_ROOT/searches/',
to store selections and search program outputs, respectively.

Fill out the following under 
DATABASE_ENGINE
DATABASE_NAME
DATABASE_USER
DATABASE_PASSWORD

In TEMPLATE_DIRS, add the path to the template, which is under
Jelesko_Django/jelesko_web/ in the Git repository

in Jelesko_Django/jelesko_web/blast_fasta/views.py, fill in choices for
BLAST_DBS and BLAST_DB_PATHS, making sure to use the proper path to the
database on the local filesystem.

dump the database to FASTA file by python manage.py dbtofasta -o
/your/desired/path. Make sure this path and the output are owned by the Apache
user, e.g.,

::
    chown -R apache:apache /your/desired/path

Make a directory for your static files (MEDIA_ROOT), e.g.,

::
    mkdir /var/www/jeleskodb

Then make subdirectories under this

::
    mkdir /var/www/jeleskodb/selects
    mkdir /var/www/jeleskodb/searches

Then make sure these are writeable by the Apache user

::
    chown -R apache:apache /var/www/jeleskodb

How do I ...
============

How do I export all sequences from the database as a FASTA file for a
subject database? ==

::

    cd $REPOSITORY_PATH/Jelesko_Django/jelesko_web/
    python manage.py 
