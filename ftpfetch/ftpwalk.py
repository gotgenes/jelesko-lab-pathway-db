#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Walk a hierarchy of files using FTP (Adapted from os.walk()).

"""

# This code is adapted from Martin Blais's original recipe at
# http://code.activestate.com/recipes/499334/


def ftpwalk(ftp, top, topdown=True, onerror=None):
    """
    Generator that yields tuples of (root, dirs, nondirs).
    """
    # Make the FTP object's current directory to the top dir.
    ftp.cwd(top)
    top = ftp.pwd()

    # We may not have read permission for top, in which case we
    # can't get a list of the files the directory contains.
    # os.path.walk always suppressed the exception then, rather than
    # blow up for a minor reason when (say) a thousand readable
    # directories are still left to visit.  That logic is copied
    # here.
    try:
        dirs, nondirs = _ftp_listdir(ftp)
    except os.error, err:
        if onerror is not None:
            onerror(err)
        return

    if topdown:
        yield top, dirs, nondirs

    for dname in dirs:
        path = '/'.join((top, dname))
        for x in ftpwalk(ftp, path, topdown, onerror):
            yield x

    if not topdown:
        yield top, dirs, nondirs


def _ftp_listdir(ftp):
    """
    List the contents of the FTP opbject's cwd and return two lists of
    subdirectory names and filenames. If the path is a symbolic link,
    'link' is set to the target of the link (note that both files and
    directories can be symbolic links).

    Note: we only parse Linux/UNIX style listings; this could easily be
    extended.

    """

    dirs, nondirs = [], []
    listing = []
    ftp.retrlines('LIST', listing.append)
    for line in listing:
        # Parse, assuming a UNIX listing
        words = line.split(None, 8)
        if len(words) < 6:
            print >> sys.stderr, 'Warning: Error reading short line', line
            continue

        # Get the filename.
        filename = words[-1].lstrip()
        if filename in ('.', '..'):
            continue

        # Get the type and mode.
        mode = words[0]

        # Get the link target, if the file is a symlink.
        i = filename.find(" -> ")
        if i >= 0 and mode.startswith('l'):
            # words[0] had better start with 'l'...
            extra = filename[i+4:]
            filename = filename[:i]


        if mode[0] == 'd':
            dirs.append(filename)
        else:
            nondirs.append(filename)
    return dirs, nondirs

