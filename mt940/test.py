#!/usr/bin/env python
# This file is part of mt940.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
"""Test MT940
"""
import datetime
import doctest
import io
import os
import sys
import unittest
from decimal import Decimal

from mt940 import (MT940, rabo_description, abn_amro_description,
    ing_description, regiobank_description)

here = os.path.dirname(__file__)
readme = os.path.normpath(os.path.join(here, '..', 'README'))


class TestMT940(unittest.TestCase):

    def setUp(self):
        self.mt940 = MT940(os.path.join(here, 'MT940.txt'))

    def test_number_statements(self):
        "Test number of statements"
        self.assertEqual(len(self.mt940.statements), 2)

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

    def test_statement_description(self):
        self.assertEqual(self.mt940.statements[0].description, '/SUM/')

    def test_transaction(self):
        "Test transaction"
        transaction = self.mt940.statements[0].transactions[0]
        self.assertEqual(transaction.date, datetime.date(2012, 5, 12))
        self.assertEqual(transaction.booking, datetime.date(2012, 5, 14))
        self.assertEqual(transaction.amount, Decimal('500.01'))
        self.assertEqual(transaction.id, 'N654')
        self.assertEqual(transaction.reference, 'NONREF')
        self.assertEqual(transaction.additional_data, '987654321')
        self.assertEqual(transaction.description,
            '''/TRTP/SEPA OVERBOEKING/IBAN/FR12345678901234/BIC/GEFRADAM
/NAME/QASD JGRED/REMI/Dit zijn de omschrijvingsregels/EREF/NOTPRO
VIDED''')

        transaction = self.mt940.statements[0].transactions[1]
        self.assertEqual(transaction.date, datetime.date(2014, 12, 5))
        self.assertEqual(transaction.booking, datetime.date(2014, 12, 5))
        self.assertEqual(transaction.amount, Decimal('-15.67'))
        self.assertEqual(transaction.id, 'IDXX')
        self.assertEqual(transaction.reference, 'REF'),
        self.assertEqual(transaction.institution_reference, '')
        self.assertEqual(transaction.additional_data, 'DATA')
        self.assertEqual(transaction.description, '')

        transaction = self.mt940.statements[0].transactions[2]
        self.assertEqual(transaction.date, datetime.date(2017, 12, 14))
        self.assertEqual(transaction.booking, None)
        self.assertEqual(transaction.amount, Decimal('15.67'))
        self.assertEqual(transaction.id, 'TIDX')
        self.assertEqual(transaction.reference, 'TEST'),
        self.assertEqual(transaction.institution_reference, 'REFERENCE')
        self.assertEqual(transaction.additional_data, None)
        self.assertEqual(transaction.description, '')


class TestMT940Stream(TestMT940):

    def setUp(self):
        with io.open(os.path.join(here, 'MT940.txt')) as fp:
            self.mt940 = MT940(fp, encoding='ascii')


class TestMT940Optional(unittest.TestCase):

    def setUp(self):
        self.mt940 = MT940(os.path.join(here, 'MT940-optional.txt'))

    def test_statement_start_balance(self):
        "Test statement has not start balance"
        start_balance = self.mt940.statements[0].start_balance
        self.assertEqual(start_balance, None)

    def test_statement_end_balance(self):
        "Test statement has no end balance"
        end_balance = self.mt940.statements[0].end_balance
        self.assertEqual(end_balance, None)

    def test_statement_description(self):
        "Test statement has no description"
        description = self.mt940.statements[0].description
        self.assertEqual(description, None)


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

    def test_mixed_tags(self):
        self.assertEqual(
            rabo_description(
                '/EREF/0007301960/ORDP//NAME/Acist Europe B.V./ADDR/'
                'Heerlen 6422 PH Heerlen NL/REMI//INV/16000291 29.7.2016'),
            {'eref': '0007301960', 'ordp': '',
                'name': 'Acist Europe B.V.',
                'addr': 'Heerlen 6422 PH Heerlen NL',
                'remi': '/INV/16000291 29.7.2016'})


class TestABNAMRODescription(unittest.TestCase):

    def test_account(self):
        self.assertEqual(abn_amro_description('12.34.56.789 John Doe'),
            {'account': '123456789'})

    def test_giro(self):
        self.assertEqual(abn_amro_description('GIRO 4090309'),
            {'account': '4090309'})

    def test_tag(self):
        self.assertEqual(abn_amro_description(
                '''/TRTP/SEPA OVERBOEKING/IBAN/FR001234567890/BIC/GEF
RADAM/NAME/ENERGIE BEDRIJF/EREF/NOTPROVIDED'''), {
                'trtp': 'SEPA OVERBOEKING',
                'iban': 'FR001234567890',
                'bic': 'GEFRADAM',
                'name': 'ENERGIE BEDRIJF',
                'eref': 'NOTPROVIDED',
                })

    def test_non_abn_amro(self):
        self.assertEqual(abn_amro_description('foo'), {})
        self.assertEqual(rabo_description('/FOO/BAR/NAME/'), {})


class TestINGDescription(unittest.TestCase):

    def test_tag(self):
        description = """/EREF/170330P40411570.4342.2964442//CNTP/
NL94RABO0123456789/RABONL2U/ENERGIE BEDRIJF///REMI/USTD//
170330/REM INFO/"""

        self.assertEqual(ing_description(description), {
                'eref': '170330P40411570.4342.2964442',
                'cntp': {
                    'account_number': 'NL94RABO0123456789',
                    'bic': 'RABONL2U',
                    'name': 'ENERGIE BEDRIJF',
                    'city': '',
                    },
                'remi': {
                    'code': 'USTD',
                    'issuer': '',
                    'remittance_info': '170330/REM INFO',
                    },
                })

    def test_non_ing(self):
        self.assertEqual(ing_description('foo'), {})
        self.assertEqual(ing_description('/FOO/BAR/NAME/'), {})


class TestRegioBankDescription(unittest.TestCase):

    def test_reference(self):
        description = """0102792984 jyhhenewr f j k

rgt-test-004"""

        self.assertEqual(regiobank_description(description), {
                'account_number': '0102792984',
                'name': 'jyhhenewr f j k',
                'address': '',
                'reference': 'rgt-test-004',
                })

    def test_sepa(self):
        description = """0707464188 dsfg w van

aan dsfg w van,nl04asnb070746418 8,sct2013021540684000000000004,
t est 1"""

        self.assertEqual(regiobank_description(description), {
                'account_number': '0707464188',
                'name': 'dsfg w van',
                'address': '',
                'iban': 'nl04asnb070746418 8',
                'remittance_info': 'sct2013021540684000000000004',
                'description': 't est 1',
                })

    def test_non_regiobank(self):
        self.assertEqual(regiobank_description('foo'), {})
        description = """foo
bar
test"""
        self.assertEqual(regiobank_description(description), {})


def test_suite():
    suite = additional_tests()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(TestMT940))
    return suite


def additional_tests():
    suite = unittest.TestSuite()
    if os.path.isfile(readme):
        suite.addTest(doctest.DocFileSuite(readme, module_relative=False))
    return suite


def main():
    suite = test_suite()
    runner = unittest.TextTestRunner()
    return runner.run(suite)


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))))
    sys.exit(not main().wasSuccessful())
