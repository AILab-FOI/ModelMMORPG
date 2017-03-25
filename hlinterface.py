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
		if not hasattr( self, 'inventory_cache' ):
			self.inventory_cache = None
		try:
			if self.inventory_cache == self.pb.playerInventory:
				return None # No changes in inventory
			else:
				self.inventory_cache = self.pb.playerInventory
			if inventory:
				inv = dict( [ ( i.itemID, i.itemAmount ) for i in self.inventory_cache.values() ] )
				return inv
		except:
			return {}

	def getVisibleItems( self ):
		''' Get visible (dropped) items
		    Returns dictionary { itemID: ( amount, mapID, X, Y ) } '''
		if not hasattr( self, 'droppeditems_cache' ):
			self.droppeditems_cache = None
		try:
			if self.droppeditems_cache == self.pb.droppedItems:
				return None
			self.droppeditems_cache = self.pb.droppedItems
			items = dict( [ ( i[ 0 ], ( i[ 3 ], self.pb.playerMap, i[ 1 ], i[ 2 ] ) ) for i in self.droppeditems_cache ] )
			return items
		except:
			return {}

	def getVisibleMobs( self ):
		''' Get visible mobs 
		    Returns dictionary { mob_being_ID:( mobtype, mapID, X, Y ) } '''
		if not hasattr( self, 'mobs_cache' ):
			self.mobs_cache = None
		try:
			if self.mobs_cache == self.pb.monsterMovements:
				return None
			self.mobs_cache = self.pb.monsterMovements
			mobs = dict( [ ( i, ( k[ -1 ][ 0 ], self.pb.playerMap, k[ -1 ][ 1 ], k[ -1 ][ 2 ] ) ) for i, k in self.mobs_cache.items() ] )
			return mobs
		except:
			return None

	def getVisibleNPCs( self ):
		''' Dummy visible NPCs until lli is done '''
		return { 'Sorfina':( '085-1', 125, 142 ), 'Tanisha':( '085-1', 122, 132 ) }

	def getVisiblePlayers( self ):
		''' Get visible (all) players
		    Returns dict { character_name:( Map, X, Y ) } '''
		if not hasattr( self, 'players_cache' ):
			self.players_cache = None
		try:
			self.listAllPlayers()
			time.sleep( 1 )
			if self.players_cache == self.pb.loggedInPlayers:		
				return None
			self.players_cache = self.pb.loggedInPlayers
			return self.players_cache
		except:
			return {}

	def getMyLocation( self ):
		''' Get player location 
		    Returns tuple ( mapID, X, Y ) '''
		if not hasattr( self, 'location' ):
			self.location = None
		try:
			if self.location == ( self.pb.playerMap, self.pb.playerPosX, self.pb.playerPosY ):
				return None
			self.location = ( self.pb.playerMap, self.pb.playerPosX, self.pb.playerPosY )
			if self.location[ 0 ]:
				return self.location
			else:
				return ()
		except:
			return ()

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
		''' Get party membership
		    Raturns string party name (-1 if no party, None if no change) '''
		if not hasattr( self, 'party_cache' ):
			self.party_cache = None
		try:
			self.partyStatus( self.avatar_name, self.avatar_name )
			time.sleep( 1 )
			if self.party_cache == self.pb.playerParty[ self.avatar_name ]:
				return None			
			self.party_cache = self.pb.playerParty[ self.avatar_name ]
			return self.party_cache
		except:
			return None
		return -1

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
			if not hasattr( self, 'char_cache' ):
				self.char_cache = None

			try:
				test = self.char_cache.__dict__ != self.character_list[ self.character ].__dict__
			except:
				test = True

			if test:
				self.char_cache = self.character_list[ self.character ]
				self.avatar_name = self.char_cache.name
				for token, value in self.char_cache.__dict__.items():
					delete_predicate = "retract( ownership( '%s', '%s', _ ) )" % ( self.avatar_name, token )
					if type( value ) == int:
						update_predicate = "assert( ownership( '%s', '%s', %d ) )" % ( self.avatar_name, token, value )
					else:
						update_predicate = "assert( ownership( '%s', '%s', '%s' ) )" % ( self.avatar_name, token, str( value ) )
					self.say( 'Updating knowledge base with: ' + update_predicate )
					self.kb.ask( delete_predicate )
					self.kb.ask( update_predicate )
			else:
				self.say( 'No changes in my stats ...' )

			self.say( 'Updating my inventory ...' )
			
			inv = self.getInventory()
			if inv:
				for itemid, amount in inv.items():
					delete_predicate = "retract( ownership( '%s', %s, _ ) )" % ( self.avatar_name, itemid )
					update_predicate = "assert( ownership( '%s', %s, %d ) )" % ( self.avatar_name, itemid, amount )
					self.say( 'Updating knowledge base with: ' + update_predicate )
					self.kb.ask( delete_predicate )
					self.kb.ask( update_predicate )
			elif inv == None:
				self.say( 'No changes in inventory ...' )
			else:
				self.say( 'Inventory not loaded yet ...' )

			self.say( 'Updating visible mobs ...' )
			mobs = self.getVisibleMobs()
			# First delete all known locations
			if mobs:
				delete_predicate = "retract( location( _, _, _, _ ) )"
				self.kb.ask( delete_predicate )
				for loc in mobs.values():
					mob, mapname, x, y = loc
					update_predicate = "assert( location( %s, '%s', %d, %d ) )" % ( mob, mapname, x, y )
					self.say( 'Updating knowledge base with: ' + update_predicate )
					self.kb.ask( update_predicate )
			elif mobs == None:
				self.say( 'No changes in visible mobs ...' )
			else:
				self.say( 'No critters creeping around ...' )

			self.say( 'Updating visible NPCs ...' ) # NOTE: NPCs should be stored permanentnly with an additional predicate
			npcs = self.getVisibleNPCs()
			for npc, loc in npcs.items():
				mapname, x, y = loc
				update_predicate = "assert( location( '%s', '%s', %d, %d ) )" % ( npc, mapname, x, y )
				self.say( 'Updating knowledge base with: ' + update_predicate )
				self.kb.ask( update_predicate )

			self.say( 'Updating visible players ...' )
			players = self.getVisiblePlayers()
			if players:
				for p, loc in players.items():
					mapname, x, y = loc
					update_predicate = "assert( location( '%s', '%s', %s, %s ) )" % ( p, mapname, x, y )
					self.say( 'Updating knowledge base with: ' + update_predicate )
					self.kb.ask( update_predicate )
			elif players == None:
				self.say( 'No changes in visible players ...' )
			else:
				self.say( 'No visible players available ...' )

			self.say( 'Updating visible items ...' )
			itms = self.getVisibleItems()
			if itms:
				for item, loc in itms.items():
					amount, mapname, x, y = loc
					update_predicate = "assert( location( '%s', %d, '%s', %d, %d ) )" % ( item, amount, mapname, x, y )
					self.say( 'Updating knowledge base with: ' + update_predicate )
					self.kb.ask( update_predicate )
			elif itms == None:
				self.say( 'No changes in visible items ...' )
			else:
				self.say( 'No items lying around at this location ...' )

			self.say( 'Updating my location ...' )
			location = self.getMyLocation()
			if location:
				mapname, x, y = location 
				# Do not need to delete my location since all locations were deleted earlier
				update_predicate = "assert( location( '%s', '%s', %s, %s ) )" % ( self.avatar_name, mapname, x, y )
				self.say( 'Updating knowledge base with: ' + update_predicate )
				self.kb.ask( update_predicate )
			elif location == None:
				self.say( "I didn't change my location ..." )
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
			if party == -1:
				self.say( 'I am no party member ...' )
			elif party == None:
				self.say( 'No change in party membership ...' )
			else:				
				delete_predicate = "retract( party( '%s', _ ) )" % self.avatar_name
				update_predicate = "assert( party( '%s', '%s' ) )" % ( self.avatar_name, party )
				self.say( 'Updating knowledge base with: ' + update_predicate )
				self.kb.ask( delete_predicate )
				self.kb.ask( update_predicate )

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
		''' Login to TMW server and locate the player '''
		def _process( self ):
			login_complete = False
			while not login_complete:
				self.myAgent.login()
				time.sleep( 1 )
				self.myAgent.pb.go()
				counter = 0
				while not self.myAgent.pb.hasNew():
					time.sleep( 0.1 )
					counter += 1
					if counter > 10:
						break

				if counter >= 10:
					continue

				try:		
					self.myAgent.locatePlayer()
				except:
					continue

				time.sleep( 1 )
	
				if not self.myAgent.pb.playerMap:
					print 10
					continue

				login_complete = True

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
			self.kb.ask( "['npc-db.pl']" )
			self.say( 'NPC knowledge base loaded!' )
		except:
			self.say( 'Error while loading NPC knowledge base, aborting!' )
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
