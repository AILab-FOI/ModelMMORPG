#!/usr/bin/env python
#-*- coding: utf-8 -*-

from spade.Agent import BDIAgent
from spade.Behaviour import OneShotBehaviour, EventBehaviour, ACLTemplate, MessageTemplate
from spade.ACLMessage import ACLMessage
from spade.AID import aid
from spade.SWIKB import SWIKB as KB

Overflow = 0.00

'''
TODO: 

Reimplement agents and their behaviours as in SSSHS, but add organizational units, see:
https://github.com/javipalanca/spade/blob/master/spade/Organization.py
https://github.com/javipalanca/spade/blob/master/spade/Organization_new.py

Implement communication via messaging.

Store data about agents state in knowledge base.
'''

class Report( OneShotBehaviour ):
	''' Reporting behaviour to be added on the fly at the end of simulation with addBehaviour() '''
	def _process( self ):
		''' Print out the stats of all storages '''
		''' TODO: Would be nice to produce some visualization on this '''
		with self.myAgent:
			totalInterventions = economyRequests + delayRequests + restoreEconomyRequests + advanceRequests + giveRequests + negotiationRequests

			global Overflow
			for s in storages:
				Overflow += s.ResourceLoss

			say( ".... [ END OF SIMULATION ] ...." )
			say( "******* Number of system interventions: %d" % totalInterventions )
			say( "*********** First intervention happened at time: %d" % firstIntervention )

			say( "******* Number of LT ALERTS: %d" % LTalerts )
			say( "*********** Number of DELAY  requests: %d" % delayRequests )
			say( "*********** Number of ECONOMY requests: %d" % economyRequests )
			say( "*********** Number of NEGOTIATION requests: %d" % negotiationRequests )

			say( "******* Number of UT ALERTS: %d" % UTalerts )
			say( "*********** Number of RESTORE requests: %d" % restoreEconomyRequests )
			say( "*********** Number of ADVANCE requests: %d" % advanceRequests )
			say( "*********** Number of GIVE requests: %d" % giveRequests )
			say( "*********** Overflow of resources: %f" % Overflow )

			for s in storages:
				say( "INDIVIDUAL REPORT FOR STORAGE %s" % s.name )
				say( "- Capacity: %d" % s.maxCapacity )
				say( "- CRL: %d" % s.currentResourceLevel )
				say( "- UT alerts: %d" % s.myUTalerts )
				say( "- Advance reqs: %d" % s.myAdvanceReqs )
				say( "- Resources lost: %f" % s.ResourceLoss )
				say( "- LT alerts: %d" % s.myLTalerts )
				say( "- Economy reqs: %d" % s.myEconomyReqs )
				say( "- Delay reqs: %d" % s.myDelayReqs )
				say( "CRL HISTORY: %s" % s.CRLhistory )
				say( "OVERFLOW per time unit: %s" % s.overflowHistory )


class TalkingAgent( BDIAgent ):
	''' Agent that prints to the console
	Abstract - only to be inherited by other agent classes	
	'''
	def say( self, msg ):
		''' Say something (e.g. print to console for debug purposes) '''
		print '%s: %s' % ( self.name.split( '@' )[ 0 ], str( msg ) )

class Observer( TalkingAgent ):
	''' Observer agent -- collects statstical data about all other agents '''
	def _setup( self ):
		''' Setup the agent's knowledge base '''
		self.kb = KB()

		self.report = Report()

class Storage( TalkingAgent ):
	''' A storage in a settlement '''
	def _setup( self ):
		pass

class Consumer( TalkingAgent ):
	''' A consumer in a settlement '''
	def _setup( self ):
		pass

class Producer( TalkingAgent ):
	''' A producer in a settlement '''
	def _setup( self ):
		pass

if __name__ == '__main__':
	''' Add simulation configuration here (e.g. number of agents, organizational units, hierarchy'''
	pass

