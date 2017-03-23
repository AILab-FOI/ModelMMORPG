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
		''' Get current inventory 
		    Returns dictionary { itemID:itemAmount } '''
		''' TODO: make all getters to return None if there were no changes to optimize update '''
		try:
			inventory = self.pb.playerInventory
			if inventory:
				inv = dict( [ ( i.itemID, i.itemAmount ) for i in inventory.values() ] )
				return inv
		except:
			return {}

	def getVisibleItems( self ):
		''' Dummy visible items until lli is done '''
		return { 'maggot slime':( '085-1', 125, 142 ), 'bug leg':( '085-1', 122, 132 ) }

	def getVisibleMobs( self ):
		''' Get visible mobs 
		    Returns dictionary { mob_being_ID:( mobtype, mapID, X, Y ) } '''
		try:
			mobs = self.pb.monsterMovements
			mobs = dict( [ ( i, ( k[ -1 ][ 0 ], self.pb.playerMap, k[ -1 ][ 1 ], k[ -1 ][ 2 ] ) ) for i, k in mobs.items() ] )
			return mobs
		except:
			return None

	def getVisibleNPCs( self ):
		''' Dummy visible NPCs until lli is done '''
		return { 'Sorfina':( '085-1', 125, 142 ), 'Tanisha':( '085-1', 122, 132 ) }

	def getVisiblePlayers( self ):
		''' Dummy visible players until lli is done '''
		return { 'Bogdan':( '085-1', 125, 142 ), 'Igor':( '085-1', 122, 132 ) }

	def getMyLocation( self ):
		''' Get player location 
		    Returns tuple ( mapID, X, Y ) '''
		try:
			self.location = ( self.pb.playerMap, self.pb.playerPosX, self.pb.playerPosY )
			if self.location[ 0 ]:
				return self.location
		except:
			return None

	def getNewNPCMessages( self ):
		''' Dummy NPC messages until lli is done '''
		return { 'Sorfina': [ 'Hello!', 'Put on a shirt!' ], 'Tanisha': [ 'Can you take care of the maggots?', 'Go outside!' ] }

	def interpretNPCMessage( self, npc, message ):
		''' Interpret NPC messages 
		    Returns tuple ( waiting_quest( npc, %s, quest_name ), quest_name ) 
		    The first element in the tuple is a string Prolog predicate 
		    for the knowledge base where %s is a place to insert the agent's 
		    character name '''
		if npc == 'Sorfina':
			if message == 'Put on a shirt!':
				return "waiting_quest( '" + npc + "', '%s', tutorial )", "tutorial"
		elif npc == 'Tanisha':
			if message == 'Can you take care of the maggots?':
				return "waiting_quest( '" + npc + "', '%s', maggots )", "maggots"
			elif message == 'Go outside!':
				return "waiting_quest( '" + npc + "', '%s', outside )", "outside"
		return False, None

	def getQuestSignificance( self, quest ):
		''' Hard-coded significances of various quests loosely modelled after 
		    time of acquirement. First one is Sorfina's tutorial, then Tanisha's
		    maggots, then ... '''
		if quest == 'tutorial':
			return 10000
		elif quest == 'maggots':
			return 9999
		elif quest == 'outside':
			return 9998
		else:
			# (yet) unknown quest
			return 0

	def getPartyMembership( self ):
		''' Dummy party membership until lli is done '''
		return None # None if no membership, else name of party

	def getSocialNetwork( self ):
		''' Dummy social network until lli is done '''
		return { 'Igor':'friend', 'Bogdan':'friend', 'Ivek':'enemy' }

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
		
		if self.character_list:
			self.say( 'Updating my stats ...' )
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
			if inv:
				for itemid, amount in inv.items():
					delete_predicate = "retract( ownership( '%s', %s, _ ) )" % ( self.avatar_name, itemid )
					update_predicate = "assert( ownership( '%s', %s, %d ) )" % ( self.avatar_name, itemid, amount )
					self.say( 'Updating knowledge base with: ' + update_predicate )
					self.kb.ask( delete_predicate )
					self.kb.ask( update_predicate )
			else:
				self.say( 'Inventory not loaded yet ...' )

			self.say( 'Updating visible mobs ...' )
			mobs = self.getVisibleMobs()
			# First delete all known locations
			delete_predicate = "retract( location( _, _, _, _ ) )"
			self.kb.ask( delete_predicate )
			for loc in mobs.values():
				mob, mapname, x, y = loc
				update_predicate = "assert( location( %s, '%s', %d, %d ) )" % ( mob, mapname, x, y )
				self.say( 'Updating knowledge base with: ' + update_predicate )
				self.kb.ask( update_predicate )

			self.say( 'Updating visible NPCs ...' ) # NOTE: NPCs should be stored permanentnly with an additional predicate
			npcs = self.getVisibleNPCs()
			for npc, loc in npcs.items():
				mapname, x, y = loc
				update_predicate = "assert( location( '%s', '%s', %d, %d ) )" % ( npc, mapname, x, y )
				self.say( 'Updating knowledge base with: ' + update_predicate )
				self.kb.ask( update_predicate )

			self.say( 'Updating visible players ...' )
			players = self.getVisiblePlayers()
			for p, loc in players.items():
				mapname, x, y = loc
				update_predicate = "assert( location( '%s', '%s', %d, %d ) )" % ( p, mapname, x, y )
				self.say( 'Updating knowledge base with: ' + update_predicate )
				self.kb.ask( update_predicate )

			self.say( 'Updating visible items ...' )
			itms = self.getVisibleItems()
			for item, loc in itms.items():
				mapname, x, y = loc
				update_predicate = "assert( location( '%s', '%s', %d, %d ) )" % ( item, mapname, x, y )
				self.say( 'Updating knowledge base with: ' + update_predicate )
				self.kb.ask( update_predicate )

			self.say( 'Updating my location ...' )
			location = self.getMyLocation()
			if location:
				mapname, x, y = location 
				# Do not need to delete my location since all locations were deleted earlier
				update_predicate = "assert( location( '%s', '%s', %s, %s ) )" % ( self.avatar_name, mapname, x, y )
				self.say( 'Updating knowledge base with: ' + update_predicate )
				self.kb.ask( update_predicate )
			else:
				self.say( 'Location unknown ...' )

			self.say( 'Updating NPC conversations ...' ) # not deleting old messages
			npc_messages = self.getNewNPCMessages()
			for npc, messages in npc_messages.items():
				for message in messages:
					update_predicate = "assert( npc_message( '%s', '%s', '%s' ) )" % ( self.avatar_name, npc, message )
					self.kb.ask( update_predicate )
					self.say( 'Updating knowledge base with: ' + update_predicate )
					update, quest = self.interpretNPCMessage( npc, message )
					if update:
						if not self.kb.ask( update % self.avatar_name ): # if I haven't got this quest already
							update_predicate = 'assert( %s )' % update % self.avatar_name
							self.kb.ask( update_predicate )
							self.say( 'Updating knowledge base with: ' + update_predicate )
							sign = self.getQuestSignificance( quest )
							update_predicate = "assert( quest_sign( '%s', '%s', %d ) )" % ( self.avatar_name, quest, sign )
							self.kb.ask( update_predicate )
							self.say( 'Updating knowledge base with: ' + update_predicate )
							delete_predicate = "retract( quest_no( '%s', '%s', '%s', _ ) )" % ( npc, self.avatar_name, quest )
							self.kb.ask( delete_predicate )
							update_predicate = "assert( quest_no( '%s', '%s', '%s', 1 ) )" % ( npc, self.avatar_name, quest )
							self.kb.ask( update_predicate )
							self.say( 'Updating knowledge base with: ' + update_predicate )

			self.say( 'Updating my party membership ...' )
			party = self.getPartyMembership()
			if party:
				delete_predicate = "retract( party( '%s', _ ) )" % self.avatar_name
				update_predicate = "assert( party( '%s', '%s' ) )" % ( self.avatar_name, party )
				self.say( 'Updating knowledge base with: ' + update_predicate )
				self.kb.ask( delete_predicate )
				self.kb.ask( update_predicate )
			else:
				self.say( 'I am no party member ...' )

			self.say( 'Updating my social network ...' )
			soc_net = self.getSocialNetwork()
			delete_predicate = "retract( social_network( '%s', _, _ ) )" % self.avatar_name
			self.kb.ask( delete_predicate )
			for player, tag in soc_net.items():
				update_predicate = "assert( social_network( '%s', '%s', '%s' ) )" % ( self.avatar_name, player, tag )
				self.say( 'Updating knowledge base with: ' + update_predicate )
				self.kb.ask( update_predicate )
				 

	def updateObjectives( self ):
		''' List all possible objectives (e.g. unsolved quests) '''
		try:
			self.say( 'My avatar name is ' + self.avatar_name )
		except:
			self.say( "My avatar hasn't loaded yet ..." )
			time.sleep( 1 )
			return None
		self.quests = self.askBelieve( "waiting_quest( NPC, '%s', Name )." % self.avatar_name )
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
		quests = self.askBelieve( "sort_quests( '%s' ), quest_no( NPC, '%s', Name, No )." % ( self.avatar_name, self.avatar_name ) )
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
			
			self.myAgent.locatePlayer()
		
			while not self.myAgent.pb.hasNew():
				time.sleep( 0.1 )

	class Reason( spade.Behaviour.Behaviour ):
		def _process( self ):
			self.myAgent.updateKB()
			obj = self.myAgent.updateObjectives()
			if obj and obj[ 0 ][ 'Name' ] != 'random_walk':
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
			self.kb.ask( "['item-db.pl']" )
			self.say( 'Item knowledge base loaded!' )
		except:
			self.say( 'Error while loading item knowledge base, aborting!' )
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
