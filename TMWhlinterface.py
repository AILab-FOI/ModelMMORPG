#!/usr/bin/env python
#-*- coding: utf-8 -*-

import spade
from spade.SWIKB import SWIKB as KB
import llinterface as lli
import time
import TMWbehavs
from random import random, randint, choice
from os.path import isfile, join

class Role:
	''' An (organizational) role is basically a set of behaviours.
            The behaviours should be a list of elements having the form: ( behaviour instance, template instance ).
	    The second item only applies to EventBehaviours (template), else it is None'''
	def __init__( self, behaviours=[] ):
		self.behaviours = behaviours

class ChangeRole( spade.Behaviour.OneShotBehaviour ):
	"""Behaviour to change the Role of the Agent. The Agent will acquire behaviours of the needed Role."""
	def __init__( self, role, *args, **kwargs ):
		spade.Behaviour.OneShotBehaviour.__init__( self, *args, **kwargs )
		self.role = role

	def _process( self ):
		for behaviour, template in self.role.behaviours:
			self.myAgent.addBehaviour( behaviour, template )

class Leader( Role ):
	class LeaderBehaviour( spade.Behaviour.OneShotBehaviour ):
		def _process( self ):
			self.myAgent.say( 'I am a leader!' )
			query = "assert( waiting_quest( 'party_time', '%s', leadership ) )" % self.myAgent.avatar_name
			self.myAgent.kb.ask( query )

	class InvitePlayers( spade.Behaviour.PeriodicBehaviour ):
		def _onTick( self ):
			''' if the quest of inviting people isn't waiting, put it into waiting again '''
			query = "waiting_quest( 'party_time', '%s', invite_player )" % self.myAgent.avatar_name
			result = self.myAgent.kb.ask( query )
			if not result:
				query = query = "retractall( waiting_quest( 'party_time', '%s', invite_player ) )" % self.myAgent.avatar_name
				self.myAgent.kb.ask( query )
				self.myAgent.say( 'Need to invite more people!' )
				query = "assert( waiting_quest( 'party_time', '%s', invite_player ) )" % self.myAgent.avatar_name
				self.myAgent.kb.ask( query )

	def __init__( self ):
		lb = self.LeaderBehaviour()
		ipb = self.InvitePlayers( 30 ) # check every 30 seconds
		self.behaviours = [ ( lb, None ), ( ipb, None ) ]

class ExtremistFollower( Role ):
	class ExtremistFollowerBehaviour( spade.Behaviour.OneShotBehaviour ):
		def _process( self ):
			self.myAgent.say( 'I am an extremist follower!' )
			query = "assert( waiting_quest( 'party_time', '%s', extremist_follower ) )" % self.myAgent.avatar_name
			self.myAgent.kb.ask( query )

	def __init__( self ):
		efb = self.ExtremistFollowerBehaviour()
		self.behaviours = [ ( efb, None ) ]

class Opportunist( Role ):
	class OpportunistBehaviour( spade.Behaviour.OneShotBehaviour ):
		def _process( self ):
			self.myAgent.say( 'I am an opportunist!' )
			query = "assert( waiting_quest( 'party_time', '%s', opportunist ) )" % self.myAgent.avatar_name
			self.myAgent.kb.ask( query )

	def __init__( self ):
		ob = self.OpportunistBehaviour()
		self.behaviours = [ ( ob, None ) ]

class ManaWorldPlayer( spade.Agent.BDIAgent, lli.Connection ):
	def getMyLocation( self ):
		''' Get player location
			Returns tuple ( mapID, X, Y ) '''
		if not hasattr( self, 'location' ):
			self.location = None
		try:
			self.locatePlayer()
			time.sleep( 0.5 )
			if self.location == ( self.pb.playerMap, self.pb.playerPosX, self.pb.playerPosY ):
				return None
			self.location = ( self.pb.playerMap, self.pb.playerPosX, self.pb.playerPosY )
			if self.location[ 0 ]:
				return self.location
			else:
				return ()
		except:
			return ()

	def sendMessage( self, receiver, message, performative='inform' ):
		msg = spade.ACLMessage.ACLMessage()
		msg.setPerformative( performative )
		rec = spade.AID.aid( "%s@127.0.0.1" % receiver, [ "xmpp://%s@127.0.0.1" % receiver ] )
		msg.addReceiver( rec )
		msg.setContent( message )
		self.send( msg )

	def say( self, msg ):
		''' Say something (e.g. print to console for debug purposes) '''
		print '%s | %s: %s' % ( time.strftime( '%H:%M:%S' ), self.name.split( '@' )[ 0 ], str( msg ) )

	def __init__( self, SERVER, PORT, USERNAME, PASSWORD, CHARACTER, *args, **kwargs ):
		spade.Agent.Agent.__init__( self, *args, **kwargs )
		lli.Connection.__init__( self, SERVER, PORT, USERNAME, PASSWORD, CHARACTER )
		lli.CHARACTER = self.name.split( '@' )[ 0 ]
		self.avatar_name = USERNAME

		self.kb = KB()
		self.destinationNPC = None

		# Check if there is an existing knowledge base
		self.kbfile = join( KBFOLDER, lli.CHARACTER + '.pl' )
		if isfile( self.kbfile ):
			try:
				self.say( 'I found my old brain!' )
				self.kb.ask( "['" + self.kbfile + "']" )
				self.say( 'Loaded my previous state of mind!' )
			except:
				self.say( 'Error while loading previous knowledge base file, aborting!' )
				import sys
				sys.exit()

		try:
			self.kb.ask( "['planner.pl']" )
			self.say( 'Planner loaded!' )
		except:
			self.say( 'Error while loading planner, aborting!' )
			import sys
			sys.exit()

		try:
			self.kb.ask( "['item-db.pl']" )
			self.say( 'Item knowledge base loaded!' )
		except:
			self.say( 'Error while loading item knowledge base, aborting!' )
			import sys
			sys.exit()

		try:
			self.kb.ask( "['npc-db.pl']" )
			self.say( 'NPC knowledge base loaded!' )
		except:
			self.say( 'Error while loading NPC knowledge base, aborting!' )
			import sys
			sys.exit()

		try:
			self.kb.ask( "['userids.pl']" )
			self.say( 'User IDs knowledge base loaded!' )
		except:
			self.say( 'Error while loading user IDs knowledge base, aborting!' )
			import sys
			sys.exit()

		try:
			self.say( 'Map knowledge base loading (this might take some time)!' )
			''' For now only the Candor maps are loaded '''
			self.kb.ask( "['tmwmap_candor.P']" )
			time.sleep( 3 )
			self.say( 'Map knowledge base loaded!' )
		except:
			self.say( 'Error while loading map knowledge base, aborting!' )
			import sys
			sys.exit()

	def _setup(self):
		self.login_complete = False

		reason = TMWbehavs.Reason()
		self.addBehaviour( reason )

if __name__ == '__main__':
	from testconf import *
	import argparse
	import os
	import glob

	parser = argparse.ArgumentParser( description='Create a TMW agent player (mali_agent[num])' )
	parser.add_argument( '--name', help='Create a TMW agent "mali_agent[num]" agents', type=int )
	parser.add_argument( '--num', help='Create [num] TMW agents from [name] to [name+num] "mali_agent[i]" agents', type=int )
	parser.add_argument( '--interval', help='Interval between agent instances in seconds', type=int, default=10 )
	parser.add_argument( '--clear', help='Clear existing knowledge bases (DANGEROUS: Deletes all .pl files from KBFOLDER)', action='store_true' )
	parser.add_argument( '--role', help='Agent(s) should have the given role (can be leader, extremist_follower or opportunist' )
	
	
	args = parser.parse_args()

	# Delete all knowledge bases
	if args.clear:
		files = glob.glob( join( KBFOLDER, '*.pl' ) )
		for f in files:
			os.remove( f )

	role = None
	if args.role:
		if args.role == 'leader':
			role = Leader()
		elif args.role == 'extremist_follower':
			role = ExtremistFollower()
		elif args.role == 'opportunist':
			role = Opportunist()
	
	if args.num and args.name:
		agent_list = []	
		for i in range( args.name, args.name + args.num ):
			a = ManaWorldPlayer( SERVER, PORT, 'mali_agent%d' % i, PASSWORD, CHARACTER, 'agent_%d@127.0.0.1' % i, 'tajna' )
			if role:
				a.addBehaviour( ChangeRole( role ) )
			a.start()
			time.sleep( args.interval )
			agent_list.append( a )
	elif args.name:
		a = ManaWorldPlayer( SERVER, PORT, 'mali_agent%d' % args.name, PASSWORD, CHARACTER, 'mali_agent%d@127.0.0.1' % args.name, 'tajna' )
		if role:
			a.addBehaviour( ChangeRole( role ) )
		a.start()

	else:
		print 'Invalid number of arguments. Type "hlinterface.py --help" for details.'
	
