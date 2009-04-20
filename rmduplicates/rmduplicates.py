
#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Remove duplicate entries based on GI numbers and prints lines to STDOUT.
"""

__author__ = 'Chris Lasher'
__email__ = 'chris DOT lasher <AT> gmail DOT com'

import sys
import optparse

def make_cli_parser():
    """Creates the command line interface."""

    usage = '\n'.join(("""\
python %prog [OPTIONS] RECORDSFILE

ARGUMENTS:
  RECORDSFILE: a file of protein records
""",
            __doc__
    ))

    cli_parser = optparse.OptionParser(usage)
    return cli_parser

def main(argv):
    cli_parser = make_cli_parser()
    opts, args = cli_parser.parse_args(argv)
    if len(args) != 1:
        cli_parser.error("Please give a file name.")
    records_file = open(args[0])

    seen = {}
    for line in records_file:
        line = line.rstrip()
        gi = line.split(None, 1)[0]
        if gi not in seen:
            seen[gi] = True
            print line

    records_file.close()


if __name__ == '__main__':
    main(sys.argv[1:])

