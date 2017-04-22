#!/usr/bin/env python
#
# Copyright (C) 2017 Martin Owens
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library.
#
"""
Test the creation, reading and writing on environment variables.
"""

import os
import sys

sys.path.insert(0, '../')

import unittest
from collections import OrderedDict
from crontab import CronTab
try:
    from test import test_support
except ImportError:
    from test import support as test_support

INITIAL_TAB = """PERSONAL_VAR=bar

CRON_VAR=fork
34 12 * * * eat_soup

CRON_VAR=spoon
35 12 * * * eat_salad

CRON_VAR=knife
36 12 * * * eat_icecream

SECONDARY=fork
38 12 * * * eat_steak
"""

class EnvTestCase(unittest.TestCase):
    """Test vixie cron user addition."""
    def setUp(self):
        self.crontab = CronTab(tab=INITIAL_TAB)

    def test_01_consistancy(self):
        """Read in crontab and write out the same"""
        self.assertEqual(INITIAL_TAB, str(self.crontab))

    def test_02_top_vars(self):
        """Whole file env variables"""
        crontab = CronTab(tab="SHELL=dash\n")
        self.assertEqual(str(crontab), "SHELL=dash\n")
        self.assertEqual(crontab.env['SHELL'], 'dash')
        crontab.env['SHELL'] = 'bash'
        self.assertEqual(str(crontab), "SHELL=bash\n")
        self.assertEqual(crontab.env['SHELL'], 'bash')

    def test_03_get_job_var(self):
        """Test each of the job env structures"""
        for job, expected in zip(self.crontab, [
            {'PERSONAL_VAR': 'bar', 'CRON_VAR': 'fork'},
            {'PERSONAL_VAR': 'bar', 'CRON_VAR': 'spoon'},
            {'PERSONAL_VAR': 'bar', 'CRON_VAR': 'knife'},
            {'PERSONAL_VAR': 'bar', 'CRON_VAR': 'knife', 'SECONDARY': 'fork'},
          ]):
            self.assertEqual(OrderedDict(job.env.all()), expected)

    def test_04_set_job_var(self):
        """Test that variables set are applied correctly"""
        self.crontab[1].env['CRON_VAR'] = 'javlin'
        self.assertEqual(self.crontab[1].env.all(),
            {'PERSONAL_VAR': 'bar', 'CRON_VAR': 'javlin'})
        self.crontab[2].env['CRON_VAR'] = 'javlin'
        self.assertEqual(self.crontab[2].env.all(),
            {'PERSONAL_VAR': 'bar', 'CRON_VAR': 'javlin'})
        self.assertEqual(self.crontab[3].env['PERSONAL_VAR'], 'bar')
        self.assertEqual(self.crontab[3].env.all(),
            {'PERSONAL_VAR': 'bar', 'CRON_VAR': 'javlin', 'SECONDARY': 'fork'})

        self.crontab.env['PERSONAL_VAR'] = 'foo'
        self.assertEqual(self.crontab[2].env.all(),
            {'PERSONAL_VAR': 'foo', 'CRON_VAR': 'javlin'})

        self.crontab.env['CRON_VAR'] = 'fork'
        self.assertEqual(self.crontab[0].env.all(),
            {'PERSONAL_VAR': 'foo', 'CRON_VAR': 'fork'})

        self.assertEqual(str(self.crontab), """PERSONAL_VAR=foo
CRON_VAR=fork

34 12 * * * eat_soup

CRON_VAR=javlin
35 12 * * * eat_salad

36 12 * * * eat_icecream

SECONDARY=fork
38 12 * * * eat_steak
""")

    def test_05_no_env(self):
        """Test that we get an error asking for no var"""
        with self.assertRaises(KeyError):
            self.crontab.env['BLUE_BOTTLE']
        with self.assertRaises(KeyError):
            self.crontab[0].env['RED_BOTTLE']

if __name__ == '__main__':
    test_support.run_unittest(EnvTestCase)