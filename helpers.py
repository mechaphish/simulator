#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Various helpers."""

from __future__ import division

import random
import string

__author__ = "Kevin Borgolte <kevinbo@cs.ucsb.edu>"

# ======
# Strings
def random_string(length=4, alphabet=string.ascii_uppercase):
    return "".join(random.choice(alphabet) for _ in range(length))


# ===================
# Probability Helpers
def perfect():
    return 1.


def no_overhead():
    return 0.


# ===========
# PoV Helpers
def always_all(total):
    return total


def atmost_80pct(total):
    return random.randint(0, total * 8 // 10)
