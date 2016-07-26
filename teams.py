#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Team models."""

from __future__ import division

import random
import logging
from models import Binary, Service
from povs import PoV

__author__ = "Kevin Borgolte <kevinbo@cs.ucsb.edu>, Giovanni Vigna <vigna@cs.ucbs.edu>"


class Team(object):
    def __init__(self, name, services, type1_probability=0.0, type2_probability=0.0, patching_probability=0.0, povs=None):
        self.name = name
        self.services = services                        # Fielded services
        self._povs = povs if povs is not None else []   # Active PoVs
        
        self.type1_probability = type1_probability # Probability that a type1 POV is found for a binary
        self.type2_probability = type2_probability # Probability that a type2 POV is found for a binary
        self.patching_probability = patching_probability
        self.logger = logging.getLogger("team")
        
    @property
    def povs(self):
        return self._povs

    def generate_patch(self, service_name, round_num):
        service = self.services[service_name]
        
        # If the service has never been patched before, produce a patch with the specified vulnerability
        if not service.round_last_submit:
            if random.random() < self.patching_probability:
                
                bname, bversion = service.binary.name.split('_')
                new_bversion = int(bversion) + 1  
                binary_name = "%s_%04d" % (bname, new_bversion) 
                binary = Binary(binary_name)
                self.logger.debug("Team %s generates patch %s for service %s" % \
                                  (self.name, 
                                   binary_name, 
                                   service.name))
                service.field(binary, round_num)
                
                
    def generate_pov(self, service_name, round_num, teams):
        for team_name, team in teams.items():
            if team_name == self.name:
                continue
            service = team.services[service_name]
            self.logger.debug("Considering the service of team %s" % team_name)
            # Check if a PoV for this service/binary is available
            pov_found = False 
            for pov in self._povs:
                if pov.service.name == service.name and pov.binary.name == service.binary.name:
                    pov_found = True
                    break
            if not pov_found:
                if random.random() < max(self.type1_probability, self.type2_probability):
                    new_pov = PoV(service.binary, service, random.choice((1,2)))
                    self._povs.append(new_pov)
                    self.logger.debug("Team %s generates PoV for service %s and binary %s fielded by %s" % \
                                      (self.name, 
                                       service.name, 
                                       service.binary.name,
                                       team.name))
            else:
                self.logger.debug("PoV against service %s and binary %s already exists" % \
                                  (service.name,
                                   service.binary.name))
                        
    def __str__(self):
        
        s = "Team Name: %s Type1: %s Type2: %s Patching: %s\nServices:" % \
            (self.name,
             self.type1_probability,
             self.type2_probability,
             self.patching_probability)
            
        for service in self.services.values():
            s = "%s\n%s" % (s, str(service))
            
        for pov in self._povs:
            s = "%s\n%s" % (s, str(pov))
            
        return s
            
    
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
