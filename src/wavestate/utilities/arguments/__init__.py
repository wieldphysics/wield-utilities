# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import declarative

from .base import (
    ArgumentError,
    grab_kwargs,
    grab_kwarg_hints,
    check_remaining_arguments,
    transfer_kw,
)

from .pyargparse import (
    kwdict_argparse,
)

from .aid import HintAid

from . import logging

kw_hints = declarative.Bunch()
#kw_hints.update(logging.kw_hints)

__all__ = [
    kwdict_argparse,
    HintAid,
    ArgumentError,
    grab_kwargs,
    grab_kwarg_hints,
    kw_hints,
    logging,
]
