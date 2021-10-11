# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals

import numpy as np
import scipy
import scipy.linalg
import scipy.signal

import declarative
from declarative.bunch import DeepBunch
from declarative.bunch.hdf_deep_bunch import HDFDeepBunch

from transient.rational.plots import (
    plot_fit,
    plot_ZP,
    plot_fitter_flag,
    plot_fitter_flag_compare,
    plot_ZP_grab
)

from transient.utilities.ipynb.displays import *

from transient.utilities.np import logspaced
from transient.utilities.mpl import (mplfigB, generate_stacked_plot_ax)

from transient.rational.fitters_ZPK import ZPKrep2MRF, MRF
from transient.rational.fitters_rational import RationalDiscFilter, ChebychevFilter 
from transient.rational.testing import testing_data

from transient.sysID import v1
from transient.sysID import v2


#run version printer from function to not further pollute namespace
def print_version():
    from .. import version_auto
    from .. import version
    print("transient version: {} (git:{})".format(version, version_auto.git_shorthash))
print_version()
del print_version
