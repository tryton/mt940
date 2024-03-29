mt940
=====

mt940 is a parser for MT940 files.

Nutshell
--------

Import::

    >>> import os
    >>> from mt940 import MT940

Instanciate::

    >>> mt940 = MT940('mt940/MT940.txt')

The statements::

    >>> len(mt940.statements)
    2
    >>> statement = mt940.statements[0]
    >>> statement.account
    '123456789'
    >>> statement.information
    '13501/1'
    >>> start_balance = statement.start_balance
    >>> start_balance.date
    datetime.date(2012, 5, 11)
    >>> start_balance.amount
    Decimal('5138.61')
    >>> start_balance.currency
    'EUR'
    >>> end_balance = statement.end_balance
    >>> end_balance.date
    datetime.date(2012, 5, 14)
    >>> end_balance.amount
    Decimal('5638.62')
    >>> end_balance.currency
    'EUR'

The transactions::

    >>> len(statement.transactions)
    3
    >>> transaction, _, _ = statement.transactions
    >>> transaction.date
    datetime.date(2012, 5, 12)
    >>> transaction.booking
    datetime.date(2012, 5, 14)
    >>> transaction.amount
    Decimal('500.01')
    >>> transaction.id
    'N654'
    >>> transaction.reference
    'NONREF'
    >>> transaction.additional_data
    '987654321'
    >>> transaction.description # doctest: +NORMALIZE_WHITESPACE
    '/TRTP/SEPA OVERBOEKING/IBAN/FR12345678901234/BIC/GEFRADAM\n/NAME/QASD JGRED/REMI/Dit zijn de omschrijvingsregels/EREF/NOTPRO\nVIDED'

To report issues please visit the `mt940 bugtracker`_.

.. _mt940 bugtracker: https://bugs.tryton.org/mt940
