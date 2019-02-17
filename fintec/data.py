#! /usr/bin/env python3
# -*- coding: utf-8 -*-

""" Gathering and manipulating data. """
import os
from enum import Enum
from typing import Union, Sequence

import pandas as pd

__all__ = ['U_FIN_DATA_BASE', 'df_rates', 'Idx']

_STRINT = Union[str, int]
_IDXCOL = Union[_STRINT, Sequence[int], None]

U_FIN_DATA_BASE = 'U_FIN_DATA_BASE'
""" The environment variable name for the data base directory. """


def _data_path(filename: str) -> str:
    """
    Get the path to file f, relative to the environment variable 'U_FIN_DATA_BASE'.
    If the environment variable is not found uses 'data' as default.

    :param filename: the filename or path to append to the data base path.
    :return: complete path to the data base file.
    """
    return os.path.join(os.getenv(U_FIN_DATA_BASE, 'data'), filename)


def _read_data(filename: str, index_col: _IDXCOL = 0, sheet_name: _STRINT = 0):
    """
    Read in a DataFrame, either from a csv file or an Excel file.

    :param filename: file to read
    :param index_col: int, str or sequence or False or None, default 0
    :param sheet_name: if it is an Excel file, the name or index number of the sheet, default 0
    :return: pandas.DataFrame
    """
    if os.path.splitext(filename)[1].lower() == '.csv':
        df = pd.read_csv(_data_path(filename), index_col=index_col)
    else:
        df = pd.read_excel(_data_path(filename), sheet_name=sheet_name, index_col=index_col)
    return df


def _read_date_indexed_data(filename: str, index_col: _IDXCOL = 0, sheet_name: _STRINT = 0):
    """
    Read data with a datetime index, interpolate nearest.

    :param filename: file to read
    :param index_col: int, str or sequence or False or None, default 0
    :param sheet_name: if it is an Excel file, the name or index number of the sheet, default 0
    :return: pandas.DataFrame
    """
    df = _read_data(filename, index_col, sheet_name)
    df.index = pd.to_datetime(df.index)
    df = df.interpolate(method='nearest', axis=0)
    return df


def df_rates(filename='fondsen.xlsx', index_col: _IDXCOL = 0, sheet_name: _STRINT = 'koersen') -> pd.DataFrame:
    """
    Read file filename relative to data_path, sheet 'sheet_name'. The index_col should be of type date.
    Fills NaN's, except leading and trailing. The type of file and how it is read is determined
    by the file extension, either .csv or .xlsx.

    :param filename: file to read
    :param index_col: int, str or sequence or False or None, default 0
    :param sheet_name: if it is an Excel file, the name or index number of the sheet, default 'koersen'
    :return: pandas.DataFrame
    """
    return _read_date_indexed_data(filename, index_col, sheet_name)


class Idx(Enum):
    """
    Enumeration of indices.
    """
    DOW = 'us-30'
    SPX = 'us-spx-500'
    NASDAQ100 = 'nq-100'
    AEX = 'netherlands-25'
    DAX = 'germany-30'
    FTSE = 'uk-100'
    SHANGHAI = 'shanghai-composite'

    def describe(self):
        return self.name, self.value

    def filename(self):
        """
        Local filename of the index.
        :return: filename of the index
        """
        return _data_path('indices/{}.csv'.format(self.name.lower()))

    def ic_historical_data_url(self):
        """
        URL of the index history.
        :return: URL of the index history
        """
        return 'https://www.investing.com/indices/{}-historical-data'.format(self.value)

    def init_file(self):
        """
        Local filename of the initial file as downloaded manually.
        :return: filename of the initial file
        """
        return 'html/{}.html'.format(self.name.lower())

