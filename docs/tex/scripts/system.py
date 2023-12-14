# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Contributors to the PhysLight Project.

"""
Simple system-level support infrastructure.
When several modules all import this module, the global variables in the module will be shared
One valuable consequence is that the calling app can register searchpaths before calling import,
and then importing the other modules will find the searchpaths already registered
"""

import os.path
import csv
import importlib.metadata
import packaging.version
from typing import Optional

searchpaths: {str, list[str]} = {}


def register_searchpaths(kind: str, paths: list[str]):
    """ Adds the list `paths` to the searchpaths of kind `kind` """
    global searchpaths
    searchpaths[kind] = paths


def resolve_path(kind, tail):
    """ Returns the resolved path against the searchpaths of kind `kind`.
        If tail is an absolute path it is returned as-is
        If tail is not found in the searchpaths, `None` is returned
    """
    global searchpaths
    if kind not in searchpaths:
        raise KeyError("Unknown path kind '%s'" % kind)
    if os.path.isabs(tail):
        return tail
    for d in searchpaths[kind]:
        fullpath = os.path.join(d, tail)
        if os.path.exists(fullpath):
            return fullpath
        #print('notfound ', fullpath)
    return None


def readCSV_rows(fname: str, NaN_as_zero=False) -> list[list[str]]:
    """
    Return a list of rows from a CSV file
    Skip empty rows and lines starting with \s*#
    """
    rows: list[list[str]] = []
    with open(fname, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) and row[0].lstrip()[0] != '#':
                if NaN_as_zero:
                    rows.append([e if e.upper() != "NAN" else 0 for e in row])
                else:
                    rows.append(row)
    return rows


def readCSV_columns(fname: str, NaN_as_zero=False) -> list[list[str]]:
    """
    Return a list of columns from a CSV file
    Skip empty rows and lines starting with \s*#
    """
    rows = readCSV_rows(fname, NaN_as_zero=NaN_as_zero)
    cols: list[list[str]] = [list(i) for i in zip(*rows)]
    return cols
