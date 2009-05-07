Introduction
============

This repository contains code and documentation for the GBCB 5874 project
with `Prof. John Jelesko`_.

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
``jelesko-lab-pathway-db`` unless you specify a different DIRNAME. We refer to
this hereon as the repository path, also noted as ``$REPO_PATH``.

The code for the Django website for deployment lives under
``$REPO_PATH/Jelesko_Django/jelesko_web/``, which we refer to here as the
Django site, also ``$DJANGO_SITE``.

For example, say you downloaded the Git repository to ``/usr/local/``. Then
``$REPO_PATH`` is ``/usr/local/jelesko-lab-pathway-db/``, ``$DJANGO_SITE`` is
``/usr/local/jelesko-lab-pathway-db/Jelesko_Django/jelesko_web/``, and
``$DJANGO_SITE/blast_fasta/views.py`` is
``/usr/local/jelesko-lab-pathway-db/Jelesko_Django/jelesko_web/blast_fasta/views.py``.

Configuring the application
---------------------------

You must define the ``MEDIA_ROOT`` and ``MEDIA_URL``. ``MEDIA_ROOT`` must have
read and write access for the user that Django is run under. When using Django
with Apache, this user is usually ``www-data`` on Debian-type systems, or
``apache`` on Red Hat type systems. Verify this by looking under
``/etc/passwd``.

It is a **really good idea** to keep ``MEDIA_ROOT`` short. FASTA has a
character limit of 121 characters for file paths; the input and output to the
FASTA programs is saved under the ``MEDIA_ROOT`` in time-stamped directories.
Thus, keep ``MEDIA_ROOT`` short. Additionally, to serve files under this
directory by Apache, it must be under the DocumentRoot. For example,
``/var/www/html/jdbmedia/``.

Under the ``MEDIA_ROOT``, there must be two directories (also read-write-able
by the Django/Apache user): ``MEDIA_ROOT/selects/`` and
``MEDIA_ROOT/searches/``, to store selections and search program outputs,
respectively.

Fill out the following under ``$REPO_PATH/Jeleskso_
DATABASE_ENGINE
DATABASE_NAME
DATABASE_USER
DATABASE_PASSWORD

In TEMPLATE_DIRS, add the path to the template, which is under
``$REPO_PATH/Jelesko_Django/jelesko_web/`` in the Git repository

in ``REPO_PATH/Jelesko_Django/jelesko_web/blast_fasta/views.py``, fill in
choices for BLAST_DBS and BLAST_DB_PATHS, making sure to use the proper path
to the database on the local filesystem.

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

How do I export all the database's sequences in FASTA format?
-------------------------------------------------------------

::

    cd $REPO_PATH/Jelesko_Django/jelesko_web/
    python manage.py dbtofasta

See the help documentation for more information

::

    python manage.py dbtofasta --help


.. _`Prof. John Jelesko` http://www.ppws.vt.edu/~jelesko/
