#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Various helpers."""

from __future__ import division

import random
import string

__author__ = "Kevin Borgolte <kevinbo@cs.ucsb.edu>, Giovanni Vigna <vigna@cs.ucbs.edu>"

# ======
# Strings
def random_string(length=4, alphabet=string.ascii_uppercase):
    return "".join(random.choice(alphabet) for _ in range(length))


# ===================
# Probability Helpers
def perfect():
    return 1

def very_good():
    attempt = random.random()
    if attempt > 0.2:
        return 1
    return 0

def good():
    attempt = random.random()
    if attempt > 0.5:
        return 1
    return 0

def bad():
    attempt = random.random()
    if attempt > 0.8:
        return 1
    return 0

def no_overhead():
    return 0.0


# ===========
# PoV Helpers
def always_all(total):
    return total


def atmost_80pct(total):
    return random.randint(0, total * 8 // 10)
