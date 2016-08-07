#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Scoring models."""

from collections import namedtuple

__author__ = "Kevin Borgolte <kevinbo@cs.ucsb.edu>, Giovanni Vigna <vigna@cs.ucsb.edu>"


class Score(object):
    def __init__(self, service_name, 
                       functionality, 
                       overhead_time,
                       overhead_memory, 
                       overhead_size,
                       attack_performed, 
                       attack_received, 
                       num_teams):
        self.service = service_name
        self._functionality = functionality
        self.overhead_time = overhead_time
        self.overhead_memory = overhead_memory
        self.overhead_size = overhead_size
        self.attack_performed = attack_performed
        self.attack_received = attack_received
        self.num_teams = num_teams
        

    @property
    def total(self):
        """Score based on CFE scoring formula."""
        return self.availability * self.security * self.evaluation

    @property
    def availability(self):
        """Calculate the availability score, based on CFE scoring."""
        return min(self.performance, self.functionality)

    @property
    def performance(self):
        perf_factor = 1 + max(0.25 * self.overhead_size,
                              self.overhead_memory,
                              self.overhead_time)
        if 0 <= perf_factor < 1.05:
            return 1
        elif 1.05 <= perf_factor < 1.62:
            return (perf_factor - 1) ** (-4)
        elif 1.62 <= perf_factor < 2:
            return -0.493 * perf_factor + 0.986
        elif perf_factor >= 2:
            return 0

    @property
    def functionality(self):
        if self._functionality == 1:
            return 1
        elif 0.40 <= self._functionality < 1:
            return (2 - self._functionality) ** (-4)
        elif 0 < self._functionality < 0.40:
            return 0.381 * self._functionality
        elif self._functionality == 0:
            return 0

    #@property
    #def reference(self):
    #    """Based on CQE 1.2."""
    #    ratio = self.povs.reference_successful * 1. / self.povs.reference_total
    #    return 1 - ratio

    #@property
    #def consensus(self):
    #    """Based on CQE 1.2."""
    #    if self.povs.successful == 0:
    #        return 1
    #    else:
    #        return 0

    @property
    def security(self):
        #"""Based on CQE 1.2."""
        #if self.reference == 0:
        #    return 0
        #else:
        #    return 1 + 0.5 * (self.reference + self.consensus)
        if self.attack_received:
            return 1.0
        else:
            return 2.0
        
    @property
    def evaluation(self):
        #"""Based on CQE 1.3."""
        #if self.povs.successful == 0:
        #    return 1
        #else:
        #    return 2
        return 1.0 + float(self.attack_performed) / float(self.num_teams - 1.0)
    