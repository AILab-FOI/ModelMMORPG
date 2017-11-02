#!/usr/bin/env python
#-*- coding: utf-8 -*-

import spade
from spade.SWIKB import SWIKB as KB
import llinterface as lli
import time
from random import random, randint, choice
from os.path import isfile, join

class ManaWorldPlayer( spade.Agent.BDIAgent, lli.Connection ):
	def say( self, msg ):
		''' Say something (e.g. print to console for debug purposes) '''
		print '%s: %s' % ( self.name.split( '@' )[ 0 ], str( msg ) )

	def storeKB( self ):
		''' Store the current state of the KB for later use '''
		self.kb.ask( "store( '%s' )" % self.kbfile )
		self.say( 'Stored my current state of mind!' )

	def getInventory( self ):
		''' Get current inventory 
		    Returns dictionary { itemSlot:( itemID, itemAmount ) } '''
		''' TODO: make all getters to return None if there were no changes to optimize update '''
		if not hasattr( self, 'inventory_cache' ):
			self.inventory_cache = None
		try:
			if self.inventory_cache == self.pb.playerInventory:
				return None # No changes in inventory
			self.inventory_cache = dict( [ ( i, j ) for i, j in self.pb.playerInventory.items() ] )
			if self.inventory_cache:
				inv = dict( [ ( j, ( i.itemID, i.itemAmount ) ) for j, i in self.inventory_cache.items() ] )
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
			print 'Monster movements (agent):', self.pb.monsterMovements
			print 'Update cache?:', self.mobs_cache == self.pb.monsterMovements
			if self.mobs_cache == self.pb.monsterMovements:
				print 'Nothing to update'
				return None
			self.mobs_cache = dict( [ ( i, j ) for i, j in self.pb.monsterMovements.items() ] )
			mobs = dict( [ ( i, ( k[ -1 ][ 0 ], self.pb.playerMap, k[ -1 ][ 1 ], k[ -1 ][ 2 ] ) ) for i, k in self.mobs_cache.items() ] )
			print 'Returning', mobs
			return mobs
		except Exception, e:
			print e
			return None

	def getVisibleNPCs( self, recursion_level=0 ):
		''' Get visible NPCs (e.g. NPCs on the same map) 
		    returns dict { NPC name:( Map, X, Y, NPC type ) }'''
		MAX_RECURSION = 3
		if not hasattr( self, 'location' ) or self.location == None:
			return {}
		if not hasattr( self, 'map_cache' ):
			self.map_cache = None
		if self.map_cache == self.location[ 0 ] and recursion_level == 0:
			return None # I'm still on the same map, so the NPCs are the same
		self.map_cache = self.location[ 0 ]
		query = "npc( Type, Name, '%s', X, Y )" % self.location[ 0 ]
		time.sleep( 1 )
		self.say( "Querying knowledge base with: " + query )
		res = self.kb.ask( query )
		NPCs = {}
		# TODO: Remove debug message comments
		#print res
		if res:
			for r in res:
				if r.has_key( 'Name' ):
					if not 'Debug' in r[ 'Name' ]:
						NPCs[ r[ 'Name' ] ] = ( self.location[ 0 ], r[ 'X' ], r[ 'Y' ], r[ 'Type' ] )
		else:
			print 'Trying again', recursion_level, MAX_RECURSION
			if recursion_level <= MAX_RECURSION:
				time.sleep( 1 )
				return self.getVisibleNPCs( recursion_level + 1 )
		return NPCs

	def getVisiblePlayers( self ):
		''' Get visible players
		    Returns dict { character_name:( Map, X, Y ) } '''
		if not hasattr( self, 'players_cache' ):
			self.players_cache = None
		try:
			self.listAllPlayers()
			time.sleep( 1 )
			if self.players_cache == self.pb.loggedInPlayers:		
				return None
			self.players_cache = self.pb.loggedInPlayers
			# visible players are only players on the same map as I am
			visible_players = dict( [ ( i[ 0 ], i[ 1 ] ) for i in self.players_cache.items() if i[ 1 ][ 0 ] == self.location[ 0 ] ] )
			return visible_players
		except:
			return {}

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

	def getNewNPCMessages( self ):
		''' Dummy NPC messages until lli is done '''
		if not hasattr( self, 'npcmsg_cache' ):
			self.npcmsg_cache = []
		try:
			if self.npcmsg_cache == self.pb.npcMessages:
				return None
			npc_msgs = [ i for i in self.pb.npcMessages if i not in self.npcmsg_cache ]
			self.npcmsg_cache.extend( [ i for i in npc_msgs ] )
			msgs = {}
			for npcid, message in npc_msgs: 
				if not msgs.has_key( npcid ):
					msgs[ npcid ] = []
				msgs[ npcid ].append( message )
			return msgs
		except:
			return {}

	def interpretNPCMessage( self, npc, message ):
		''' Interpret NPC messages 
		    Returns tuple ( waiting_quest( npc, %s, quest_name ), quest_name, npc name ) 
		    The first element in the tuple is a string Prolog predicate 
		    for the knowledge base where %s is a place to insert the agent's 
		    character name '''

		try:
			query = "npc_id( %s, Name )" % npc
			res = self.kb.ask( query )
			npc = res[ 0 ][ "Name" ]
		except:
			pass
		
		# TODO: Also interpret other messages as possible preconditions for other actions
		if npc == 'ServerInitial':
			if message == '[Server/Client Notice]':
				return "waiting_quest( 'Sorfina', '%s', tutorial )", "tutorial", "Sorfina"
			else:
				return False, None, "Sorfina"
		elif npc == 'Sorfina' or npc == '110008655':
			return False, None, "Sorfina"
		elif npc == 'Dresser#tutorial':
			return False, None, "Sorfina"
		elif npc == 'Tanisha':
			return "waiting_quest( 'Tanisha', '%s', maggots )", "maggots", "Tanisha"
		elif npc == 'Soul Menhir#candor':
			return "waiting_quest( 'Soul Menhir#candor', '%s', soul_menhir_candor )", "soul_menhir_candor", "Soul Menhir#candor"
		elif npc == 'Kaan':
			return "waiting_quest( 'Kaan', '%s', kaan )", "kaan", "Kaan"
		elif npc == 'Aiden':
			return "waiting_quest( 'Aiden', '%s', monster_points )", "monster_points", "Aiden"
		return "waiting_quest( '%s', '%s', stop_talking )" % npc, "stop_talking", npc

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
			if self.party_cache == 'None':
				return -1
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


			self.say( 'Updating my location ...' )
			location = self.getMyLocation()
			if location:
				mapname, x, y = location 
				delete_predicate = "retract( agent_location( _, _, _, _ ) )"
				update_predicate = "assert( agent_location( '%s', '%s', %s, %s ) )" % ( self.avatar_name, mapname, x, y )
				self.say( 'Updating knowledge base with: ' + update_predicate )
				self.kb.ask( delete_predicate )
				self.kb.ask( update_predicate )
			elif location == None:
				self.say( "I didn't change my location ..." )
			else:
				self.say( 'Location unknown ...' )

			self.say( 'Updating my inventory ...' )
			# TODO: Possibly a bug
			inv = self.getInventory()
			if inv:
				for slot, j in inv.items():
					itemid, amount = j
					delete_predicate = "retract( ownership( '%s', %s, _ ) )" % ( self.avatar_name, itemid )
					update_predicate1 = "assert( ownership( '%s', %s, %d ) )" % ( self.avatar_name, itemid, amount )
					update_predicate2 = "assert( slot( '%s', %d, %s, %d ) )" % ( self.avatar_name, slot, itemid, amount )
					self.say( 'Updating knowledge base with: ' + update_predicate1 )
					self.say( 'Updating knowledge base with: ' + update_predicate2 )
					self.kb.ask( delete_predicate )
					self.kb.ask( update_predicate1 )
					self.kb.ask( update_predicate2 )
			elif inv == None:
				self.say( 'No changes in inventory ...' )
			else:
				self.say( 'Inventory not loaded yet ...' )


			self.say( 'Updating visible mobs ...' )
			mobs = self.getVisibleMobs()
			# First delete all known locations
			if mobs:
				delete_predicate = "retract( mob_location( _, _, _, _, _ ) )"
				self.kb.ask( delete_predicate )
				for mobid, loc in mobs.items():
					mob, mapname, x, y = loc
					update_predicate = "assert( mob_location( %s, '%s', %d, %d, %d ) )" % ( mob, mapname, x, y, mobid )
					self.say( 'Updating knowledge base with: ' + update_predicate )
					self.kb.ask( update_predicate )
			elif mobs == None:
				self.say( 'No changes in visible mobs ...' )
			else:
				self.say( 'No critters creeping around ...' )

			
			self.say( 'Updating visible NPCs ...' )
			npcs = self.getVisibleNPCs()
			if npcs:
				for npc, loc in npcs.items():
					mapname, x, y, ID = loc
					update_predicate = "assert( npc_location( '%s', '%s', %s, %s ) )" % ( npc, mapname, x, y )
					self.say( 'Updating knowledge base with: ' + update_predicate )
					self.kb.ask( update_predicate )
			elif npcs == None:
				self.say( 'No changes in visible NPCs ...' )
			else:
				self.say( "There are seemingly no NPCs on this map, or my location hasn't loaded yet ..." )

			self.say( 'Updating visible players ...' )
			players = self.getVisiblePlayers()
			if players:
				delete_predicate = "retract( player_location( _, _, _, _ ) )"
				self.kb.ask( delete_predicate )
				for p, loc in players.items():
					mapname, x, y = loc
					update_predicate = "assert( player_location( '%s', '%s', %s, %s ) )" % ( p, mapname, x, y )
					self.say( 'Updating knowledge base with: ' + update_predicate )
					self.kb.ask( update_predicate )
			elif players == None:
				self.say( 'No changes in visible players ...' )
			else:
				self.say( 'No visible players available ...' )


			self.say( 'Updating visible items ...' )
			itms = self.getVisibleItems()
			if itms:
				delete_predicate = "retract( item_location( _, _, _, _, _ ) )"
				for item, loc in itms.items():
					amount, mapname, x, y = loc
					update_predicate = "assert( item_location( '%s', %d, '%s', %d, %d ) )" % ( item, amount, mapname, x, y )
					self.say( 'Updating knowledge base with: ' + update_predicate )
					self.kb.ask( update_predicate )
			elif itms == None:
				self.say( 'No changes in visible items ...' )
			else:
				self.say( 'No items lying around at this location ...' )

			self.say( 'Updating NPC conversations ...' ) # not deleting old messages
			try:
				npc_messages = self.getNewNPCMessages()
			except Exception as e:
				print e
			counter = 1
			try:
				if npc_messages:
					for npc, messages in npc_messages.items():
						for message in messages:
							res = self.interpretNPCMessage( npc, message )
							update, quest, npc = res
							if npc:
								print message
								update_predicate = "assert( npc_message( '%s', '%s', '%s' ) )" % ( self.avatar_name, npc, message.replace( "'", "\\'" ).replace( "\n", " " ) )
								self.kb.ask( update_predicate )
								self.say( 'Updating knowledge base with: ' + update_predicate )
							if update:
								try:
									if not self.kb.ask( update % self.avatar_name ) and not self.kb.ask( "solved_quest( '%s' )" % quest ): # if I haven't got this quest already and it isn't solved
										update_predicate = 'assert( %s )' % update % self.avatar_name
										self.kb.ask( update_predicate )
										self.say( 'Updating knowledge base with: ' + update_predicate )
										sign = self.getQuestSignificance( quest )
										update_predicate = "assert( quest_sign( '%s', '%s', %d ) )" % ( self.avatar_name, quest, sign )
										self.kb.ask( update_predicate )
										self.say( 'Updating knowledge base with: ' + update_predicate )
										delete_predicate = "retract( quest_no( '%s', '%s', '%s', _ ) )" % ( npc, self.avatar_name, quest )
										self.kb.ask( delete_predicate )
										counter += 1
										update_predicate = "assert( quest_no( '%s', '%s', '%s', %d ) )" % ( npc, self.avatar_name, quest, counter )
										self.kb.ask( update_predicate )
										self.say( 'Updating knowledge base with: ' + update_predicate )
								except Exception as e:
									print e
				elif npc_messages == 'None':
					self.say( 'No new NPC messages ...' )
				else:
					self.say( 'No NPC messages arrived yet ...' )
			except Exception as e:
				print 'ERROR', e


			'''self.say( 'Updating my party membership ...' )
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
				self.kb.ask( update_predicate )'''

			self.say( 'Updating my social network ...' )
			soc_net = self.getSocialNetwork()
			delete_predicate = "retract( social_network( '%s', _, _ ) )" % self.avatar_name
			self.kb.ask( delete_predicate )
			for player, tag in soc_net.items():
				update_predicate = "assert( social_network( '%s', '%s', '%s' ) )" % ( self.avatar_name, player, tag )
				self.say( 'Updating knowledge base with: ' + update_predicate )
				self.kb.ask( update_predicate )
		# Store my knowledgebase		
		self.storeKB()

				 

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
		query = "sort_quests( '%s' ), quest_no( NPC, '%s', Name, No ), \+ solved_quest( Name )." % ( self.avatar_name, self.avatar_name )
		quests = self.askBelieve( query )
		if quests:
			next = sorted( quests, key=lambda x: x[ 'No' ] )[ 0 ][ 'Name' ]
			self.say( 'My next objective is quest: ' + next )
			return next
		time.sleep( 1 )

	def getNextAction( self, quest ):
		''' Derive the next action of the current quest '''
		if quest == 'random_walk':
			return [ 'randomWalk', [] ]
		time.sleep( 1 )
		query = "next_action( _action ), do_action( _action, Action, _params ), member( Param, _params )"
		res = self.kb.ask( query )
		#print res
		if res:
			action = [ 1, [] ]
			for r in res:
				action[ 0 ] = r[ 'Action' ]
				action[ 1 ].append( r[ 'Param' ] )
			return action
		else:
			res = self.kb.ask( query )
			if res:
				action = [ 1, [] ]
				for r in res:
					action[ 0 ] = r[ 'Action' ]
					action[ 1 ].append( r[ 'Param' ] )
				return action
			self.say( 'I have no idea how to solve quest "%s" ...' % quest )
			return None

	def planQuest( self, quest ):
		''' Derive a plan and start the quest '''
		if quest == 'random_walk':
			return True
		time.sleep( 1 )
		query = "start_quest( '%s' )"  % quest
		res = self.kb.ask( query )
		if res:
			return True # quest planned and started
		else: 
			return False # cannot plan or start quest	

	def isThereANearByNPC( self ):
		mp, x, y = self.location
		query = "MapName = '%s', npc_location( NPC, MapName, X, Y ), npc( _, NPC, MapName, X, Y ), npc_id( NID, NPC ), DX is abs( X - %s ), DY is abs( Y - %s ), DX < 6, DY < 6." % ( mp, x, y )
		res = self.kb.ask( query  )
		if res:
			return choice( res )

	def isThereANearMobWithType( self, mobname ):
		mp, x, y = self.location
		'''query = "mob_location( MID, '%s', X, Y, BID ), mob( MID, _, '%s' ), DX is abs( %s - X ), DY is abs( %s - Y ), DX < 6, DY < 6" % ( mp, mobname, x, y )
		res = self.kb.ask( query )
		res = sorted( res, key=lambda x:x[ 'BID' ] )
		if res:
			return res'''

		query = "mob( MID, _, '%s' )" % mobname
		res = self.kb.ask( query )
		ret = [ { "BID":bid, "X":l[ -1 ][ 1 ], "Y":l[ -1 ][ 2 ] } for bid, l in self.pb.monsterMovements.items() if l[ -1 ][ 0 ] == int( res[ 0 ][ "MID" ] ) ]
		return sorted( ret, key=lambda x: x[ "BID" ] )
			
		

	def act( self, action ):
		''' Act out an action '''
		time.sleep( 1 )
		if action[ 0 ] == 'randomWalk':
			try:
				nearnpc = self.isThereANearByNPC()
				if nearnpc:
					npc = nearnpc[ 'NPC' ]
					npcID = nearnpc[ 'NID' ]
					mapID = nearnpc[ 'MapName' ]
					x = int( nearnpc[ 'X' ] )
					y = int( nearnpc[ 'Y' ] )
					try:
						self.say( "Going to nearby NPC %s at location %s-%d-%d ..." % ( npc, mapID, x, y ) )
						self.setDestination( x, y, 2 )
						time.sleep( 2 )
						self.act( [ 'talkToNPC', [ npcID ] ] )
						return True
					except Exception as e:
						print e
						return False
				mp, x, y = self.location
				mn, mx = -5, 6
				x = int( x )
				y = int( y )
				x += randint( mn, mx )
				y += randint( mn, mx )
				self.setDestination( x, y, 2 )
				time.sleep( 1 )
				return True
			except Exception as e:
				print e
				return False
		elif action[ 0 ] == 'answerNPC':
			npcID = int( action[ 1 ][ 0 ] )
			answer = int( action[ 1 ][ 1 ] )
			try:
				self.say( "Answering to NPC %d with %d ..." % ( npcID, answer ) )
				self.answerToNPC( npcID, answer )
				time.sleep( 1 )
				return True
			except Exception as e:
				print e
				return False
		elif action[ 0 ] == 'stopTalkingToNPC':
			npcID = int( action[ 1 ][ 0 ] )
			try:
				self.say( "Stopping communication with NPC %d ..." % npcID )
				self.closeCommunication( npcID )
				return True
			except Exception as e:
				print e
				return False
		elif action[ 0 ] == 'stopTalkingToNPCSorfina':
			npcID = int( action[ 1 ][ 0 ] )
			try:
				self.say( "Stopping communication with NPC %d ..." % npcID )
				self.closeCommunication( npcID )
				return True
			except Exception as e:
				print e
				return False
		elif action[ 0 ] == 'talkToNPC':
			npcID = int( action[ 1 ][ 0 ] )
			try:
				self.say( "Talking to NPC %d ..." % npcID )
				self.talkToNPC( npcID )
				return True
			except Exception as e:
				print e
				return False
		elif action[ 0 ] == 'goToNPC':
			# TODO: implement navigation to other maps when necessary
			npc = action[ 1 ][ 0 ]
			mapID = action[ 1 ][ 1 ]
			x = int( action[ 1 ][ 2 ] )
			y = int( action[ 1 ][ 3 ] )
			try:
				self.say( "Going to NPC %s at location %s-%d-%d ..." % ( npc, mapID, x, y ) )
				self.setDestination( x, y, 2 )
				time.sleep( 2 )
				return True
			except Exception as e:
				print e
				return False
		elif action[ 0 ] == 'goToLocation' or action[ 0 ] == 'tryToGoToLocation':
			# TODO: implement navigation to other maps when necessary
			mapID = action[ 1 ][ 0 ]
			x = int( action[ 1 ][ 1 ] )
			y = int( action[ 1 ][ 2 ] )
			try:
				self.say( "Going to location %s-%d-%d ..." % ( mapID, x, y ) )
				self.setDestination( x, y, 2 )
				time.sleep( 2 )
				return True
			except Exception as e:
				print e
				return False
		elif action[ 0 ] == 'equipItem':
			slot = int( action[ 1 ][ 0 ] )
			try:
				self.say( "Trying to equip item in slot %d ..." % ( slot ) )
				self.itemEquip( slot )
				time.sleep( 1 )
				return True
			except Exception as e:
				print e
				return False
		elif action[ 0 ] == 'killMob':
			mobname = action[ 1 ][ 0 ]
			try:
				self.say( "Trying to attack a %s ..." % ( mobname ) )
				mobs = self.isThereANearMobWithType( mobname )[ ::-1 ] # start with the last mob seen
				mob = False
				if mobs:
					for mob in mobs[ :-3 ] or mobs: # only last 3 mobs
						for i in range( 5 ): # Retry 5 times
							monster_ID = int( mob[ "BID" ] )
							monster_X = int( mob[ "X" ] )
							monster_Y = int( mob[ "Y" ] )
							print "MONSTER ID", monster_ID
							self.setDestination( monster_X, monster_Y, 2 )
							time.sleep( 1 )
							self.attack( monster_ID, 7 ) # 7 to keep attacking, 0 for one attack
							self.setDestination( monster_X - randint( 0, 2 ), monster_Y - randint( 0, 2 ), 2 )
							self.attack( monster_ID, 7 )
							time.sleep( 1 )
							self.setDestination( monster_X + randint( 0, 2 ), monster_Y + randint( 0, 2 ), 2 )
							self.attack( monster_ID, 7 )
							time.sleep( 1 )
							self.setDestination( monster_X - randint( 0, 2 ), monster_Y + randint( 0, 2 ), 2 )
							self.attack( monster_ID, 7 )
							time.sleep( 1 )
							self.setDestination( monster_X + randint( 0, 2 ), monster_Y - randint( 0, 2 ), 2 )
							self.attack( monster_ID, 7 )
							time.sleep( 1 )
					else:
						self.say( "There are no monsters of this type near me. " )
				if mob:
					return True
				self.say( "There are no monsters of this type near me. Giving up." )
				return False
			except Exception as e:
				print e
				return False
	
	
	def actionDone( self, action ):
		''' Test if action was successful '''
		if action[ 0 ] == 'randomWalk':
			return True
		elif action[ 0 ] == 'answerNPC':
			return True # there are no visible outcomes of this action
		elif action[ 0 ] == 'stopTalkingToNPC' or action[ 0 ] == 'stopTalkingToNPCSorfina':
			return True # there are no visible outcomes of this action
		elif action[ 0 ] == 'talkToNPC':
			return True # there are no visible outcomes of this action
		elif action[ 0 ] == 'equipItem':
			return True # TODO: Proove this
		elif action[ 0 ] == 'goToLocation':
			time.sleep( 2 )
			self.getMyLocation()
			return self.location == tuple( action[ 1 ] ) # returns True if the agent has arrived
		elif action[ 0 ] == 'tryToGoToLocation':
			time.sleep( 1 )
			return True # This is just a try to get the next NPC message
		elif action[ 0 ] == 'goToNPC':
			time.sleep( 2 )
			self.getMyLocation()
			print 'My location', self.location
			print 'My destination', tuple( action[ 1 ][ 1: ] )
			return self.location == tuple( action[ 1 ][ 1: ] ) # returns True if the agent has arrived
		if action[ 0 ] == 'killMob':
			time.sleep( 1 ) # TODO: Proove this
			return True
		return False # Unknown action

	def actionFailed( self ):
		''' Tell the knowledge base that an action was unsuccessful '''
		query = 'action_failed'
		self.kb.ask( query )

	def planDone( self, quest ):
		''' Test if a quest has been finished '''
		if quest == 'random_walk':
			return True
		query = "solved_quest( '%s' ), X = 1" % quest # Little hack to test SWI's state of mind ...
		time.sleep( 1 )
		result = self.kb.ask( query )
		try:
			#print '!!!!!', result[ 'X' ]
			if result[ 'X' ] == 1:
				return True
		except:
			return False

	def reconsider( self ):
		''' Is it time to reconsider my plans? '''
		probability = 1.0 # for now never
		reconsider = random() > probability
		return reconsider

	class Reason( spade.Behaviour.Behaviour ):
		def _process( self ):
			while not self.myAgent.login_complete:
				self.myAgent.login()
				self.myAgent.loggedin = False
				while not self.myAgent.loggedin:
					try:
						self.myAgent.quit()
					except:
						pass
					self.myAgent.loggedin = self.myAgent.login()
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
					continue

				self.myAgent.login_complete = True

			# Move the agent to get the first quest
			# TODO: Remove this later when we setup
			# saving and loading of agent's state
			
			'''self.myAgent.setDestination( 23, 24, 2 )
			time.sleep( 1 )		
			self.myAgent.answerToNPC( 110008658, 1 )
			time.sleep( 1 )
			self.myAgent.setDestination( 27, 27, 2 )
			time.sleep( 2 )
			self.myAgent.answerToNPC( 110008654, 1 )
			time.sleep( 1 )
			self.myAgent.answerToNPC( 110008654, 1 )
			time.sleep( 1 )
			self.myAgent.answerToNPC( 110008654, 1 )
			time.sleep( 1 )
			self.myAgent.setDestination( 33, 27, 2 )
			time.sleep( 2 )
			self.myAgent.setDestination( 44, 30, 2 )
			time.sleep( 2 )
			self.myAgent.closeCommunication( 110008655 )
			time.sleep( 1 )
			self.myAgent.setDestination( 29, 24, 2 )
			time.sleep( 3 )
			self.myAgent.talkToNPC( 110008656 )
			time.sleep( 2 )
			self.myAgent.closeCommunication( 110008656 )
			time.sleep( 1 )
			self.myAgent.itemEquip( 2 )
			time.sleep( 1 )
			self.myAgent.itemEquip( 3 )
			time.sleep( 1 )
			self.myAgent.setDestination( 27, 27, 2 )
			time.sleep( 2 )
			self.myAgent.talkToNPC( 110008654 )
			time.sleep( 1 )
			self.myAgent.closeCommunication( 110008654 )
			time.sleep( 1 )
			self.myAgent.setDestination( 44, 31, 2 )
			time.sleep( 2 )'''

			self.myAgent.say( 'Updating my knowledge base ...' )
			self.myAgent.updateKB()

			self.myAgent.say( 'Updating my objectives ...' )
			obj = self.myAgent.updateObjectives()
			self.myAgent.say( 'Selecting an objective ...' )
			if obj and obj[ 0 ][ 'Name' ] != 'random_walk':
				next = self.myAgent.selectObjective( obj )
			else:
				next = 'random_walk'
			self.myAgent.say( 'Planning quest "%s" ...' % next )
			start = self.myAgent.planQuest( next )
			if not start:
				self.myAgent.say( 'Cannot plan or start quest ...' )
				return
			planDone = False
			while not planDone:
				nextAction = self.myAgent.getNextAction( next )
				if not nextAction:
					self.myAgent.say( "My plan didn't work out. I'll try something else." )
					break
				self.myAgent.say( 'My next action is "%s(%s)"' % ( nextAction[ 0 ], ','.join( nextAction[ 1 ] ) ) )
				result = self.myAgent.act( nextAction )
				self.myAgent.say( 'I made my move, let us see if this worked ...' )
				
				if not result:
					self.myAgent.say( 'Action failed miserably, need to rethink my options ...' )
					break

				retries = 3
				success = self.myAgent.actionDone( nextAction )
				self.myAgent.say( "Updating my knowledge base ..." )
				self.myAgent.updateKB()
				while not success or retries == 0:
					time.sleep( 1 )
					self.myAgent.say( "Updating my knowledge base ..." )
					self.myAgent.updateKB()
					self.myAgent.say( "Testing if action was successful ..." )
					try:
						success = self.myAgent.actionDone( nextAction )
					except Exception, e:
						print "ERROR:", e
					retries -= 1

				if not success:
					self.myAgent.say( 'The action was unsuccessful, need to rethink my options ...' )
					self.myAgent.actionFailed()
					break # action has been unsuccessful

				self.myAgent.say( 'The action was successfull!' )

				try:
					planDone = self.myAgent.planDone( next )
				except Exception as e:
					print 'ERROR: ', e

				if planDone:
					self.myAgent.say( 'I finished quest "%s"! Going for the next one ...' % next )
					break

				
				if self.myAgent.reconsider():
					self.myAgent.say( 'It seems to be time to reconsider my options ...' )
					self.myAgent.say( 'Updating my knowledge base ...' )
					self.myAgent.updateKB()
					self.myAgent.say( 'Updating my objectives ...' )
					obj = self.myAgent.updateObjectives()
					self.myAgent.say( 'Selecting an objective ...' )
					if obj and obj[ 0 ][ 'Name' ] != 'random_walk':
						newnext = self.myAgent.selectObjective( obj )
					else:
						newnext = 'random_walk'
					if newnext != next:
						self.myAgent.say( 'Planning quest "%s" ...' % next )
						start = self.myAgent.planQuest( next )
						if not start:
							self.myAgent.say( 'Cannot plan or start quest ...' )
							return	
				

	class ChangeRole(spade.Behaviour.OneShotBehaviour):
		"""Behaviour to change the Role of the Agent. The Agent will acquire behaviours of the needed Role."""
		def _process(self):
			pass
			
	def __init__( self, SERVER, PORT, USERNAME, PASSWORD, CHARACTER, *args, **kwargs ):
		spade.Agent.Agent.__init__( self, *args, **kwargs )
		lli.Connection.__init__( self, SERVER, PORT, USERNAME, PASSWORD, CHARACTER )
		lli.CHARACTER = self.name.split( '@' )[ 0 ]
		
		self.kb = KB()
		
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

		''' TODO: Uncomment this later when random_walk is fully implemented
		try:		
			self.say( 'Map knowledge base loading (this might take some time)!' )
			self.kb.ask( "['tmwmap.P']" )
			time.sleep( 27 )
			self.say( 'Map knowledge base loaded!' )
		except:
			self.say( 'Error while loading map knowledge base, aborting!' )
			import sys
			sys.exit()'''

	def _setup( self ):
		#login = self.Login()
		#self.addBehaviour( login )
		self.login_complete = False

		reason = self.Reason()
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
	
	
	args = parser.parse_args()

	# Delete all knowledge bases
	if args.clear:
		files = glob.glob( join( KBFOLDER, '*.pl' ) )
		for f in files:
			os.remove( f )
	
	if args.num and args.name:
		agent_list = []	
		for i in range( args.name, args.name + args.num ):
			a = ManaWorldPlayer( SERVER, PORT, 'mali_agent%d' % i, PASSWORD, CHARACTER, 'agent_%d@127.0.0.1' % i, 'tajna' )
			a.start()
			time.sleep( args.interval )
			agent_list.append( a )
	elif args.name:
		a = ManaWorldPlayer( SERVER, PORT, 'mali_agent%d' % args.name, PASSWORD, CHARACTER, 'mali_agent%d@127.0.0.1' % args.name, 'tajna' )
		a.start()

	else:
		print 'Invalid number of arguments. Type "hlinterface.py --help" for details.'
	
