#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Simulate the CGC game."""

from __future__ import print_function

from collections import defaultdict, namedtuple
import random
import sys

from helpers import random_string
from models import Binary, Round, Service
from scoring import Score
from teams import Team, TeamPoVType1All, TeamPoVType1Half

# pylint: disable=missing-docstring,too-few-public-methods,too-many-arguments
# pylint: disable=fixme

__author__ = "Kevin Borgolte <kevinbo@cs.ucsb.edu>"


# TODO:
# - How will we model IDS? PoVs might have 100% probabilty, but fail for a team
#   because of IDS rules.
# - Remove redundancy in Team/Service name mapping.

PoVCount = namedtuple('PoVCount', ['successful', 'reference_successful',
                                   'reference_total'])


class Simulation(object):
    def __init__(self, services, teams):
        """Create a Simulation."""
        # TODO: Services and povs should be moved outside of this constructor to
        #       be more flexible. In fact, instantiated beforehand based on
        #       probability functions, like "PerfectTeam" etc.
        self.services = services
        self.teams = teams

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
                for pov in team.povs:
                    # Only attack teams who have same binary fielded; a team
                    # might have fielded a patched version for which the PoV
                    # does not work.
                    targets = (t for t in self.teams.values()
                               if t != team and
                               t.services[pov.service.name].binary == pov.binary and
                               t.services[pov.service.name].is_fielded(round_no))
                    for target in targets:
                        if pov.successful:
                            round_.pov_successful(pov, target)

            # Total Score per Team
            for team in self.teams.values():
                for service in team.services.values():
                    consensus = round_.successful[service.name].count(team.name)
                    povcount = PoVCount(consensus,
                                        service.reference_povs_successful,
                                        service.reference_povs_total)

                    if service.is_fielded(round_no):
                        functionality = service.functionality
                    else:
                        functionality = 0

                    score = Score(functionality, service.overhead, povcount)
                    round_.scores[team.name].append(score)

                scores[team.name] = sum(s.total for s in
                                        round_.scores[team.name])

            yield scores


def plot(round_scores):
    """Plot the scores nicely.

    Expects an ordered list of scores per round, which should be maps from team
    to the team's score for this round.
    """
    import matplotlib.pyplot as plt

    teams = defaultdict(list)

    for round_score in round_scores:
        for team, score in round_score.items():
            teams[team].append(score)

    for team, scores in teams.items():
        plt.plot(range(len(round_scores)), scores, label=team)

    legend = plt.legend(loc='upper left', fontsize='x-large')
    legend.get_frame().set_facecolor('#d9ccff')

    # TODO: add axis labels

    plt.show()


def main(args):     # pylint: disable=unused-argument,missing-docstring
    services_raw = {n: n.lower() + "_0000"              # 30 random services
                    for n in random_string(length=4)
                    for _ in range(50)}
    services = {name: Service(name, Binary(binary), 0)
                for name, binary in services_raw.items()}
    teams = {'Whiskey': Team('Whiskey', services),
             'Tango': TeamPoVType1All('Tango', services),
             'Foxtrot': TeamPoVType1Half('Foxtrot', services)}
    simulation = Simulation(services, teams)
    rounds = list(simulation.run(seed=0x1337))

    for scores in rounds:
        print(scores)

    plot(rounds)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
