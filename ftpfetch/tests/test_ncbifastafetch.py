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


        cases = (
                    (
'dr-xr-xr-x   7 ftp      anonymous    12288 Mar 20 17:29 1000genomes',
'1000genomes'),
                    (
'-r--r--r--   1 ftp      anonymous     1868 Mar 28  2008 README.ftp',
None),
                    (
'lr--r--r--   1 ftp      anonymous       31 Jan  3  2008 asn1-converters -> ./toolbox/ncbi_tools/converters',
None),
        )
        for case, expected in cases:
            result = []
            ncbifastafetch._parse_dir_line(case, result)
            if expected:
                self.assertEqual(result, [expected])
            else:
                self.assertEqual(result, [])


    def test_identify_faa(self):
        """_identify_faa()"""

        pass


if __name__ == '__main__':
    unittest.main()
