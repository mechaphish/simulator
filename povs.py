#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""PoV models."""

__author__ = "Kevin Borgolte <kevinbo@cs.ucsb.edu>"

from helpers import perfect


class PoV(object):
    def __init__(self, binary, service, kind, f_success=perfect):
        self.binary = binary        # Target binary
        self.service = service      # Target service
        self.kind = kind            # Type (1: pc control, 2: page read)
        self.f_success = f_success  # Probability of success (0 - 1)

    @property
    def successful(self):
        return self.f_success()
