#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © 2021 Massachusetts Institute of Technology.
# SPDX-FileCopyrightText: © 2021 Lee McCuller <mcculler@mit.edu>
# NOTICE: authors should document their contributions in concisely in NOTICE
# with details inline in source files, comments, and docstrings.
"""
"""
import sys
import time
import logging
import contextlib

from ..utilities.strings import padding_remove


class HintAid(object):
    def __init__(
        self,
        hints=None,
        hints_seen=None,
        active=True,
    ):
        self.mtime_start = time.time()

        if hints is None:
            hints = dict()

        if isinstance(hints, (list, tuple)):
            usehints = dict()
            for hdict in hints:
                usehints.update(hdict)
        else:
            usehints = dict(hints)

        self.hints = usehints
        self.hints_seen = hints_seen

        # holds a heading for the logging, as well as sets tabbing
        self.log_header_stack = ()
        # indicates how far into the header has been printed yet.
        # for the live log
        self.log_header_printed = 0

        # log entries
        self._logs = []
        self.log_number = 0
        return

    # def hint_set(self, hname, hval, default = False):
    #    if default:
    #        self.hints.setdefault(hname, hval)
    #    else:
    #        self.hints[hname] = hval
    #    return

    def hint_has(self, hname):
        return hname in self.hints

    def hint_setdefault(self, hname, hval):
        self.hints.setdefault(hname, hval)
        return

    def hint_arg(self, func_arg, *args, **kwargs):
        if func_arg is None:
            return self.hint(*args, **kwargs)
        else:
            return func_arg

    def hint(self, *args, **kwargs):
        superarg = []
        for arg in args:
            if isinstance(arg, (list, tuple)):
                superarg.extend(arg)
            else:
                superarg.append(arg)

        # helper for when the known keys are being indexed
        if self.hints_seen is not None:
            keys_remapped = [key.format(**kwargs) for key in superarg]
            for idx, key in enumerate(keys_remapped):
                overrides, relateds = self.hints_seen.setdefault(key, (set(), set()))
                relateds.update(keys_remapped[:idx])
                overrides.update(keys_remapped[idx + 1 :])

        for key in superarg:
            key = key.format(**kwargs)
            ret = self.hints.get(key, NOARG)
            if ret is not NOARG:
                return ret
        return kwargs["default"]

    def log(self, *args, **kwargs):
        """
        First argument is the level, should include a log group, which must be one of
        ['info', 'debug', 'warn', 'alert', 'rationale', 'progress']
        """
        level = args[0]
        if isinstance(level, int):
            level = args[0]
            args = args[1:]
            group = kwargs.setdefault("group", "info")
        else:
            level = -1
            group = kwargs.setdefault("group", "debug")
            # TODO print line and file upon hint request
            # args = args

        header = self.log_header_stack
        kwargs["header"] = header
        kwargs["time"] = time.time()
        kwargs["time_start"] = self.mtime_start

        if self.hint("log_off", default=False):
            return

        kwargs["args"] = args
        # TODO, merge if consecutive with the same parameters
        self._logs.append(kwargs)
        self.log_number += 1

        # FOR LIVE PRINTING
        if group == "info":
            log_mod_level = logging.INFO
            group_character = "I"
            level_limit = self.hint(
                [
                    "log_level_info",
                    "log_level",
                ],
                default=8,
            )
        elif group == "debug":
            log_mod_level = logging.DEBUG
            group_character = "D"
            level_limit = self.hint(
                [
                    "log_level_debug",
                    "log_level",
                ],
                default=8,
            )
        elif group == "warn":
            log_mod_level = logging.WARNING
            group_character = "W"
            level_limit = self.hint(
                [
                    "log_level_warn",
                    "log_level",
                ],
                default=8,
            )
        elif group == "alert":
            log_mod_level = logging.WARNING
            group_character = "A"
            level_limit = self.hint(
                [
                    "log_level_alert",
                    "log_level",
                ],
                default=8,
            )
        elif group == "rationale":
            log_mod_level = logging.INFO
            group_character = "R"
            level_limit = self.hint(
                [
                    "log_level_rationale",
                    "log_level",
                ],
                default=8,
            )
        elif group == "progress":
            log_mod_level = logging.INFO
            group_character = "P"
            level_limit = self.hint(
                [
                    "log_level_progress",
                    "log_level",
                ],
                default=8,
            )
        else:
            raise RuntimeError("Unrecognized log grouping")

        if self.hint("log_print", default=True) and level <= level_limit:
            hint_log_stdout = self.hint("log_stdout", default=True)
            if hint_log_stdout not in [None, True, False]:
                lfile = hint_log_stdout
            else:
                lfile = sys.stdout

            header = self.log_header_stack
            header_len = len(header)

            prefix = "{}{} {: >6.2f} {}".format(
                level if level >= 0 else "-",
                group_character,
                kwargs["time"] - kwargs["time_start"],
                "  " * header_len,
            )

            # TODO, make these take a header argument
            if not self.hint("logging_use", default=False):

                def pfunc(*args, **kwargs):
                    print(*args, **kwargs)

            else:

                def pfunc(*args, **kwargs):
                    kwargs.pop("file", None)
                    logging.log(log_mod_level + 9 - level, *args, **kwargs)

            if header_len > self.log_header_printed:
                pfunc(
                    "{}:{}:".format("-" * (len(prefix)), ":".join(header)), file=lfile
                )
                self.log_header_printed = header_len
                # tag that the header has been printed

            hint_log_stderr = self.hint("log_stderr", default=True)
            if hint_log_stderr and group == "warn":
                if hint_log_stderr not in [None, True, False]:
                    lfile = hint_log_stderr
                else:
                    lfile = sys.stderr
            else:
                lfile = sys.stdout

            arg_lines = [[]]
            for arg in args:
                if isinstance(arg, str):
                    if "\n" in arg:
                        arg = padding_remove(arg)
                    arg_spl = arg.split("\n")
                    arg_lines[-1].append(arg_spl[0])
                    for subline in arg_spl[1:]:
                        arg_lines.append([subline])
                else:
                    arg_lines[-1].append(arg)

            # TODO, have pfunc do this splitting
            pfunc(prefix, *arg_lines[0], file=lfile)
            for argsl in arg_lines[1:]:
                pfunc(" " * len(prefix), *argsl, file=lfile)
        return

    def log_debug(self, *args, **kwargs):
        kwargs["group"] = "debug"
        self.log(*args, **kwargs)

    def log_warn(self, *args, **kwargs):
        kwargs["group"] = "warn"
        self.log(*args, **kwargs)

    def log_alert(self, *args, **kwargs):
        kwargs["group"] = "alert"
        self.log(*args, **kwargs)

    def log_info(self, *args, **kwargs):
        kwargs["group"] = "info"
        self.log(*args, **kwargs)

    def log_rationale(self, *args, **kwargs):
        kwargs["group"] = "rationale"
        self.log(*args, **kwargs)

    def log_progress(self, *args, **kwargs):
        kwargs["group"] = "progress"
        self.log(*args, **kwargs)

    @contextlib.contextmanager
    def log_heading(self, header):
        save_stack = self.log_header_stack
        self.log_header_stack = save_stack + (header,)
        # TODO, auto print header on command?
        yield
        self.log_header_stack = save_stack
        if self.log_header_printed > len(save_stack):
            self.log_header_printed = len(save_stack)


# unique element to indicate a default argument
_NOARG = lambda: _NOARG
NOARG = ("NOARG", _NOARG)
