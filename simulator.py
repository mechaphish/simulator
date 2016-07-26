#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Simulate the CGC game."""

from __future__ import print_function

from collections import defaultdict, namedtuple
import random
import sys
import optparse
import logging
import ConfigParser
import pprint
import numpy
import copy

from helpers import random_string
from models import Binary, Round, Service
from scoring import Score
from teams import Team, TeamPoVType1All, TeamPoVType1Half

# pylint: disable=missing-docstring,too-few-public-methods,too-many-arguments
# pylint: disable=fixme

__author__ = "Kevin Borgolte <kevinbo@cs.ucsb.edu>, Giovanni Vigna <vigna@cs.ucbs.edu>"

# TODO:
# - How will we model IDS? PoVs might have 100% probability, but fail for a team
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
        self.logger = logging.getLogger("simulation")
    
    def run(self, num_rounds=50, seed=None):
        """Simulate the game.

        For reproducibility, you can specify the seed for the random number
        generator.
        """
        random.seed(seed)
        
        rounds = list()
        for round_no in range(num_rounds):
            self.logger.debug("Starting round %d" % round_no)
            scores = {}

            round_ = Round(round_no)

            # Run PoVs of each team
            for team in self.teams.values():
                self.logger.debug("Executing the PoVs of team %s (%d)" % \
                                  (team.name,
                                   len(team.povs)))

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
                        self.logger.debug("Throwing PoV of type %d against team %s, service %s, binary %s" % \
                                          (pov.kind,
                                           target.name,
                                           pov.service.name,
                                           pov.service.binary.name))
                        if pov.successful:
                            self.logger.debug("PoV succeeded!")
                            round_.pov_successful(team, pov, target)
                        else:
                            self.logger.debug("PoV failed!")
                            
            # Total score per Team
            for team in self.teams.values():
                self.logger.debug("Evaluating scores for team %s" % team.name)
                for service in team.services.values():
                    self.logger.debug("Evaluating scores for service %s" % service.name)
                    
                    attacks_performed = round_.successful_attacks_performed(service.name, team.name)
                    attacks_received = round_.successful_attacks_received(service.name, team.name)
                    
                    self.logger.debug("Attacks performed: %d" % attacks_performed)
                    self.logger.debug("Attacks received: %d" % attacks_received)
                    #consensus = round_.successful[service.name].count(team.name)
                    #povcount = PoVCount(consensus,
                    #                    service.reference_povs_successful,
                    #                    service.reference_povs_total)

                    if service.is_fielded(round_no):
                        functionality = service.functionality
                    else:
                        functionality = 0
                    
                    overhead = service.overhead
                    
                    score = Score(service.name, functionality, overhead, attacks_performed, attacks_received, len(self.teams.values()))
                    round_.scores[team.name].append(score)
                    
                    self.logger.debug("Score %f: Availability: %f min(performance %f, functionality %f), Security: %f, Evaluation: %f" % \
                                      (score.total,
                                       score.availability, 
                                       score.performance,
                                       score.functionality,
                                       score.security,
                                       score.evaluation))
                #scores[team.name] = sum(s.total for s in
                #                        round_.scores[team.name])
            rounds.append(round_)
        
            # Team actions
            for team in self.teams.values():
                self.logger.debug("Determining behavior for team %s" % team.name)
                for service in team.services.values():
                    self.logger.debug("Determining behavior for service %s" % service.name)
                    team.generate_patch(service.name, round_no)
                    team.generate_pov(service.name, round_no, self.teams)
                self.logger.debug(str(team))
                    
        return rounds


def plot(rounds):
    """Plot the scores nicely.

    Expects an ordered list of rounds.
    """
    import matplotlib.pyplot as plt

    teams = defaultdict(list)

    plt.figure(figsize=(20,10))
    
    for round_ in rounds:
        for team, scores in round_.scores.items():
            total_round_score = 0
            for score in scores:
                total_round_score += score.total
            teams[team].append(total_round_score)
    
      
    for team, scores in teams.items():
        # transforms scores in cumulative format
        scores = numpy.cumsum(scores)
        plt.plot(range(len(rounds)), scores, label=team)

    legend = plt.legend(loc='upper left', fontsize='x-large')
    legend.get_frame().set_facecolor('#d9ccff')
    plt.ylabel("Points")
    plt.xlabel("Rounds")
    
    # TODO: add axis labels

    plt.show()


def main(args):     # pylint: disable=unused-argument,missing-docstring

    parser = optparse.OptionParser(usage="""
Usage: This script simulates a competition
""")
    
    parser.add_option("-d", "--debug",
                      dest="debug", action="store_true",
                      help="enables debugging",
                      default=False)
    parser.add_option("-c", "--config-file",
                      dest="config_file", type="string",
                      help="configuration file",
                      default="simulator.ini")
    
    (cmdline_options, args) = parser.parse_args()
    if len(args) != 0:
        parser.print_help()
        return 1
    
    if cmdline_options.debug == True:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger("simulator")
    logger.debug("Starting...")

    conf = ConfigParser.ConfigParser()
    try:
        conf.read(cmdline_options.config_file)
    except Exception, e:
        logger.error("Cannot access configuration file %s: %s" % (cmdline_options.config_file, str(e)))
        return 1
    
    num_services = int(conf.get('simulator', 'services'))
    services = dict()
    num_teams = int(conf.get('simulator', 'teams'))
    teams = dict()
    num_rounds = int(conf.get('simulator', 'rounds'))
    try:
        seed = int(conf.get('simulator', 'seed'))
    except:
        seed = 0x1337
    
    sections = conf.sections()
    
    # Creates the services
    for section in sections:
        if section.startswith('service-'):
            name = section[len('service-'):]
            services[name] = Service(name, Binary(name + "_0000"), 0)
            if len(services.values()) == num_services:
                break
            
    # Fill in the unspecified services
    for _ in range(len(services.values()), num_services):
        name = random_string(length=6).lower()
        services[name] = Service(name, Binary(name + "_0000"), 0)
        
    for section in sections:
        if section.startswith('team-'):
            name = section[len('team-'):]
            try:
                team_type = conf.get(section, 'type')
            except:
                team_type = 'default'
            try: 
                type1_probability = conf.get(section, 'type1_probability')
            except:
                type1_probability = 0
            try: 
                type2_probability = conf.get(section, 'type2_probability')
            except:
                type2_probability = 0
            try: 
                patching_probability = conf.get(section, 'patching_probability')
            except:
                patching_probability = 0
            
            # Creates a deep copy of the services
            team_services = dict()
            for service in services.values():
                team_services[service.name] = Service(service.name, Binary(service.binary.name), 0)
                
            if team_type == 'pov_type_1_half':
                teams[name] = TeamPoVType1Half(name, team_services)
            elif team_type == 'pov_type_1_all':
                teams[name] = TeamPoVType1All(name, team_services)
            else:
                teams[name] = Team(name, 
                                   team_services, 
                                   type1_probability=type1_probability, 
                                   type2_probability=type2_probability, 
                                   patching_probability=patching_probability)
            if len(teams.values()) == num_teams:
                break
            
    # Fill in the unspecified teams
    for _ in range(len(teams.keys()), num_teams):
        name = "TEAM-" + random_string(length=4)
        teams[name] = Team(name, services)

    for team in teams.values():
        logger.debug(str(team))
    
    simulation = Simulation(services, teams)
    rounds = simulation.run(num_rounds=num_rounds, seed=seed)

    #for scores in rounds:
    #    print(scores)

    plot(rounds)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
