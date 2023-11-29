#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © 2021 Massachusetts Institute of Technology.
# SPDX-FileCopyrightText: © 2021 Lee McCuller <mcculler@caltech.edu>
# NOTICE: authors should document their contributions in concisely in NOTICE
# with details inline in source files, comments, and docstrings.
"""
"""
from collections import abc
import numpy as np
from .any_io import (
    load_any,
    write_any,
)

from .csv_io import (
    load_csv,
)

from .types import (
    type2type,
    ext2type,
    type2features,
    determine_type,
)

from .utilities import (
    subkey_search,
    load_ls,
)


def save(fname, d):
    typeB = determine_type(fname)
    write_any(
        fname=typeB.fname,
        ftype=typeB.ftype,
        fdict=d,
    )


def load(fname, ftype=None):
    typeB = determine_type(fname)
    if ftype is None:
        ftype = typeB.ftype

    return load_any(
        fname=typeB.fname,
        ftype=ftype,
    )


def compare_deep(d1, d2):
    """
    This function walks down into dictionaries and lists to perform an element-by-element comparison.
    It is different than just the python == operator on dictionaries because it handles numpy arrays
    appropriately using np.all
    """
    if isinstance(d1, abc.Mapping):
        if len(d1) != len(d2):
            return False
        for k, v in d1.items():
            try:
                if not compare_deep(v, d2[k]):
                    return False
            except KeyError:
                return False
            return True
    elif isinstance(d1, np.ndarray):
        if not isinstance(d2, np.ndarray):
            return False
        try:
            return np.all(d1 == d2)
        except Exception:
            return False
    elif isinstance(d1, np.generic):
        if not isinstance(d2, np.generic):
            return False
        try:
            return d1.item() == d2.item()
        except Exception:
            return False
    elif isinstance(d1, (list, tuple)):
        if len(d1) != len(d2):
            return False
        for idx, v in enumerate(d1):
            if not compare_deep(v, d2[idx]):
                return False
            return True
    else:
        return d1 == d2


__all__ = [
    "load_any",
    "write_any",
    "load_csv",
    "type2type",
    "ext2type",
    "type2features",
    "determine_type",
    "subkey_search",
    "save",
    "load",
    "load_ls",
    "compare_deep",
]
