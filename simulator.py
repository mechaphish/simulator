#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Simulate the CGC game."""

import random
import sys

from collections import defaultdict, namedtuple

# pylint: disable=missing-docstring,too-few-public-methods,too-many-arguments
# pylint: disable=fixme

__author__ = "Kevin Borgolte <kevinbo@cs.ucsb.edu>"
__version__ = "0.0.0"


# TODO: How will we model IDS? PoVs might have 100% probabilty, but fail for a
#       team because of IDS rules.


# ===================
# Probability Helpers
def perfect():
    return 1.


# ===========
# PoV Helpers
def always_all(total):
    return total


# =======
# Scoring Functions
Overhead = namedtuple('Overhead', ['execution_time', 'file_size',
                                   'memory_usage'])
PoVCount = namedtuple('PoVCount', ['successful', 'reference_successful',
                                   'reference_total'])


class Score(object):
    def __init__(self, functionality_factor, overhead, povs):
        self.functionality_factor = functionality_factor
        self.overhead = overhead
        self.povs = povs

    @property
    def total(self):
        """Score based on CQE scoring formula."""
        return self.availability * self.security * self.evaluation

    @property
    def availability(self):
        """Calculate the availability score, based on CQE scoring."""
        return min(self.performance, self.functionality)

    @property
    def performance(self):
        perf_factor = 1 + max(0.25 * self.overhead.file_size,
                              self.overhead.memory_usage,
                              self.overhead.execution_time)
        if 0 <= perf_factor < 1.10:
            return 1
        elif 1.10 <= perf_factor < 1.62:
            return (perf_factor - 1) ** (-4)
        elif 1.62 <= perf_factor < 2:
            return -0.493 * perf_factor + 0.986
        elif perf_factor >= 2:
            return 0

    @property
    def functionality(self):
        if self.functionality_factor == 1:
            return 1
        elif 0.40 <= self.functionality_factor < 1:
            return (2 - self.functionality_factor) ** (-4)
        elif 0 < self.functionality_factor < 0.40:
            return 0.381 * self.functionality_factor
        elif self.functionality_factor == 0:
            return 0

    @property
    def reference(self):
        """Based on CQE 1.2."""
        ratio = self.povs.reference_successful * 1. / self.povs.reference_total
        return 1 - ratio

    @property
    def consensus(self):
        """Based on CQE 1.2."""
        if self.povs.successful == 0:
            return 1
        else:
            return 0

    @property
    def security(self):
        """Based on CQE 1.2."""
        if self.reference == 0:
            return 0
        else:
            return 1 + 0.5 * (self.reference + self.consensus)

    @property
    def evaluation(self):
        """Based on CQE 1.3."""
        if self.povs.successful == 0:
            return 1
        else:
            return 2


# ======
# Models
class Binary(object):
    def __init__(self, name, f_execution_time_overhead=perfect,
                 f_file_size_overhead=perfect,
                 f_memory_usage_overhead=perfect,
                 f_functionality_factor=perfect):
        """Binary model.

        A binary models the overhead and functionality of a replacement
        challenge set. It expects functions that return 0..inf for overhead
        and 0..1 for the functionality factor.
        """
        self.name = name
        self.f_execution_time_overhead = f_execution_time_overhead
        self.f_memory_usage_overhead = f_memory_usage_overhead
        self.f_file_size_overhead = f_file_size_overhead
        self.f_functionality_factor = f_functionality_factor


class Service(object):
    def __init__(self, name, binary, round_,
                 f_reference_povs_successful=always_all,
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


class PoV(object):
    def __init__(self, service, kind, f_success=perfect):
        self.service = service       # Target service
        self.kind = kind             # Type (1: pc control, 2: page read)
        self.f_success = f_success   # Probability of success (0 - 1)

    @property
    def successful(self):
        return self.f_success()


class Round(object):
    def __init__(self, round_):
        round_ = round_
        self.successful = defaultdict(list)
        self.scores = defaultdict(list)

    def pov_successful(self, pov, team):
        self.successful[pov.service.name].append(team.name)


class Team(object):
    def __init__(self, name, services, povs=None):
        self.name = name
        self.services = services                        # Fielded services
        self.povs = povs if povs is not None else []    # Active PoVs


class Simulation(object):
    def __init__(self, teams, services):
        """Create a Simulation."""
        # TODO: Services and povs should be moved outside of this constructor to
        #       be more flexible. In fact, instantiated beforehand based on
        #       probability functions, like "PerfectTeam" etc.
        self.services = {name: Service(name, binary, 0) for
                         name, binary in services.items()}
        self.teams = {name: Team(name, self.services) for name in teams}

    def run(self, rounds=50, seed=None):
        """Simulate the game.

        For reproducibility, you can specify the seed for the random number
        generator.
        """
        random.seed(seed)
        for round_no in range(rounds):
            scores = {}

            # Run PoVs
            for team in self.teams.values():
                round_ = Round(round_no)

                # Execute the current team PoVs against the relevant binaries
                # of other teams (Evaluation points).
                for pov in team.povs.values():
                    # Only attack teams who have same binary fielded; a team
                    # might have fielded a patched version for which the PoV
                    # does not work.
                    targets = (t for t in self.teams.values()
                               if t != team and
                               t.services[pov.service].binary == pov.binary and
                               t.services[pov.service].is_fielded(round_no))
                    for target in targets:
                        if pov.run():
                            round_.pov_successful(pov, target)

            # Total Score per Team
            for team in self.teams.values():
                for service in team.services.values():
                    consensus = round_.successful[service.name].count(team.name)
                    povcount = PoVCount(consensus,
                                        service.reference_povs_successful,
                                        service.reference_povs)

                    if service.is_fielded(round_no):
                        functionality = service.functionality
                    else:
                        functionality = 0

                    score = Score(povcount, service.overhead, functionality)
                    round_.scores[team.name].append(score)

                scores[team.name] = sum(s.total for s in
                                        round_.scores[team.name])

            yield scores


def main(args):     # pylint: disable=unused-argument
    teams = ['Whiskey', 'Tango', 'Foxtrot']
    services = {'SFTP': 'sftp_0000',
                'HTTP': 'http_0000',
                'SMTP': 'smtp_0000'}
    simulation = Simulation(teams, services)
    for scores in simulation.run(seed=0x1337):
        print(scores)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
