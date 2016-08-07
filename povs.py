#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""PoV models."""

__author__ = "Kevin Borgolte <kevinbo@cs.ucsb.edu>, Giovanni Vigna <vigna@cs.ucsb.edu>"

from helpers import perfect
import random

class PoV(object):
    def __init__(self, binary, service, kind):
        self.binary = binary        # Target binary
        self.service = service      # Target service
        self.kind = kind            # Type (1: pc control, 2: page read)
        

    def successful(self, target):
        protection = target.services[self.service.name].binary.protection
        r = random.random()
        if r > protection:
            return 1
        else:
            return 0

        
    def __str__(self):
        s = "PoV Service: %s Binary: %s Kind: %d" % \
            (self.service.name,
             self.binary.name,
             self.kind)
        return s