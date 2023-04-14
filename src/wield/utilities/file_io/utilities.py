#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © 2021 Massachusetts Institute of Technology.
# SPDX-FileCopyrightText: © 2021 Lee McCuller <mcculler@caltech.edu>
# NOTICE: authors should document their contributions in concisely in NOTICE
# with details inline in source files, comments, and docstrings.
"""
"""
import collections
import numpy as np
import collections
import sys


# unique element to indicate a default argument
_NOARG = lambda: _NOARG
NOARG = ("NOARG", _NOARG)


def subkey_search(fdict, subkey, default=NOARG):
    if subkey is None:
        return fdict
    subdict = fdict
    skeys = subkey.split(".")

    while skeys:
        if not isinstance(subdict, collections.abc.Mapping):
            raise TypeError("Intermediate type not a dictionary")

        try:
            subdict = subdict[".".join(skeys)]
        except KeyError:
            pass
        else:
            break

        for idx in range(1, len(skeys)):
            semikey = ".".join(skeys[:-idx])
            try:
                subdict = subdict[semikey]
            except KeyError:
                pass
            else:
                skeys = skeys[-idx:]
                break
        else:
            if default is NOARG:
                # this is the for-else syntax, only triggered if the for loop never
                # finds a match
                raise KeyError("Could not recursively find {}".format(subkey))
            else:
                return default
    return subdict


def dump_obj(d):
    if isinstance(d, np.ndarray):
        if d.shape == ():
            return "[]"
        if len(d) < 8:
            return "[" + (", ".join(dump_obj(o) for o in d)) + "]"
        else:
            return "[{} {} array]".format(d.shape, d.dtype)
    elif isinstance(d, list):
        d = np.asarray(d)
        if len(d) < 8:
            return "[" + (", ".join(dump_obj(o) for o in d)) + "]"
        else:
            return "[{} {} list]".format(len(d), d.dtype)
    elif isinstance(d, tuple):
        d = np.asarray(d)
        if len(d) < 8:
            return "(" + (", ".join(dump_obj(o) for o in d)) + ")"
        else:
            return "[{} {} tuple]".format(len(d), d.dtype)
    else:
        return str(d)


def dump_fdict_keys(d, k=None, depth=-1, file=sys.stdout):
    """
    """
    subprint = False
    if isinstance(d, collections.abc.Mapping):
        if k is not None:
            print("{}{}:".format("  " * depth, k), file=file)
        for subk, v in sorted(d.items()):
            dump_fdict_keys(v, subk, depth=depth + 1)
    elif isinstance(d, (np.ndarray, list, tuple)):
        d = np.asarray(d)
        if d.shape == ():
            return dump_fdict_keys(d.item(), k, depth, file=file)
        else:
            print("{}{}: {}".format("  " * depth, k, dump_obj(d)), file=file)
        if d.dtype == object and len(d) < 8:
            subprint = True
    else:
        print("{}{}: {}".format("  " * depth, k, str(d)), file=file)

    if subprint:
        for idx, v in enumerate(d):
            dump_fdict_keys(v, idx, depth=depth + 1)


def load_ls(d, file=sys.stdout):
    """
    Print the structure of the file similarly to the utilit "h5ls -r <fname>"
    """
    dump_fdict_keys(d, file=file)
