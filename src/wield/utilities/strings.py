#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © 2021 Massachusetts Institute of Technology.
# SPDX-FileCopyrightText: © 2021 Lee McCuller <mcculler@caltech.edu>
# NOTICE: authors should document their contributions in concisely in NOTICE
# with details inline in source files, comments, and docstrings.
"""
"""
import re
import string
import numpy as np
import textwrap


_re_any_words = re.compile(r"\s*\S+")
_re_leading_space = re.compile(r"\s*")


def padding_remove(docstring_like, tabsize=4):
    """
    Both removes the leading line paddings on triple quoted strings and removes common indentation
    (expands tabs to do so)
    """
    docstring_like = docstring_like.strip()
    docstring_like = docstring_like.expandtabs(tabsize)
    docstring_lines = docstring_like.splitlines(True)

    spacings = []
    for line in docstring_lines[1:]:
        if len(line.strip()) == 0:
            continue
        spacings.append(len(_re_leading_space.match(line).group(0)))
    if spacings:
        common_spacing = min(spacings)
    else:
        common_spacing = 0
    common_tab_spacing = (common_spacing // tabsize) * tabsize

    if docstring_lines:
        fixed_lines = [docstring_lines[0]]
        for line in docstring_lines[1:]:
            fixed_lines.append(line[common_tab_spacing:])
    else:
        fixed_lines = []

    return "".join(fixed_lines)


def transform(v):
    if isinstance(v, complex):
        if v.imag >= 0:
            return "{0:.3f}+{1:.3f}i".format(v.real, v.imag)
        else:
            return "{0:.3f}-{1:.3f}i".format(v.real, -v.imag)
    else:
        return v


def table(
    table,
    headers,
    labels=None,
    diag=None,
    headers_modify=None,
    transform=transform,
    minwidth=12,
    **kwargs
):
    import tabulate

    if headers_modify == "split":
        headers = ((["/\n".join(h.split("/")).strip() for h in headers]),)
    elif headers_modify == "bind":
        labels2 = []
        headers2 = []
        for n, (l, h) in enumerate(zip(labels, headers)):
            assert l == h
            labels2.append("({}) {}".format(string.ascii_uppercase[n], l))
            headers2.append("({})".format(string.ascii_uppercase[n]))
        labels = labels2
        headers = headers2

    rows = []
    if diag is not None:
        headers = [diag] + list(headers)
    if labels is not None:
        for label, row in zip(labels, table):
            exrow = [label]
            exrow.extend(transform(v) for v in row)
            rows.append(exrow)
    else:
        for row in table:
            exrow = []
            exrow.extend(transform(v) for v in row)
            rows.append(exrow)

    if minwidth is not None and rows:
        arr_table = np.array(rows, dtype=object)[:, -len(headers) :]
        widths = []
        for idx in range(arr_table.shape[1]):
            s = tabulate.tabulate(arr_table[:, idx].reshape(-1, 1), **kwargs)
            w = len(s.split("\n")[0])
            widths.append(w)

        headers2 = []
        for w, header in zip(widths, headers):
            if w < minwidth:
                w = minwidth
            headers2.append("\n".join(textwrap.wrap(header, width=w)))
    else:
        headers2 = headers

    return tabulate.tabulate(rows, headers=headers2, **kwargs)
