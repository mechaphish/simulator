#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Base models.

Base models shall not be modified. If they are being modified or inherited,
please move them to their own module, similar to teams or povs.
"""

from collections import defaultdict, namedtuple

from helpers import atmost_80pct, no_overhead, perfect

__author__ = "Kevin Borgolte <kevinbo@cs.ucsb.edu>"


class Binary(object):
    """Binary model.

    A binary models the overhead and functionality of a replacement
    challenge set. It expects functions that return 0..inf for overhead
    and 0..1 for the functionality factor.
    """

    def __init__(self, name, f_execution_time_overhead=no_overhead,
                 f_file_size_overhead=no_overhead,
                 f_memory_usage_overhead=no_overhead,
                 f_functionality_factor=perfect):
        self.name = name
        self.f_execution_time_overhead = f_execution_time_overhead
        self.f_memory_usage_overhead = f_memory_usage_overhead
        self.f_file_size_overhead = f_file_size_overhead
        self.f_functionality_factor = f_functionality_factor


Overhead = namedtuple('Overhead', ['execution_time', 'file_size',
                                   'memory_usage'])


class Service(object):
    """Service model.

    A service models whether a service is active, which binary a team has
    deployed, when it was last deployed, how many reference PoVs for the
    service exist, and whether they were successful.
    """
    def __init__(self, name, binary, round_,
                 f_reference_povs_successful=atmost_80pct,
                 reference_povs_total=4):
        self.name = name
        self.binary = binary
        self.round_introduced = round_
        self.round_last_submit = None
        self.f_reference_povs_successful = f_reference_povs_successful
        self.reference_povs_total = reference_povs_total

    def field(self, binary, round_):
        self.round_last_submit = round_
        self.binary = binary

    def is_fielded(self, round_):
        """Check if the service is fielded yet.

        Per A157: A service is fielded at n+2 if the RCB was submitted in n.
        Per A163: A RCB for newly introduced challenge set is fielded at n+3.
        """
        if self.round_last_submit is None:
            # Per A163, the binary is a newly introduced RCB
            return round_ >= (self.round_introduced)
        else:
            return round_ > (1 + max(self.round_last_submit,        # A157
                                     self.round_introduced + 1))    # A163

    @property
    def functionality(self):
        return self.binary.f_functionality_factor()

    @property
    def overhead(self):
        return Overhead(self.binary.f_execution_time_overhead(),
                        self.binary.f_file_size_overhead(),
                        self.binary.f_memory_usage_overhead())

    @property
    def reference_povs_successful(self):
        """Return a number between 0 and self.reference_povs_total."""
        return self.f_reference_povs_successful(self.reference_povs_total)


class Round(object):
    """Round model.

    A round models the successful PoVs per service per team and the scores that
    were assigned to each team in this specific round.
    """
    def __init__(self, round_):
        round_ = round_
        self.successful = defaultdict(list)
        self.scores = defaultdict(list)

    def pov_successful(self, pov, team):
        self.successful[pov.service.name].append(team.name)
