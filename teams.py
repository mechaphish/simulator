#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Team models."""

from __future__ import division

import random

from povs import PoV

__author__ = "Kevin Borgolte <kevinbo@cs.ucsb.edu>"


class Team(object):
    def __init__(self, name, services, povs=None):
        self.name = name
        self.services = services                        # Fielded services
        self._povs = povs if povs is not None else []   # Active PoVs

    @property
    def povs(self):
        return self._povs


class TeamPoVType1All(Team):
    @property
    def povs(self):
        # FIXME: Currently, the team is pwning only its own services. This is
        # okay because it is not patching them yet, if it would be, then it
        # needs to attack the specific binary.
        return [PoV(s.binary, s, 1) for s in self.services.values()]


class TeamPoVType1Half(Team):
    @property
    def povs(self):
        # FIXME: Currently, the team is pwning only its own services. This is
        # okay because it is not patching them yet, if it would be, then it
        # needs to attack the specific binary.
        povs = [PoV(s.binary, s, 1) for s in self.services.values()]
        return random.sample(povs, len(povs) // 2)
