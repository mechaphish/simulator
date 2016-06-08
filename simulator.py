#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

"""Simulate the CGC game."""

# pylint: disable=missing-docstring

__author__ = "Kevin Borgolte <kevinbo@cs.ucsb.edu>"
__version__ = "0.0.0"


# TODO:
# - How to model IDS?
#   PoVs might have 100% probabilty, but fail for a team because of IDS rules.


class Binary:
    file_size_overhead_threashold = 0.2
    execution_time_overhead_threashold = 0.05
    memory_usage_overhead_threashold = 0.05

    def __init__(self, name):
        self.name = name
        self.file_size_overhead = None


class Service:
    def __init__(self, name, binary):
        self.name = name
        self.binary = binary


class PoV:
    def __init__(self, service, kind):
        self.service = service  # Target service
        self.kind = kind        # Type (1: pc control, 2: page read)
        self.successful = 1     # Probability of success (0 - 1)


class Round:
    targets = dict()

    def __init__(self, round_, services):
        round_ = round_
        for service in services:
            self.targets[service.name] = list()

    def exploit_successful(self, exploit, team):
        self.targets[exploit.service].append(team.name)


class Team:
    def __init__(name, services):
        self.name = name
        self.services = services        # Fielded services
        self.povs = povs                # Active PoVs


class Game:
    tick = 0

    def __init__(self, teams, services):
        self.services = {name: Service(name, binary) for
                         name, binary in services.items()}
        self.teams = {name: Team(name, services) for name in teams}

    def run(self):
        """Simulate the game."""
        for team in teams.values():
            round_ = Round(tick, services)

            # Execute the current team PoVs against the relevant binaries of
            # other teams (Evaluation points).
            for pov in team.povs.values():

                # Only attack teams who have same binary fielded; a team might
                # have fielded a patched version for which the PoV does not
                # work.
                targets = (t for t in teams.values()
                           if t != team and
                           t.services[pov.service].binary == pov.binary)
                for target in targets:
                    if pov.run():
                        round_.pov_successful(pov, target)

            # TODO
            # Checks the availability of each service
            for service_name, service in team.services:
                pass

            # Check the security of each service by running any available PoV against it
            for attacking_team_name, attacking_team in teams.items()
                # Skip the attacking team
                if attacking_team_name == team_name:
                        continue
                # Check if the attacking team has one ore more PoVs for this service
                for service_name, service in team.services:
                        for exploit
        tick += 1
        return


def main(args):
    teams = ['Whiskey', 'Tango', 'Foxtrot']
    services = {'SFTP': 'sftp_0000',
                'HTTP': 'http_0000',
                'SMTP': 'smtp_0000'}
    game = Game(teams, services)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
