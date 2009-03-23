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

    def test_identify_faa(self):
        """_identify_faa()"""

        cases = [
                'masking_coordinates.gz',
                'mm_alt_chr1.fa.gz',
                'NC_010002.faa',
                'protein.fa.gz'
                ]
        expected = cases[-2:]

        self.assertEqual(
                ncbifastafetch._identify_faa(cases),
                expected
        )


if __name__ == '__main__':
    unittest.main()
