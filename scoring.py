#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Scoring models."""

from collections import namedtuple

__author__ = "Kevin Borgolte <kevinbo@cs.ucsb.edu>, Giovanni Vigna <vigna@cs.ucbs.edu>"


class Score(object):
    def __init__(self, service_name, functionality_factor, overhead, attack_performed, attack_received, num_teams):
        self.num_teams = num_teams
        self.service = service_name
        self.functionality_factor = functionality_factor
        self.overhead = overhead
        self.attack_performed = attack_performed
        self.attack_received = attack_received
        

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
    