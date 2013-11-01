#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013, Cédric Krier
# Copyright (c) 2013, B2CK
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""Test MT940
"""
import os
import unittest
import datetime
from decimal import Decimal

here = os.path.dirname(__file__)
from mt940 import MT940, rabo_description


class TestMT940(unittest.TestCase):

    def setUp(self):
        self.mt940 = MT940(os.path.join(here, 'MT940.txt'))

    def test_number_statements(self):
        "Test number of statements"
        self.assertEqual(len(self.mt940.statements), 1)

    def test_statement_account(self):
        "Test statement account"
        self.assertEqual(self.mt940.statements[0].account, '123456789')

    def test_statement_information(self):
        "Test statement information"
        self.assertEqual(self.mt940.statements[0].information, '13501/1')

    def test_statement_start_balance(self):
        "Test statement start balance"
        start_balance = self.mt940.statements[0].start_balance
        self.assertEqual(start_balance.date, datetime.date(2012, 5, 11))
        self.assertEqual(start_balance.amount, Decimal('5138.61'))
        self.assertEqual(start_balance.currency, 'EUR')

    def test_statement_end_balance(self):
        "Test statement end balance"
        end_balance = self.mt940.statements[0].end_balance
        self.assertEqual(end_balance.date, datetime.date(2012, 5, 14))
        self.assertEqual(end_balance.amount, Decimal('5638.62'))
        self.assertEqual(end_balance.currency, 'EUR')

    def test_transaction(self):
        "Test transaction"
        transaction, = self.mt940.statements[0].transactions
        self.assertEqual(transaction.date, datetime.date(2012, 5, 12))
        self.assertEqual(transaction.booking, datetime.date(2012, 5, 14))
        self.assertEqual(transaction.amount, Decimal('500.01'))
        self.assertEqual(transaction.id, 'N654')
        self.assertEqual(transaction.reference, 'NONREF')
        self.assertEqual(transaction.account, '987654321')
        self.assertEqual(transaction.description,
            '''/TRTP/SEPA OVERBOEKING/IBAN/FR12345678901234/BIC/GEFRADAM
/NAME/QASD JGRED/REMI/Dit zijn de omschrijvingsregels/EREF/NOTPRO
VIDED''')


class TestRaboDescription(unittest.TestCase):

    def test_one_tag(self):
        self.assertEqual(rabo_description('/EREF/foo'), {'eref': 'foo'})

    def test_empty_tags(self):
        self.assertEqual(rabo_description('/BENM//NAME/Doe'),
            {'benm': '', 'name': 'Doe'})

    def test_long_tags(self):
        self.assertEqual(rabo_description(
                '/ORDP//NAME/Doe/REMI//CDTRREFTP//CD/SCOR/ISSR/CUR/CDTRREF/'
                '12345'
                )['cdtrref'], '12345')

    def test_non_rabo(self):
        self.assertEqual(rabo_description('foo'), {})
        self.assertEqual(rabo_description('/FOO/BAR/NAME/'), {})

if __name__ == '__main__':
    unittest.main()
