#!/usr/bin/env python
#-*- coding: utf-8 -*-

import spade
from spade.SWIKB import SWIKB as KB
import llinterface as lli
import time

class ManaWorldPlayer( spade.Agent.BDIAgent, lli.Connection ):
	def say( self, msg ):
		''' Say something (e.g. print to console for debug purposes) '''
		print '%s: %s' % ( self.name.split( '@' )[ 0 ], str( msg ) )

	def getInventory( self ):
		''' Dummy inventory until lli is done '''
		return { 'bug leg':2, 'cotton shirt':1, 'hitchhikers towel':1 }

	def getVisibleMobs( self ):
		''' Dummy visible mobs until lli is done '''
		return { 'maggot':( '085-1', 125, 142 ), 'black scorpion':( '085-1', 122, 132 ) }

	def getMyLocation( self ):
		''' Dummy location until lli is done '''
		return ( '085-1', 119, 132 )

	def updateKB( self ):
		''' Update the knowledgebase based on current observation
		    of the environment in TMW, e.g.:
			- list own location
			- list the inventory
			- list current visible items laying around (include location and type)
			- list visible mobs/NPCs/other players (include location and name)
			- list any changes in quest acomplishment (e.g. quest solved)
			- list any ongoing or done conversation with NPCs that are possibly
			  giving out a quest
			- any changes in social network (e.g. friends, enemies etc.)
			- any changes in organization (e.g. party membership)
			...? 
		    and update the knowledge base accordingly'''
		self.say( 'Updating my stats ...' )
		if self.character_list:
			char = self.character_list[ self.character ]
			self.avatar_name = char.name
			for token, value in char.__dict__.items():
				delete_predicate = "retract( ownership( '%s', '%s', _ ) )" % ( self.avatar_name, token )
				if type( value ) == int:
					update_predicate = "assert( ownership( '%s', '%s', %d ) )" % ( self.avatar_name, token, value )
				else:
					update_predicate = "assert( ownership( '%s', '%s', '%s' ) )" % ( self.avatar_name, token, str( value ) )
				self.say( 'Updating knowledge base with: ' + update_predicate )
				self.kb.ask( delete_predicate )
				self.kb.ask( update_predicate )
			self.say( 'Updating my inventory ...' )
			inv = self.getInventory()
			for itemid, amount in inv.items():
				delete_predicate = "retract( ownership( '%s', '%s', _ ) )" % ( self.avatar_name, itemid )
				update_predicate = "assert( ownership( '%s', '%s', %d ) )" % ( self.avatar_name, itemid, amount )
				self.say( 'Updating knowledge base with: ' + update_predicate )
				self.kb.ask( delete_predicate )
				self.kb.ask( update_predicate )
			self.say( 'Updating visible mobs ...' )
			mobs = self.getVisibleMobs()
			# First delete all known locations
			delete_predicate = "retract( location( _, _, _, _ ) )"
			self.kb.ask( delete_predicate )
			for mob, loc in mobs.items():
				mapname, x, y = loc
				update_predicate = "assert( location( '%s', '%s', %d, %d ) )" % ( mob, mapname, x, y )
				self.say( 'Updating knowledge base with: ' + update_predicate )
				self.kb.ask( update_predicate )
			self.say( 'Updating my location ...' )
			mapname, x, y = self.getMyLocation()
			# Do not need to delete my location since all locations were deleted earlier
			update_predicate = "assert( location( '%s', '%s', %d, %d ) )" % ( self.avatar_name, mapname, x, y )
			self.say( 'Updating knowledge base with: ' + update_predicate )
			self.kb.ask( update_predicate )

	def updateObjectives( self ):
		''' List all possible objectives (e.g. unsolved quests) '''
		self.quests = self.askBelieve( 'waiting_quest( NPC, a, Name ).' )
		time.sleep( 1 )
		if self.quests:
			self.say( 'My current quests are:' )
			for quest in self.quests:
				try:
					self.say( quest[ 'Name' ] + ' given by ' + quest[ 'NPC' ] )
				except:
					pass
			return self.quests
		else:
			self.say( 'I have no current quests!' )
			return [ { 'Name':'random_walk', 'NPC':'anonymous' } ]
		

	def selectObjective( self, objectives ):
		''' Select most relevant objective (quest) to be solved next '''
		quests = self.askBelieve( 'sort_quests( A ), quest_no( NPC, A, Name, No ).' )
		if quests:
			next = sorted( quests, key=lambda x: x[ 'No' ] )[ 0 ][ 'Name' ]
			self.say( 'My next objective is quest: ' + next )
			return next
		time.sleep( 1 )

	class Login( spade.Behaviour.OneShotBehaviour ):
		def _process( self ):
			self.myAgent.login()

			time.sleep( 1 )
			self.myAgent.pb.go()			
			while not self.myAgent.pb.hasNew():
				time.sleep( 0.1 )

	class Reason( spade.Behaviour.Behaviour ):
		def _process( self ):
			self.myAgent.updateKB()
			obj = self.myAgent.updateObjectives()
			if obj[ 0 ][ 'Name' ] != 'random_walk':
				next = self.myAgent.selectObjective( obj )
			else:
				next = 'random_walk'
			
			# plan

	class ChangeRole(spade.Behaviour.OneShotBehaviour):
		"""Behaviour to change the Role of the Agent. The Agent will acquire behaviours of the needed Role."""
		def _process(self):
			pass
			
	def __init__( self, SERVER, PORT, USERNAME, PASSWORD, CHARACTER, *args, **kwargs ):
		spade.Agent.Agent.__init__( self, *args, **kwargs )
		lli.Connection.__init__( self, SERVER, PORT, USERNAME, PASSWORD, CHARACTER )
		lli.CHARACTER = self.name.split( '@' )[ 0 ]
		
		self.kb = KB()
		try:		
			self.kb.ask( "['planner.pl']" )
			self.say( 'Planner loaded!' )
		except:
			self.say( 'Error while loading planner, aborting!' )
			import sys
			sys.exit()

		try:		
			self.say( 'Map knowledge base loading in background!' )
			self.kb.ask( "['tmwmap.P']" )
		except:
			self.say( 'Error while loading map knowledge base, aborting!' )
			import sys
			sys.exit()


	def _setup( self ):
		login = self.Login()
		self.addBehaviour( login )

		reason = self.Reason()
		self.addBehaviour( reason )

if __name__ == '__main__':
	from testconf import *
	a = ManaWorldPlayer( SERVER, PORT, USERNAME, PASSWORD, CHARACTER, 'player@127.0.0.1', 'tajna' )
	a.start()
