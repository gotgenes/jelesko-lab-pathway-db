============================
Jelesko Pathway Evolution DB
============================

Introduction
============

This repository contains code and documentation for the GBCB 5874 project
with `Prof. John Jelesko`_.

For the impatient
=================

See if your question is in `How do I ...`_. Otherwise, keep reading.

Git repository layout
=====================

* ``Jelesko_Django``: Contains the code for the Django application. See
  `Deploying the FASTA Django Application`_
* ``README.rst``: this file
* ``fastatoflat``: converts FASTA formatted files to a flat file for DB
  import. See
  `How do I insert the FASTA-formatted protein sequences I've downloaded into the database?`
* ``ftpfetch``: contains the script to fetch NCBI protein data. See
  `How do I download all the protein sequences from the NCBI whole genome projects?`
* ``paper``: final report for the GBCB 5874 course
* ``rmduplicates``: removes duplicate entries from flat files for DB import.
  See `How do I remove duplicate entries from the flat file?`_


Deploying the FASTA Django Application
======================================

You are expected to be familiar with Django_ prior to deploying this site.
When in doubt, consult the Django documentation. This site was built using
Django 1.0.2, so the documentation is available at
http://docs.djangoproject.com/en/1.0/

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

Creating a branch to customize the site
---------------------------------------

You should create a new branch in which you can add your own site
customizations.

::

    git checkout -b localsettings master

Configuring the database
------------------------

If you're using Postgres or MySQL, you will need to create a database and a
user for your Django site. Grant the user enough permissions to create tables
and insert, select, and delete from the tables in the database. Mark down the
name of the database and the user for `Configuring the application`_.

If you're using sqlite3, you'll only need to create a database and give the
path to the file.

Configuring the application
---------------------------

The first step involves filling out settings under under ``$DJANGO_SITE/settings.py``. This includes, but is not limited to the following settings:

* ``DATABASE_ENGINE``
* ``DATABASE_NAME``
* ``DATABASE_USER``
* ``DATABASE_PASSWORD``
* ``MEDIA_ROOT``
* ``MEDIA_URL``
* ``TEMPLATE_DIRS``

Fill in the database information in the database fields using the information
from `Configuring the database`_.

You must define the ``MEDIA_ROOT`` and ``MEDIA_URL``. ``MEDIA_ROOT`` must
have read and write access for the user that Django is run under. When using
Django with Apache, this user is usually ``www-data`` on Debian-type systems,
or ``apache`` on Red Hat type systems. Verify this by looking under
``/etc/passwd``.

It is a *really* good idea to keep ``MEDIA_ROOT`` short. The FASTA programs
have a character limit of 121 characters for file paths, and the input and
output to the FASTA programs will be saved under the ``MEDIA_ROOT`` in
time-stamped directories.  Thus, *keep* ``MEDIA_ROOT`` *short*. Additionally,
to serve files under this directory by Apache, it must be under the
DocumentRoot.  For example, ``/var/www/html/jdbmedia/``. And in case you
didn't realize this yet, **it is a really good idea to keep** ``MEDIA_ROOT``
**short**!

Under the ``MEDIA_ROOT``, there must be two directories (also read-write-able
by the Django/Apache user): ``MEDIA_ROOT/selects/`` and
``MEDIA_ROOT/searches/``, to store selections and search program outputs,
respectively. Make sure all directories and files under ``MEDIA_ROOT`` have
the proper permissions for the Django/Apache user.

``MEDIA_URL`` should not be under the same Location as that used to access the
Django site. See `Configuring Apache`_ for more about the Location directive.

In ``TEMPLATE_DIRS``, add the path of ``$DJANGO_SITE``.

Next, in ``$DJANGO_SITE/blast_fasta/views.py``, fill out ``BLAST_DBS`` and
``BLAST_DB_PATHS``, making sure to use the proper path to the database on the
local filesystem. Make sure the paths in ``BLAST_DB_PATHS`` are accessible to
the Django/Apache user (i.e., under the ``DocumentRoot`` or otherwise aliased,
and with proper permissions).

Save your settings
^^^^^^^^^^^^^^^^^^

At this point, you need to commit your changes to the Git repository to your
local branch.

::

    git commit -am "Saving local settings."


Synchronizing the Django site to the database
---------------------------------------------

The Django site must synchronize with the database you're using.

::

    cd $DJANGO_SITE
    python manage.py syncdb

Configuring Apache
------------------

Make sure you have `mod_python`_ installed and running on your system.

Either in your main Apache configuration or in an auxiliary configuration you
will need to add a Location directive such as the following.

::

    <Location "/jeleskodb/">
        SetHandler python-program
        PythonHandler django.core.handlers.modpython
        PythonPath "['$REPO_PATH/Jelesko_Django/'] + sys.path"
        SetEnv DJANGO_SETTINGS_MODULE jelesko_web.settings
        PythonOption django.root /jeleskodb
        PythonDebug On
    </Location>

Note that this **must** be a Location directive, not a Directory directive,
since this isn't a physical directory on the file system.

The actual location is up to you. In this case, all pieces of the Django site
will be accessible under http://yoursite/jeleskodb/.


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

How do I download all the protein sequences from the NCBI whole genome projects?
--------------------------------------------------------------------------------

Use the ``ncbifastafetch.py`` script.

::

    cd $REPO_PATH/ftpfetch
    python ncbifastafetch.py --help

How do I insert the FASTA-formatted protein sequences I've downloaded into the database?
----------------------------------------------------------------------------------------

First, generate a flat tab-separated-values file from the FASTA files using
the ``fastatoflat.py`` script.

::

    cd $REPO_PATH/fastatoflat
    python fastatoflat.py --help

Once you've generated your flat file, you can use your database's import tool
to load it into the ``blast_fasta_protein`` table. For example, with MySQL,
you can use ``mysqlimport``:

::

    mysqlimport -d --columns="gi,accession,genus_species,annotation,download_date,sequence" --ignore-lines=1 -p DATABASE /path/to/blast_fasta_protein.txt

Read the documentation for your database to learn how to do this properly.

**NOTE:** Before you do this, you may need to remove duplicate entries (more
than one entry may have the same GI/identifier). See `How do I remove
duplicate entries from the flat file?`_

How do I remove duplicate entries from the flat file?
-----------------------------------------------------

Use the ``rmduplicates.py`` script.

::

    cd $REPO_PATH/rmduplicates
    python rmduplicates.py --help


.. _Prof. John Jelesko: http://www.ppws.vt.edu/~jelesko/
.. _Django: http://www.djangoproject.com/
.. _mod_python: http://www.modpython.org/
