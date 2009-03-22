#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Tests for ncbifastafetch.py

"""

__author__ = 'Chris Lasher'
__email__ = 'chris DOT lasher <AT> gmail DOT com'

import os
import sys
import unittest

parpath = os.path.join(os.path.dirname(sys.argv[0]), os.pardir)
sys.path.insert(0, os.path.abspath(parpath))
import ncbifastafetch


class NcbiFastaFetchTests(unittest.TestCase):
    """
    Tests for ncbifastafetch.

    """

    def test_parse_dir_listing(self):
        """_parse_dir_listing()"""

        case = """\
dr-xr-xr-x   7 ftp      anonymous    12288 Mar 20 17:29 1000genomes
-r--r--r--   1 ftp      anonymous     1868 Mar 28  2008 README.ftp
lr--r--r--   1 ftp      anonymous       31 Jan  3  2008 asn1-converters -> ./toolbox/ncbi_tools/converters
dr-xr-xr-x   8 ftp      anonymous     4096 Sep 29  2004 blast
dr-xr-xr-x   3 ftp      anonymous     4096 Sep 13  2004 cgap
dr-xr-xr-x   4 ftp      anonymous     4096 Jan  8 20:45 cn3d
dr-xr-xr-x  18 ftp      anonymous     4096 Mar 18 14:12 dbgap
dr-xr-xr-x  11 ftp      anonymous     4096 Jun  4  2006 entrez
dr-xr-xr-x   6 ftp      anonymous     4096 Aug  4  2006 fa2htgs
dr-xr-xr-x  10 ftp      anonymous   143360 Feb 19 00:51 genbank
dr-xr-xr-x   6 ftp      anonymous     4096 Dec 18  2006 gene
dr-xr-xr-x  52 ftp      anonymous     8192 Mar  6 20:26 genomes
dr-xr-xr-x  11 ftp      anonymous     4096 Mar 13 23:20 mmdb
dr-xr-xr-x   5 ftp      anonymous   126976 Feb 19 01:12 ncbi-asn1
dr-xr-xr-x 133 ftp      anonymous    12288 Mar 13 16:20 pub
dr-xr-xr-x  11 ftp      anonymous     4096 Mar 17 00:04 pubchem
dr-xr-xr-x   2 ftp      anonymous     4096 Mar 21 01:15 pubmed
dr-xr-xr-x  15 ftp      anonymous     4096 Mar 19 12:20 refseq
dr-xr-xr-x  57 ftp      anonymous     8192 Aug 20  2008 repository
dr-xr-xr-x   5 ftp      anonymous     4096 Feb 23 16:26 sequin
dr-xr-xr-x   8 ftp      anonymous     4096 Jan 30  2008 sky-cgh
dr-xr-xr-x  19 ftp      anonymous     4096 Mar 12 13:48 snp
dr-xr-xr-x   9 ftp      anonymous     4096 Jan 26 20:30 sra
dr-xr-xr-x   2 ftp      anonymous     4096 Sep 29  2004 tech-reports
dr-xr-xr-x  13 ftp      anonymous     4096 Oct 16  2006 toolbox
dr-xr-xr-x   4 ftp      anonymous     4096 Sep 14  2004 tpa
"""
        expected = ['1000genomes', 'blast', 'cgap', 'cn3d', 'dbgap',
                'entrez', 'fa2htgs', 'genbank', 'gene', 'genomes',
                'mmdb', 'ncbi-asn1', 'pub', 'pubchem', 'pubmed',
                'refseq', 'repository', 'sequin', 'sky-cgh', 'snp',
                'sra', 'tech-reports', 'toolbox', 'tpa',
                ]

        self.assertEqual(
                ncbifastafetch._parse_dir_listing(case),
                expected
        )


if __name__ == '__main__':
    unittest.main()
